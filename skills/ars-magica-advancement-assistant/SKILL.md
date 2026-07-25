---
name: ars-magica-advancement-assistant
description: Plan and adjudicate Ars Magica seasons, advancement, study, teaching, practice, exposure, wounds, recovery, aging, and warping with cited rules and explicit uncertain inputs. Use for character progression, seasonal schedules, long-term consequences, and advancement calculations.
---

# Ars Magica Advancement Assistant

Use this skill for character change over time. Depend on
`ars-magica-corpus-navigator` for every rule-bearing conclusion and citation.
Treat laboratory activities as a handoff to `ars-magica-spell-lab-assistant`.

## Workflow

1. Identify the time horizon: one season, one year, or a multi-year plan.
2. Record the character state, activity, constraints, and desired outcome.
3. Separate declared values from unknown values. Ask for a missing value only if
   it changes the recommendation or calculation materially.
4. Use `ars-magica-corpus-navigator` to find the governing advancement,
   recovery, aging, or warping rules before calculating.
5. Calculate each season or event in order. Carry state changes forward only
   when the sources support that timing.
6. Present a timeline, arithmetic breakdown, consequences, choices, and
   citations.

## Required Inputs By Topic

| Topic | Capture before a definitive calculation |
| --- | --- |
| Study | source, Quality, subject, relevant modifiers, season count |
| Teaching or training | teacher, student, relevant scores, group size, activity details |
| Practice or exposure | actual activity, eligibility, source of experience, season count |
| Wounds and recovery | wound state, recovery conditions, care, relevant rolls or modifiers |
| Aging | age, timing, relevant modifiers, longevity or living conditions when applicable |
| Warping | source, frequency, duration, current state, resistance or protection where relevant |

If an input is unavailable, provide labeled scenarios such as `if Quality is
8` and `if Quality is 11`; do not fabricate a canonical value.

## Output Shape

```text
Goal and horizon:
Current state:
Season or event timeline:
Per-step calculation:
Consequences and decision points:
Open inputs and scenarios:
Sources:
```

## Boundaries

- Route spell invention, enchantment, vis extraction, and other laboratory
  activities to `ars-magica-spell-lab-assistant`.
- Use `ars-magica-rules-assistant` for a focused rules dispute within an
  advancement plan.
- Use `ars-magica-character-helper` when the task is initial character creation
  rather than later development.
- Use `ars-magica-software-builder` when the result must become a persistent
  model, validation rule, or deterministic application function.

## Guardrails

- Cite every rule-bearing calculation as `path:line_start-line_end`.
- Keep die-dependent results, Storyguide decisions, and missing facts visible.
- Distinguish advancement advice from the rules calculation supporting it.
- Do not collapse multiple possible activities into one assumed seasonal result.
