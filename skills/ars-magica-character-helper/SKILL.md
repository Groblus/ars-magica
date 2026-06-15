---
name: ars-magica-character-helper
description: Help create first-time Ars Magica Definitive Edition characters. Use when guiding magus, companion, or grog concepts; choosing House, role, Virtues, Flaws, Abilities, Arts, and starting spells; or producing a cited character creation checklist from the local Ars Magica corpus.
---

# Ars Magica Character Helper

Use this skill for character creation support. It depends on `ars-magica-corpus-navigator`; use that skill's search and citation rules for source lookup.

## Workflow

1. Start from concept: magus, companion, grog, or undecided.
2. For magi, ask for House preference only if the user has one; otherwise suggest 2-4 Houses by playstyle.
3. Use Definitive Edition core for baseline rules. Use 5e House books only for House-specific depth.
4. Search structured data before prose:
   - `docs/data/core-data.json` buckets: `virtues`, `flaws`, `abilities`, `spells`.
   - `skills/ars-magica-corpus-navigator/scripts/search.py "character creation"`.
5. Produce a checklist with unresolved choices, not a fake finished sheet unless the user asks for one.
6. Cite rules and options as `path:line_start-line_end`.

## Output Shape

- Concept summary
- Character type and likely role
- House or social role suggestions
- Virtues/Flaws shortlist with tradeoffs
- Ability and Art priorities
- Starting spell suggestions for magi
- Next decisions for the player

## Guardrails

- Keep first-time characters playable; avoid deep mystery, hedge, or edge-case subsystems unless requested.
- Mark 5e supplement material as compatible support.
- Do not use 3e/4e material.
