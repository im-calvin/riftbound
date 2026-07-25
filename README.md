# Riftbound Judge

A [Claude Code](https://claude.com/claude-code) subagent that answers **Riftbound TCG** rules questions like a certified judge. It cites its source on every answer, prefers the official rulebook, applies the latest errata and patch notes, looks things up live when unsure, and can be taught corrected rulings.

## Install

### 1. Install Claude Code
```bash
# macOS / Linux
curl -fsSL https://claude.com/install.sh | bash

# or with Homebrew
brew install --cask claude-code
```
Verify:
```bash
claude --version
```

### 2. Get this repo
```bash
git clone https://github.com/im-calvin/riftbound
cd riftbound
```

### 3. Launch Claude Code in the repo
```bash
claude
```
The `riftbound-judge` agent (`.claude/agents/riftbound-judge.md`) loads automatically because it lives in the project. **The agent registry is read at startup**, so if you add or edit an agent while Claude Code is running, restart it to pick up the change.

> Want the judge available in *every* project, not just this repo? Copy the agent into your global agents dir — but note it reads rules from this repo's `rules/` and `rulings/` folders, so keep it project-scoped unless you also relocate those:
> ```bash
> cp .claude/agents/riftbound-judge.md ~/.claude/agents/
> ```

## Use

Ask the judge anything about Riftbound rules, card interactions, timing, deck legality, or tournament procedure:

```
> Use the riftbound-judge agent: how many copies of a card can my Main Deck have?
```

Every answer comes back in a fixed format:

- **Ruling** — the direct answer
- **Reasoning** — the rule steps, with section numbers
- **Source(s)** — doc + section or URL, and which precedence tier
- **Confidence** — High (rulebook/errata/override) · Medium (verified community) · Low (unofficial — confirm with a head judge)

## How it decides (precedence, highest wins)

1. `rulings/overrides.md` — rulings **you** taught it (top authority)
2. `rules/errata/*` — card errata (overrides printed card text)
3. `rules/patch-notes/*` — rules changes, newest effective date wins
4. `rules/core-rules.md` · `rules/tournament-rules.md` — base engine
5. Live lookup — official pages → [Riftbound FAQ](https://www.riftboundfaq.com/) → [RiftJudge](https://app.riftjudge.com/) → Reddit (unofficial)

## Teach it a correct ruling

If the judge gets something wrong, tell it the correct ruling in a normal (edit-enabled) session. It appends a structured entry to `rulings/overrides.md` — the only file it can write to — and that ruling then wins over everything else. You can also edit that file by hand using the template at its top.

## Keep the rules current

Bundled rules are snapshots. When the [official Rules Hub](https://playriftbound.com/en-us/rules-hub/) shows a newer "Last updated" date than the snapshots, re-sync using the procedure in [`rules/SOURCES.md`](rules/SOURCES.md).

## Layout

```
.claude/agents/riftbound-judge.md   # the agent (system prompt + tools)
rules/
  SOURCES.md                        # every doc: URL, dates, re-sync steps
  pdf/                              # original PDFs (archival source of truth)
  core-rules.md  tournament-rules.md
  patch-notes/  errata/             # extracted snapshots
rulings/overrides.md                # taught corrections
CLAUDE.md                           # repo notes loaded by Claude Code
```
