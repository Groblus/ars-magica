---
name: ars-magica-spell-lab-assistant
description: Help with Ars Magica spell design, spell lookup, lab totals, seasonal laboratory activities, enchantments, vis use, and lab planning using Definitive Edition core and compatible 5e support.
---

# Ars Magica Spell And Lab Assistant

Use this skill for magic mechanics and seasonal lab planning. It depends on `ars-magica-corpus-navigator`.

## Workflow

1. Identify the task: lookup spell, design spell, invent spell, enchant item, extract vis, bind familiar, longevity ritual, or seasonal plan.
2. Search structured data first:
   - `docs/data/core-data.json` buckets: `spells`, `spell_guidelines`, `lab_activities`.
   - `python3 skills/ars-magica-corpus-navigator/scripts/search.py "laboratory total"`.
3. For spell design, determine Technique, Form, base guideline, Range, Duration, Target, requisites, ritual status, and final level.
4. For lab work, state the relevant Lab Total, threshold, seasonal progress, vis limit, and unresolved inputs.
5. Cite rules as `path:line_start-line_end`.

## Guardrails

- Do not overrule troupe judgment on ambiguous spell effects; flag judgment calls.
- Separate "rules calculation" from "suggested design".
- Treat 5e supplements as support, not authority over Definitive Edition core.
