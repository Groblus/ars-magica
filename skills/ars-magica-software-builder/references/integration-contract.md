# Integration Contract

Use these defaults unless the product has a justified incompatible constraint.

## Data Boundaries

| Boundary | Owns | Must contain |
| --- | --- | --- |
| Reference catalog | sourced definitions | stable ID, schema version, source references |
| Saga state | mutable campaign facts | stable ID, visibility, provenance, linked catalog IDs |
| Calculation request | declared inputs | input version, policy choices, optional seed |
| Calculation result | derived outcome | total, components, warnings, assumptions, source references |
| Render request | an artifact intent | template ID, theme, preset, audience, data version |
| Rendered artifact | immutable output | output hash, input hashes, renderer and asset versions |

## Stable IDs

Use lower-case, namespaced IDs such as `spell:pilum-of-fire`,
`person:marcus`, `saga:autumn-covenant`, and `source:core:casting-spells`.
Never use a display name as an identifier. Keep aliases separate. Do not
renumber published IDs.

## Rule Function Contract

Prefer pure functions with typed input and result objects:

```text
request + cited rule version + explicit policy -> result + audit trail
```

Put dice, random tables, and Storyguide choices in the request. Return a
machine-readable trace suitable for a player explanation and a test fixture.

## Adapter Contract

Keep shared application services independent of MCP, CLI, HTTP, UI, and print
adapters. Each adapter maps its transport request to the same validated service
request and maps the structured result to its output format.

## Interoperability

Version every external payload. Export stable IDs, display labels, source
provenance, visibility, and explicit unknowns. Treat VTT, JSON-LD, print, and
map formats as adapters; do not reshape the domain model around one consumer.

## Rendering

Render from validated data and a named template/preset. Preserve text, maps,
art, and source citations as separate inputs so a player-safe artifact can be
rendered from the same state without leaking Storyguide-only fields.
