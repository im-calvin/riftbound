#!/usr/bin/env python3
"""Query the bundled Riftbound card catalog (cards/cards.json).

Examples:
    python3 scripts/card.py ava              # name search (partial, case-insensitive)
    python3 scripts/card.py "loose cannon"   # multi-word name
    python3 scripts/card.py --code OGN-107   # search by card code
    python3 scripts/card.py --text hidden    # search rules text
    python3 scripts/card.py ava --json       # raw JSON for the matches
    python3 scripts/card.py jinx --set OGN   # filter matches to a set

Notes:
- Prints the printed catalog text AND flags when card errata exists for that
  card in rules/errata/* (errata overrides the printed text — go read it).
- Exit code 1 if nothing matched (handy in shell pipelines).
"""
import argparse
import glob
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_PATH = os.path.join(REPO_ROOT, "cards", "cards.json")
ERRATA_GLOB = os.path.join(REPO_ROOT, "rules", "errata", "*.md")


def load_cards():
    if not os.path.exists(CARDS_PATH):
        sys.exit("cards/cards.json not found — run: python3 scripts/sync_cards.py")
    with open(CARDS_PATH, encoding="utf-8") as f:
        return json.load(f)["cards"]


def errata_names():
    """Card headings (### Name) found across the errata files, lowercased."""
    names = set()
    for path in glob.glob(ERRATA_GLOB):
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^###\s+(.+?)\s*$", line)
                if m and m.group(1).upper() not in ("NEW TEXT", "OLD TEXT", "RELATED ARTICLES"):
                    names.add((m.group(1).strip().lower(), os.path.basename(path)))
    return names


def match(cards, args):
    q = " ".join(args.query).strip().lower()
    out = []
    for c in cards:
        name = (c.get("name") or "").lower()
        code = (c.get("code") or "").lower()
        text = (c.get("text") or "").lower()
        if args.code and args.code.lower() not in code:
            continue
        if args.text and args.text.lower() not in text:
            continue
        if q and q not in name:
            continue
        if args.set and (c.get("set_id") or "").lower() != args.set.lower():
            continue
        out.append(c)
    return out


def fmt(c, erra):
    lines = []
    head = c.get("name") or "(unnamed)"
    meta = []
    for k in ("type", "energy", "might", "set", "code", "rarity"):
        v = c.get(k)
        if v not in (None, "", []):
            meta.append(("%s %s" % ({"energy": "⚡", "might": "⚔"}.get(k, ""), v)).strip())
    lines.append("=== %s ===" % head)
    if meta:
        lines.append("  " + " · ".join(meta))
    if c.get("domains"):
        lines.append("  domains: " + ", ".join(c["domains"]))
    if c.get("tags"):
        lines.append("  tags: " + ", ".join(c["tags"]))
    if c.get("text"):
        lines.append("  text: " + c["text"].replace("\n", "\n        "))
    if c.get("image_url"):
        lines.append("  image: " + c["image_url"])
    hit = next((fn for (nm, fn) in erra if nm == (c.get("name") or "").lower()), None)
    if hit:
        lines.append("  ⚠ ERRATA EXISTS in rules/errata/%s — that NEW TEXT overrides the printed text above." % hit)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Query the Riftbound card catalog.")
    ap.add_argument("query", nargs="*", help="name search (partial, case-insensitive)")
    ap.add_argument("--code", help="filter/search by card code, e.g. OGN-107")
    ap.add_argument("--text", help="search within rules text")
    ap.add_argument("--set", help="filter to a set id, e.g. OGN / UNL / VEN")
    ap.add_argument("--json", action="store_true", help="print raw JSON for matches")
    ap.add_argument("--limit", type=int, default=20, help="max matches to show (default 20)")
    args = ap.parse_args()

    if not (args.query or args.code or args.text):
        ap.error("give a name to search, or use --code / --text")

    cards = load_cards()
    hits = match(cards, args)
    if not hits:
        print("No cards matched.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(hits[: args.limit], ensure_ascii=False, indent=1))
        return

    erra = errata_names()
    shown = hits[: args.limit]
    print("\n\n".join(fmt(c, erra) for c in shown))
    if len(hits) > len(shown):
        print("\n... %d more matches (raise --limit or narrow the query)." % (len(hits) - len(shown)))


if __name__ == "__main__":
    main()
