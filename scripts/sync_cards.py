#!/usr/bin/env python3
"""Re-sync the bundled Riftbound card catalog.

Pulls the official card gallery data (the same data behind Piltover Archive and
the Riftbound card gallery) and writes a compact judge-oriented snapshot to
`cards/cards.json`. Run from the repo root:

    python3 scripts/sync_cards.py

Source: the card gallery's Next.js data endpoint on the official site. We first
scrape the current `buildId` from the gallery HTML, then fetch the JSON:

    https://riftbound.leagueoflegends.com/en-us/card-gallery/
    https://riftbound.leagueoflegends.com/_next/data/<buildId>/en-us/card-gallery.json

NOTE: Riot also offers a first-party developer API (card art, rulesets) at
https://developer.riotgames.com/docs/riftbound, but it is gated behind app
approval + an API key. This public endpoint needs no key and returns the same
official card data. If you get a developer key, prefer the first-party API and
update this script.

Errata still overrides printed card text — the judge applies `rules/errata/*`
on top of whatever this catalog says. See CLAUDE.md precedence order.
"""
import html as htmlmod
import json
import os
import re
import urllib.request

SNAPSHOT_DATE = "2026-07-25"  # bump when you re-sync

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://riftbound.leagueoflegends.com"
GALLERY_PATH = "/en-us/card-gallery/"
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")


def get_build_id():
    m = re.search(r'"buildId":"([^"]+)"', fetch(BASE + GALLERY_PATH))
    if not m:
        raise RuntimeError("could not find buildId in card-gallery HTML")
    return m.group(1)


def html_to_plaintext(h):
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|li)>", "\n", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = htmlmod.unescape(h)
    h = re.sub(r"[ \t]+", " ", h)
    return re.sub(r"\n{2,}", "\n", h).strip()


def label(node, *path):
    """Walk nested {'value': {...'label':X}} shapes safely."""
    cur = node
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def simplify(card):
    ctype = None
    ct = card.get("cardType")
    if isinstance(ct, dict) and ct.get("type"):
        ctype = ct["type"][0].get("label")

    text_html = label(card, "text", "richText", "body") or ""
    tags = card.get("tags", {}).get("tags") if isinstance(card.get("tags"), dict) else None
    domains = None
    dom = card.get("domain")
    if isinstance(dom, dict) and dom.get("values"):
        domains = [d.get("label") for d in dom["values"]]

    return {
        "name": card.get("name"),
        "code": card.get("publicCode"),
        "collector_number": card.get("collectorNumber"),
        "set": label(card, "set", "value", "label"),
        "set_id": label(card, "set", "value", "id"),
        "type": ctype,
        "rarity": label(card, "rarity", "value", "label"),
        "energy": label(card, "energy", "value", "label"),
        "might": label(card, "might", "value", "label"),
        "domains": domains,
        "tags": tags,
        "text": html_to_plaintext(text_html) if text_html else "",
        "image_url": label(card, "cardImage", "url"),
    }


def main():
    build_id = get_build_id()
    print("buildId =", build_id)
    url = "%s/_next/data/%s/en-us/card-gallery.json" % (BASE, build_id)
    data = json.loads(fetch(url))
    items = data["pageProps"]["page"]["blades"][2]["cards"]["items"]
    cards = [simplify(c) for c in items if c.get("name")]
    cards.sort(key=lambda c: (c["set_id"] or "", c["collector_number"] or 0))

    out_dir = os.path.join(REPO_ROOT, "cards")
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        "source": url,
        "snapshot_date": SNAPSHOT_DATE,
        "count": len(cards),
        "cards": cards,
    }
    out_path = os.path.join(out_dir, "cards.json")
    with open(out_path, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("wrote cards/cards.json  (%d cards)" % len(cards))
    print("Update snapshot dates in rules/SOURCES.md (and SNAPSHOT_DATE here).")


if __name__ == "__main__":
    main()
