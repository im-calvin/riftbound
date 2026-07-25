# Taught Rulings (Overrides)

**This file is the highest authority.** The riftbound-judge agent reads it first on every question and treats a matching entry as final — above errata, patch notes, and the core/tournament rulebooks.

Add an entry when a ruling here is corrected by a human authority (you, a head judge, an official clarification). The agent also appends here automatically when you correct it.

## Format
Copy this block per ruling:

```
### <short question or interaction>
- **Ruling:** <the correct answer>
- **Reason / source:** <why, and where it came from — head judge, official post URL, etc.>
- **Supersedes:** <what bundled rule/errata this overrides, or "none — clarification">
- **Taught:** <YYYY-MM-DD>
- **Taught by:** <who>
```

Keywords: put searchable card names and rule terms in the heading so `grep` finds it.

---

## Rulings

### EXAMPLE — remove or edit this entry
- **Ruling:** This is a template example, not a real ruling. Delete it.
- **Reason / source:** Shows the expected format so the agent and future edits stay consistent.
- **Supersedes:** none — example
- **Taught:** 2026-07-25
- **Taught by:** setup
