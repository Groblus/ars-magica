---
name: ars-magica
description: Route broad Ars Magica requests for players, Storyguides, and software builders to the right focused workflow. Use for general questions, mixed tasks, or when the user does not know whether they need character help, rules adjudication, advancement, spell/lab planning, covenant design, saga preparation, or software design.
---

# Ars Magica

Use this skill as the front door. Identify the user's goal, select the smallest
set of focused skills, and preserve a single coherent answer. Do not duplicate
specialist workflows.

## Routing

| Request | Route |
| --- | --- |
| Find, verify, or cite source material | `ars-magica-corpus-navigator` |
| Create or revise a magus, companion, or grog | `ars-magica-character-helper` |
| Adjudicate a rule, calculate a total, or explain a formula | `ars-magica-rules-assistant` |
| Plan study, training, practice, exposure, recovery, aging, or warping | `ars-magica-advancement-assistant` |
| Design a spell, enchantment, or laboratory activity | `ars-magica-spell-lab-assistant` |
| Build a covenant, its resources, or its pressures | `ars-magica-covenant-builder` |
| Prepare sessions, scenes, NPCs, factions, or player handouts | `ars-magica-storyguide-prep` |
| Design or generate printable sheets, cards, props, or packets | `ars-magica-publication-designer` |
| Design schemas, rules functions, MCP/CLI surfaces, or integrations | `ars-magica-software-builder` |

## Workflow

1. Classify the request by desired outcome, not by the words it happens to use.
2. Ask only for an input that materially changes the outcome.
3. For a mixed request, name a lead skill and invoke supporting skills in dependency order.
4. Invoke `ars-magica-corpus-navigator` before any rule-bearing conclusion. Use
   the focused skill's citation workflow rather than answering from memory.
5. Keep player-visible material separate from Storyguide-only material when the
   request includes both.
6. State assumptions, unresolved decisions, and the next useful action.

## Common Combinations

- Character plus rules question: lead with `ars-magica-character-helper`; use
  `ars-magica-rules-assistant` for the disputed choice or calculation.
- Seasonal plan involving laboratory work: lead with
  `ars-magica-spell-lab-assistant`; use `ars-magica-advancement-assistant` for
  non-laboratory advancement, recovery, aging, or warping.
- Saga material with a rules consequence: lead with `ars-magica-storyguide-prep`;
  use `ars-magica-rules-assistant` for cited mechanics.
- Printable material: lead with `ars-magica-publication-designer`; use the
  relevant character, covenant, spell/lab, or Storyguide skill for content.
- Application feature: lead with `ars-magica-software-builder`; use
  `ars-magica-rules-assistant` to establish the cited rule behavior first.

## Guardrails

- Do not make a rule ruling, calculation, or implementation claim without the
  corpus navigator's source discipline.
- Do not turn an ordinary question into an edition discussion.
- Do not expose Storyguide secrets in a player-facing result.
- Prefer a focused skill over a broad lore dump.
