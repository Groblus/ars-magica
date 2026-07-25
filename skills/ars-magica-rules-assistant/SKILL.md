---
name: ars-magica-rules-assistant
description: Adjudicate sourced Ars Magica rules, formulas, calculations, and implementation-oriented mechanics. Use for casting, combat, spell effects, Virtues, Flaws, Abilities, Arts, totals, edge cases, rules comparisons, or translating cited mechanics into software behavior.
---

# Ars Magica Rules Assistant

Use this skill for rule-bearing questions. Depend on
`ars-magica-corpus-navigator` for every rule lookup and citation; do not treat
memory, extracted fields, or a calculation as authority.

## Workflow

1. State the question as a decision, formula, or disputed interaction.
2. List the facts supplied by the user and the facts that remain unknown.
3. Use `ars-magica-corpus-navigator` to locate the governing rule and any
   exception before interpreting it. Read the cited source span, not only a
   search snippet.
4. Separate explicit text, direct calculation, and troupe judgment.
5. Calculate from named inputs. Show every modifier, intermediate value, cap,
   threshold, and rounding rule that affects the result.
6. Give the result, operational consequence, unresolved inputs, and citations.

## Calculation Output

Use this shape when arithmetic matters:

```text
Question:
Known inputs:
Formula:
Breakdown:
Result:
Rules notes:
Uncertain inputs or troupe rulings:
Sources:
```

Keep alternatives as separate scenarios. Never choose a favorable value for an
unsupplied characteristic, score, modifier, die result, environmental fact, or
Storyguide ruling.

## Adjudication

- Prefer the narrowest applicable rule, then read its surrounding section.
- Reconcile apparent conflicts by scope, timing, definitions, and explicit
  exceptions. Cite each rule involved.
- Say when the sources leave room for troupe judgment. Offer bounded options,
  not invented certainty.
- Distinguish a legal reading from a balance or story recommendation.
- Route spell design, enchantments, and laboratory activity to
  `ars-magica-spell-lab-assistant` unless the user only needs a discrete rule
  ruling or formula.
- Route ongoing study, training, recovery, aging, and warping to
  `ars-magica-advancement-assistant`.

## Software Explanations

When the user is implementing a rule:

1. Establish the cited behavior first.
2. Express the rule as a pure input/output contract.
3. Preserve uncertainty as an explicit input, enum, warning, or policy hook.
4. Return an auditable breakdown with source references, rather than a bare
   scalar.
5. Route durable schemas, APIs, MCP tools, CLI design, rendering, and
   interoperability to `ars-magica-software-builder`.

## Guardrails

- Cite every rule-bearing conclusion as `path:line_start-line_end`.
- Do not silently substitute a house rule, inferred intention, or example for
  governing text.
- Do not invent mechanics to make a requested result possible.
