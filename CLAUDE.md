# Riftbound Judge

A Claude Code subagent that answers Riftbound TCG rules questions like a certified judge: it always cites its source, prefers the official rulebook, applies the latest errata and patch notes, looks things up live when unsure, and can be taught corrected rulings.

The agent lives in `.claude/agents/riftbound-judge.md`. Invoke it with the Agent tool for any Riftbound rules, interaction, deck-legality, or tournament-procedure question.

## Source-of-truth precedence (highest wins)
1. `rulings/overrides.md` — human-taught corrections. **Top authority.**
2. `rules/errata/*` — card-specific errata (overrides base card text).
3. `rules/patch-notes/*` — rules changes; newest effective date wins.
4. `rules/core-rules.md` and `rules/tournament-rules.md` — base engine. (For competitions, tournament rules 104.1 says tournament rules beat core rules.)
5. Live lookup — official pages → Riftbound FAQ (riftboundfaq.com, preferred community source) → RiftJudge (prefer "Human verified") → Reddit (unofficial, flag it).

## Layout
```
.claude/agents/riftbound-judge.md   # the agent
rules/
  SOURCES.md                        # every doc: URL, official date, snapshot date, re-sync steps
  pdf/                              # original PDFs (archival source of truth)
  core-rules.md  tournament-rules.md
  patch-notes/  errata/             # extracted snapshots
rulings/overrides.md                # taught corrections (agent reads first, writes here)
```

## Teaching it a correct ruling
Tell the agent the correct ruling in a normal (edit-enabled) session; it appends a structured entry to `rulings/overrides.md`. Or edit that file yourself using the template at its top.

## Keeping rules current
See the re-sync procedure in `rules/SOURCES.md`. Re-fetch when the Rules Hub shows a newer "Last updated" than the snapshot dates.
