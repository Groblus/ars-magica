---
name: ars-magica-software-builder
description: Design Ars Magica software with stable schemas, source provenance, pure rules functions, MCP or CLI integration, rendering contracts, and interoperable exports. Use when building applications, APIs, data models, validators, tools, print outputs, VTT integrations, or rules-engine features.
---

# Ars Magica Software Builder

Use this skill to turn game concepts into maintainable software contracts. For
rule behavior, invoke `ars-magica-corpus-navigator` and
`ars-magica-rules-assistant` before designing the implementation.

Read [references/integration-contract.md](references/integration-contract.md)
when defining data, function, integration, rendering, or interoperability
contracts.

## Workflow

1. Identify the user outcome, consumers, and authority boundary.
2. Establish cited rule behavior before encoding any rule-bearing logic.
3. Separate immutable reference catalog data from mutable saga and character
   state.
4. Define stable IDs, validation, provenance, visibility, and versioning before
   storage or UI design.
5. Design calculations as pure functions with explicit inputs and structured,
   auditable outputs.
6. Expose the same application service through adapters such as MCP, CLI, web,
   print rendering, or VTT export. Keep adapters thin.
7. Specify error states, unknown inputs, migration behavior, and test examples.

## Design Rules

- Reference catalog records must retain source citations and never make copied
  prose the only machine-readable authority.
- Saga state must reference catalog IDs instead of duplicating rules content.
- Treat player, Storyguide, and public visibility as data access, not display
  styling.
- Return calculation components, warnings, assumptions, and source references
  with every rules result.
- Make randomness injectable or seedable; persist the resolved result and its
  trace.
- Make output artifacts reproducible from versioned input, template, asset, and
  renderer identifiers.

## Existing Integration Surface

The local FastMCP server in `mcp/ars_magica_server.py` already exposes corpus
search and structured lookups. Preserve its cited-reference role; add future
rules and rendering tools as thin adapters over shared application functions,
not as duplicated business logic.

## Handoffs

- Use `ars-magica-rules-assistant` for cited formulas, edge cases, and
  implementation semantics.
- Use `ars-magica-advancement-assistant` for progression behavior.
- Use `ars-magica-spell-lab-assistant` for magic and laboratory domain rules.
- Use `ars-magica-corpus-navigator` whenever a design decision depends on rule
  text.
- Use `ars-magica-storyguide-prep` for the play-facing content a feature must
  support.

## Guardrails

- Do not encode uncited rules from memory.
- Do not let an LLM response become the sole calculation or validation layer.
- Do not couple rendering or transport code directly to storage schema.
- Do not hide uncertainty, source gaps, or troupe-policy choices in defaults.
