#!/usr/bin/env python3
"""Re-sync the bundled Riftbound rules snapshots.

Downloads the Core + Tournament Rules PDFs and the patch-note / errata pages,
then extracts each to markdown under rules/. Run from the repo root:

    python3 scripts/sync_rules.py

Requires `pypdf` (auto-checked). Update snapshot dates in rules/SOURCES.md after
running, and bump SNAPSHOT_DATE below.

Source of truth for URLs: rules/SOURCES.md.
"""
import html as htmlmod
import json
import os
import re
import subprocess
import sys
import urllib.request

SNAPSHOT_DATE = "2026-07-25"  # bump when you re-sync

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (local pdf name, markdown out, title, official "last updated", url)
PDFS = [
    ("core-rules.pdf", "core-rules.md", "Core Rules", "2026-07-16",
     "https://cmsassets.rgpub.io/sanity/files/dsfx7636/news_live/e9ac8e3d33e0f78cef296f5945aba7bc1313b086.pdf"),
    ("tournament-rules.pdf", "tournament-rules.md", "Tournament Rules", "2026-07-16",
     "https://cmsassets.rgpub.io/sanity/files/dsfx7636/news_live/503da65669ced10598d62925a6f6bc15111af726.pdf"),
]

# (subdir, out filename, title, url)
PAGES = [
    ("patch-notes", "core.md", "Core Rules Patch Notes",
     "https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-core-rules-patch-notes/"),
    ("patch-notes", "spiritforged.md", "Spiritforged Patch Notes",
     "https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-core-rules-spiritforged-patch-notes/"),
    ("patch-notes", "unleashed.md", "Unleashed Patch Notes",
     "https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-core-rules-unleashed-patch-notes/"),
    ("patch-notes", "vendetta.md", "Vendetta Patch Notes",
     "https://playriftbound.com/en-us/news/announcements/core-rules-vendetta-patch-notes"),
    ("errata", "origins.md", "Origins Card Errata",
     "https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-origins-card-errata/"),
    ("errata", "spiritforged.md", "Spiritforged Errata",
     "https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-spiritforged-errata/"),
    ("errata", "unleashed.md", "Unleashed Errata",
     "https://playriftbound.com/en-us/news/rules-and-releases/unleashed-errata-updates/"),
    ("errata", "vendetta.md", "Vendetta Errata",
     "https://playriftbound.com/en-us/news/announcements/vendetta-errata-updates"),
]

LIGATURES = [("ﬁ", "fi"), ("ﬂ", "fl"), ("ﬀ", "ff"),
             ("ﬃ", "ffi"), ("ﬄ", "ffl"),
             ("’", "'"), ("“", '"'), ("”", '"'),
             ("–", "-"), ("—", "-")]


def ensure_pypdf():
    try:
        import pypdf  # noqa: F401
    except ImportError:
        print("Installing pypdf ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pypdf"])


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=60).read()
    return data if binary else data.decode("utf-8", "replace")


def extract_pdf(pdf_path):
    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    parts = []
    for i, page in enumerate(reader.pages):
        parts.append("\n\n===== PAGE %d =====\n%s" % (i + 1, page.extract_text() or ""))
    return len(reader.pages), "".join(parts)


def clean_pdf_text(raw):
    for a, b in LIGATURES:
        raw = raw.replace(a, b)
    out = []
    for line in raw.split("\n"):
        if line.startswith("===== PAGE"):
            out.append("\n<!-- " + line.strip("= ").strip() + " -->")
            continue
        out.append(re.sub(r"  +", " ", line).rstrip())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def collect_bodies(node, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "body" and isinstance(v, str) and len(v) > 200:
                acc.append(v)
            elif k in ("title", "heading") and isinstance(v, str) and 0 < len(v) < 200:
                acc.append("\n\n## " + v)
            else:
                collect_bodies(v, acc)
    elif isinstance(node, list):
        for v in node:
            collect_bodies(v, acc)


def html_to_text(h):
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|li|h[1-6]|tr)>", "\n", h)
    h = re.sub(r"(?i)<li[^>]*>", "- ", h)
    h = re.sub(r"(?i)<(h[1-6])[^>]*>", "\n### ", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = htmlmod.unescape(h)
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r"\n[ \t]+", "\n", h)
    return re.sub(r"\n{3,}", "\n\n", h).strip()


# Heading-only lines injected by the site's nav/header — dropped from snapshots.
CHROME_HEADINGS = {
    "Create One", "Sign In", "Rules and Releases", "Announcements", "Riftbound",
}


def strip_web_chrome(text):
    """Remove nav/header/footer chrome from a scraped page body.

    Drops heading-only lines that are known site chrome, and truncates the
    trailing "Related Articles" footer nav block that every page carries.
    """
    # Cut the footer nav that starts at the Related Articles block.
    text = re.split(r"(?m)^#+\s*Related Articles\s*$", text)[0]
    out = []
    for line in text.split("\n"):
        m = re.match(r"^#+\s*(.+?)\s*$", line)
        if m and m.group(1) in CHROME_HEADINGS:
            continue
        out.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def extract_page_body(raw):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)
    if not m:
        return None
    data = json.loads(m.group(1))
    acc = []
    collect_bodies(data.get("props", {}).get("pageProps", {}), acc)
    if not acc:
        return None
    return strip_web_chrome("\n\n".join(html_to_text(x) for x in acc))


def sync_pdfs():
    pdf_dir = os.path.join(REPO_ROOT, "rules", "pdf")
    os.makedirs(pdf_dir, exist_ok=True)
    for pdf_name, md_name, title, updated, url in PDFS:
        pdf_path = os.path.join(pdf_dir, pdf_name)
        print("PDF  %s ..." % title)
        with open(pdf_path, "wb") as f:
            f.write(fetch(url, binary=True))
        n, raw = extract_pdf(pdf_path)
        body = clean_pdf_text(raw)
        header = (
            "# Riftbound %s (extracted)\n\n"
            "> Source: official %s PDF, Last Updated %s.\n"
            "> Extracted from `rules/pdf/%s`. Section numbers preserved from the original.\n\n"
            % (title, title, updated, pdf_name)
        )
        with open(os.path.join(REPO_ROOT, "rules", md_name), "w") as f:
            f.write(header + body)
        print("     -> rules/%s  (%d pages)" % (md_name, n))


def sync_pages():
    for sub, fn, title, url in PAGES:
        print("PAGE %s ..." % title)
        try:
            body = extract_page_body(fetch(url))
        except Exception as e:  # noqa: BLE001
            body = None
            print("     WARN fetch/parse failed: %s" % e)
        if not body:
            body = "(could not extract structured body — see source URL)"
        header = ("# Riftbound — %s\n\n> Source: %s\n> Fetched: %s (snapshot).\n\n"
                  % (title, url, SNAPSHOT_DATE))
        out_dir = os.path.join(REPO_ROOT, "rules", sub)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, fn), "w") as f:
            f.write(header + body + "\n")
        print("     -> rules/%s/%s" % (sub, fn))


def main():
    ensure_pypdf()
    sync_pdfs()
    sync_pages()
    print("\nDone. Update snapshot dates in rules/SOURCES.md (and SNAPSHOT_DATE here).")


if __name__ == "__main__":
    main()
