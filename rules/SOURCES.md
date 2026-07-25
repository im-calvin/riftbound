# Rules Sources

All bundled rules snapshots and where they came from. Re-fetch when the "Last updated" on the official [Rules Hub](https://playriftbound.com/en-us/rules-hub/) is newer than the snapshot date below.

| Doc | Local file | Official source | Last updated (official) | Snapshot date |
|-----|-----------|-----------------|------------------------|---------------|
| Core Rules | `core-rules.md` (+ `pdf/core-rules.pdf`) | https://cmsassets.rgpub.io/sanity/files/dsfx7636/news_live/e9ac8e3d33e0f78cef296f5945aba7bc1313b086.pdf | 2026-07-16 | 2026-07-25 |
| Tournament Rules | `tournament-rules.md` (+ `pdf/tournament-rules.pdf`) | https://cmsassets.rgpub.io/sanity/files/dsfx7636/news_live/503da65669ced10598d62925a6f6bc15111af726.pdf | 2026-07-16 | 2026-07-25 |
| Core Patch Notes | `patch-notes/core.md` | https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-core-rules-patch-notes/ | — | 2026-07-25 |
| Spiritforged Patch Notes | `patch-notes/spiritforged.md` | https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-core-rules-spiritforged-patch-notes/ | — | 2026-07-25 |
| Unleashed Patch Notes | `patch-notes/unleashed.md` | https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-core-rules-unleashed-patch-notes/ | — | 2026-07-25 |
| Vendetta Patch Notes | `patch-notes/vendetta.md` | https://playriftbound.com/en-us/news/announcements/core-rules-vendetta-patch-notes | effective 2026-07-24 | 2026-07-25 |
| Origins Errata | `errata/origins.md` | https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-origins-card-errata/ | — | 2026-07-25 |
| Spiritforged Errata | `errata/spiritforged.md` | https://riftbound.leagueoflegends.com/en-us/news/rules-and-releases/riftbound-spiritforged-errata/ | — | 2026-07-25 |
| Unleashed Errata | `errata/unleashed.md` | https://playriftbound.com/en-us/news/rules-and-releases/unleashed-errata-updates/ | — | 2026-07-25 |
| Vendetta Errata | `errata/vendetta.md` | https://playriftbound.com/en-us/news/announcements/vendetta-errata-updates | — | 2026-07-25 |

## Card catalog

Card data (names, text, type, energy, might, domains, tags, image URLs) is bundled at `cards/cards.json` and refreshed by `scripts/sync_cards.py`.

| Source | Access | Notes |
|--------|--------|-------|
| Official card gallery data | `https://riftbound.leagueoflegends.com/_next/data/<buildId>/en-us/card-gallery.json` | Public, no key. `<buildId>` is scraped from `https://riftbound.leagueoflegends.com/en-us/card-gallery/`. This is the data behind [Piltover Archive](https://piltoverarchive.com/). Used by `sync_cards.py`. ~1,180 cards. |
| Riot first-party developer API | `https://developer.riotgames.com/docs/riftbound` | **Gated** — requires app approval + API key (and RSO for gameplay apps). Serves card art, rulesets, and assets. Preferred upgrade path once you have a key; endpoints are not public until approved. |
| Community card search | https://www.riftbound.one/ · https://www.rift.tools/ | Fast rules-text / multi-filter card search. Community, unofficial. |

Card errata (`rules/errata/*`) overrides the printed text in `cards/cards.json` — apply it on top per the precedence order in `CLAUDE.md`.

## Live lookup sources (not bundled — fetched at answer time), highest trust first
- **Official news / rules hub** — https://playriftbound.com/en-us/rules-hub/ — authoritative for anything newer than the snapshots above.
- **Riftbound FAQ** — https://www.riftboundfaq.com/ — community FAQ built with input from experienced judges, cross-referenced to the official CRD. Preferred community source (above RiftJudge).
- **RiftJudge** — https://app.riftjudge.com/ — community Q&A DB (10k+). Prefer entries marked "Human verified".
- **Reddit** — r/Riftbound and similar. Lowest trust; use only when the above are silent, and flag the answer as unofficial.

## Re-sync procedure
1. Download the two PDFs into `rules/pdf/`.
2. Extract to markdown with `pypdf` (preserve section numbers; fix ligatures fi/fl; collapse double spaces).
3. Re-fetch the 8 patch-note/errata pages (content lives in each page's `__NEXT_DATA__` JSON, key `body`).
4. Update the snapshot dates in this table.
