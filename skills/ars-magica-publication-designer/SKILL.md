---
name: ars-magica-publication-designer
description: "Use when designing or generating Ars Magica printable materials: character sheets, spell cards, NPC cards, props, handouts, maps, session packets, locale storyboards, portrait sheets, or print-ready material specs."
---

# Ars Magica Publication Designer

Use this skill to turn saga content into attractive, printable, citation-aware materials for players and storyguides. The renderer accepts compact material mappings and `ars_magica.models.ArtifactSpec` instances directly. Always set the intended audience: the renderer recursively removes Storyguide-only mappings and secret/Storyguide-named fields before a template, manifest, attribution file, or package receives data.

## Workflow

1. Identify the artifact type: character sheet, companion/grog sheet, spell deck, NPC card, storyguide packet, prop, map/locale board, portrait sheet, or custom packet.
2. Choose the closest publishing template with `ars-magica templates list` or MCP `list_publishing_templates`.
3. Inspect the required content contract with `ars-magica templates inspect <template>` or MCP `inspect_publishing_template`.
4. Build a material spec with `template`, `theme`, `preset`, `content`, `assets`, `audience`, and `source_references`.
5. Keep rules/source text and generated media separate: rules in `content`, visual/audio/map references in `assets` with creator/license/source metadata.
6. Render with `ars-magica render-html spec.json -o material.html` or MCP `render_material_html`; package with `ars-magica package spec.json material.zip` or MCP `package_material_zip`.

## Defaults

- Rules authority: Definitive core first, 5th edition supplements only when useful and cited.
- Player-facing output: hide storyguide secrets and use `audience: player`.
- Storyguide output: include secrets, NPC motives, clocks, scene beats, and unresolved adjudication notes.
- Home printing: use `home-letter` or `home-a4`.
- Table cards: use `poker-cards`.
- Accessible review: use `screen-accessible`.
- Low-ink handouts: use `ink-economy` theme with `photocopy-monochrome` preset.

## Material spec shape

```json
{
  "title": "Spring Covenant Packet",
  "template": "storyguide-session-packet",
  "theme": "laboratory-notebook",
  "preset": "home-letter",
  "audience": "storyguide",
  "content": {},
  "assets": [],
  "source_references": []
}
```

## Quality bar

- Prefer deliberate layout direction over generic parchment styling.
- Preserve citations in `source_references`; use `reviewed/Core.md:500-510` or a SourceReference-like mapping with `title` and `locator`/`citation`; do not bury them in decorative text.
- Record artwork, portraits, maps, music, and props as separate assets with rights metadata.
- If a template cannot express the requested artifact, produce a clear custom spec and note the missing template capability.

For PDF output on macOS, WeasyPrint 69 requires native Pango/GObject libraries in addition to the Python extra. Install them before diagnosing renderer errors.
