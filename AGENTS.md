# Ars Magica Open License Corpus - Agent Guide

This repository is a sparse checkout of the Ars Magica Open License Markdown corpus plus agentic tooling for citation-first lookup, deterministic mechanics, structured saga data, and printable materials.

## Repository Map

| Path | Purpose | Notes |
|---|---|---|
| `README.md` | Project overview | Install, CLI, MCP, skills, and rebuild commands. |
| `LICENSE.md` | License text | Open-license basis for the corpus. |
| `reviewed/` | Manually reviewed Markdown books | Trusted source corpus. Do not edit during tooling integration work. |
| `docs/` | GitHub Pages artifacts | Landing page, library browser, inventory report, first-session packet, and JSON exports. |
| `skills/` | Installable skills | Router, corpus navigator, focused play skills, software builder, and publication designer. |
| `src/ars_magica/models/` | Pydantic contracts | State, rules, covenant, saga, publishing, map, media, and rights models. |
| `schemas/v1/` | JSON Schema contracts | Portable schema equivalents for software integration. |
| `src/ars_magica/rules/` | Deterministic mechanics | Dice, casting, penetration, spell levels, lab totals, advancement, validation. |
| `src/ars_magica/publishing/` | Publishing runtime | Template discovery, HTML rendering, optional PDF, deterministic packages. |
| `press/` | Publishing resources | Templates, themes, tokens, presets, schemas, and styles. |
| `mcp/ars_magica_server.py` | Local MCP server | Corpus DB tools plus deterministic rules and publishing tools. |

## Authority Policy For Agents

Use `reviewed/Ars Magica - Definitive Edition (Core Rules).md` as the baseline rules authority.

Treat 5th Edition books as compatible supporting sources when relevant and cited.

Do not center answers around edition comparison unless the user explicitly asks. The normal operating mode is Definitive/5th-edition play and software support.

Treat 3rd and 4th Edition books as legacy inspiration only. Do not present their mechanics as current without explicit conversion.

## Current Architecture

The main `ars-magica` skill routes tasks. The corpus navigator is the retrieval/citation layer. Focused skills handle rules, advancement, software contracts, character/covenant/storyguide prep, spell/lab assistance, and printable materials.

The Python package uses a modern `src` layout. `ars_magica.__init__` stays lightweight so dependency-free rules helpers can be imported without loading Pydantic models. Domain models require the core Pydantic dependency declared in `pyproject.toml`.

The MCP server has three surfaces:

| Surface | Tools | Dependency behavior |
|---|---|---|
| Corpus database | Search, section retrieval, TOCs, spells, virtues, flaws, abilities, covenant options | Requires the local SQLite database. Missing/LFS-placeholder failures are localized to these calls. |
| Deterministic mechanics | Dice, casting, penetration, spell level, lab total | No corpus database required; results include citations. |
| Publishing | Template discovery, template inspection, HTML rendering, ZIP packaging | Discovery is dependency-light; rendering requires publishing extras such as Jinja2. |

## CLI

```bash
ars-magica dice simple --roll 0
ars-magica dice stress --rolls 1,1,5 --botch-dice 1
ars-magica templates list
ars-magica templates inspect magus-character-sheet
ars-magica render-html spec.json -o material.html
ars-magica package spec.json material.zip
```

## Printable Materials

Use `skills/ars-magica-publication-designer/` for character sheets, spell cards, NPC cards, props, maps, locale boards, scene packets, portraits, and other printable artifacts.

Material specs should keep generated media and rules text separate. Put rules-facing data in `content`, external or generated images/audio/maps in `assets`, and citations in `source_references`.

## Working Rules For Future Agents

Do not assume every Ars Magica sourcebook is present. Prefer heading-aware retrieval and precise citations over broad full-file reads.

When answering rules questions, cite the Definitive core first. Bring in compatible 5th Edition sourcebooks only as secondary support.

When building software outputs, use the Pydantic models and JSON Schemas as contracts. Definitions should remain separate from mutable saga state.

When building generated artifacts, preserve source citations as path plus line span wherever possible and record asset rights metadata.
