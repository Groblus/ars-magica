# Ars Magica Open License Corpus - Agent Guide

This repository is a sparse checkout of the Ars Magica Open License Markdown corpus. It is currently best treated as a curated `reviewed/` subset for reading, exploration, extraction, and agentic tooling.

## Repository Map

| Path | Purpose | Notes |
|---|---|---|
| `README.md` | Upstream project overview | Describes the full 53-book corpus and Markdown conversion workflow. |
| `LICENSE.md` | License text | Open-license basis for the corpus. |
| `arm5openlicenselogo.png` | Logo image | Useful for generated reports or local reading surfaces. |
| `reviewed/` | Manually reviewed Markdown books | 25 books in this sparse checkout; use these as the trusted source. |
| `ars-magica-inventory-report.html` | Human-readable inventory report | Generated exploratory report with tables, diagrams, and build ideas. |

The README mentions `raw-md/`, `wip/`, and `3rd-party/`, but those directories are not present in this sparse checkout.

## Corpus Summary

| Metric | Count |
|---|---:|
| Reviewed Markdown books | 25 |
| Definitive Edition core books | 1 |
| 5th Edition sourcebooks | 19 |
| 4th Edition legacy books | 3 |
| 3rd Edition legacy books | 2 |
| Reviewed Markdown lines | 153,227 |

## Edition Policy For Agents

Use `reviewed/Ars Magica - Definitive Edition (Core Rules).md` as the baseline rules authority.

Treat 5th Edition books as generally compatible with Definitive Edition unless a specific rule conflict is discovered.

Treat 3rd and 4th Edition books as legacy inspiration only. Their setting material can be useful, but mechanics, assumptions, and metaplot should not be treated as current without conversion.

## First-Time Play Priorities

| Priority | Books | Agent Use |
|---|---|---|
| P0 | `Ars Magica - Definitive Edition (Core Rules).md` | Start here for all rules, character creation, magic, combat, covenants, realms, stories, sagas, indexes, and reference tables. |
| P1 | `Ars Magica 5e - Covenants.md` | Use early for covenant creation, boons/hooks, labs, libraries, vis, covenfolk, governance, and saga infrastructure. |
| P1 | `Ars Magica 5e - Houses of Hermes - True Lineages.md` | Use for Bonisagus, Guernicus, Mercere, Tremere, the Code, Hermetic politics, and Order institutions. |
| P1 | `Ars Magica 5e - Houses of Hermes - Societates.md` | Use for Flambeau, Jerbiton, Tytalus, Ex Miscellanea, and many common player concepts. |
| P2 | `Ars Magica 5e - Houses of Hermes - Mystery Cults.md` | Use for Bjornaer, Criamon, Merinita, Verditius, and mystery-heavy characters. |
| P2 | `Ars Magica 5e - Realms of Power - Magic.md` | Use for auras, magical creatures, vis, magical beings, and Magic Realm depth. |
| P2 | `Ars Magica 5e - Lords of Men.md` | Use when nobles, knights, feudal obligations, warfare, or mundane power matter. |
| P2 | `Ars Magica 5e - The Church.md` | Use for the medieval Church as a major setting institution. |
| P3 | Other 5e realm, mundane, tribunal, mystery, hedge magic, apprentice, and location books | Use when the saga focus calls for them. |
| P4 | 3e/4e books and `Transforming Mythic Europe` | Use as legacy lore, advanced campaign material, or conversion targets. |

## Reviewed Books By Category

### Core

| Book | Status | Role |
|---|---|---|
| `reviewed/Ars Magica - Definitive Edition (Core Rules).md` | Definitive baseline | Core rules, indexes, reference guide, first reading anchor. |

### Covenant And Saga Toolkit

| Book | Status | Role |
|---|---|---|
| `reviewed/Ars Magica 5e - Covenants.md` | 5e compatible | Covenant design, boons/hooks, governance, wealth, libraries, labs, vis sources. |
| `reviewed/Ars Magica 5e - Magic - Apprentices.md` | 5e compatible | Young characters, apprenticeships, gauntlets, child-focused stories. |
| `reviewed/Ars Magica 5e - Magic - Hedge Magic (Revised).md` | 5e compatible | Non-Hermetic traditions, rivals, allies, integration stories. |
| `reviewed/Ars Magica 5e - The Mysteries (Revised).md` | 5e compatible | Mystery initiations, cults, alchemy, astrology, theurgy. |
| `reviewed/Ars Magica 5e - Mythic Locations.md` | 5e compatible | Drop-in adventure sites and story hooks. |
| `reviewed/Ars Magica 5e - Transforming Mythic Europe.md` | 5e compatible, advanced | Long-saga transformation projects; not first-time baseline. |

### Houses Of Hermes

| Book | Houses | Role |
|---|---|---|
| `reviewed/Ars Magica 5e - Houses of Hermes - True Lineages.md` | Bonisagus, Guernicus, Mercere, Tremere | High-value political and institutional support. |
| `reviewed/Ars Magica 5e - Houses of Hermes - Societates.md` | Flambeau, Jerbiton, Tytalus, Ex Miscellanea | High-value player concept support. |
| `reviewed/Ars Magica 5e - Houses of Hermes - Mystery Cults.md` | Bjornaer, Criamon, Merinita, Verditius | Higher-complexity mystery and house-specific support. |

### Realms Of Power

| Book | Realm | Role |
|---|---|---|
| `reviewed/Ars Magica 5e - Realms of Power - Magic.md` | Magic | Auras, creatures, vis, magical beings. |
| `reviewed/Ars Magica 5e - Realms of Power - Faerie.md` | Faerie | Faerie logic, Arcadia, faerie stories and beings. |
| `reviewed/Ars Magica 5e - Realms of Power - The Divine (Revised).md` | Divine | Miracles, holy characters, angels, Divine auras. |
| `reviewed/Ars Magica 5e - Realms of Power - The Infernal.md` | Infernal | Demons, corruption, sin, infernal antagonists. |

### Mythic Europe And Mundane Society

| Book | Role |
|---|---|
| `reviewed/Ars Magica 5e - Art & Academe.md` | Universities, medicine, philosophy, scholarship, art. |
| `reviewed/Ars Magica 5e - City & Guild.md` | Towns, trade, guilds, crafts, urban covenants. |
| `reviewed/Ars Magica 5e - Lords of Men.md` | Nobility, knights, warfare, feudal structures. |
| `reviewed/Ars Magica 5e - The Church.md` | Church institutions, clergy, monastic life, holy orders. |

### Tribunal And Regional Books

| Book | Edition | Status |
|---|---:|---|
| `reviewed/Ars Magica 5e - Guardians of the Forests - The Rhine Tribunal.md` | 5e | Current-use setting source for Rhine/Germany. |
| `reviewed/Ars Magica 5e - The Lion and the Lily - The Normandy Tribunal.md` | 5e | Current-use setting source for Normandy/northern France. |
| `reviewed/Ars Magica 4e - Heirs to Merlin - Stonehenge Tribunal.md` | 4e | Legacy England/Wales lore; convert mechanics. |
| `reviewed/Ars Magica 4e - Sanctuary of Ice - The Greater Alps Tribunal.md` | 4e | Legacy Greater Alps lore; convert mechanics. |
| `reviewed/Ars Magica 4e - Icelandic Wars - Land of Fire and Ice.md` | 4e | Legacy Iceland scenario material; convert mechanics. |
| `reviewed/Ars Magica 3e - Lion of the North - The Loch Leglean Tribunal.md` | 3e | Legacy Scotland/Loch Leglean lore; distrust rules assumptions. |
| `reviewed/Ars Magica 3e - Tribunals of Hermes - Rome.md` | 3e | Legacy Italy/Rome lore; 3e tone/metaplot may conflict with later editions. |

## Definitive Core Chapter Anchors

The core rules file has these top-level chapter anchors:

| Chapter | Starts Near | Use |
|---|---:|---|
| Introduction | line 340 | Game premise, troupe play, basic orientation. |
| The Order of Hermes | line 551 | Houses, Hermetic society, Code, politics. |
| Characters | line 971 | Character creation. |
| Virtues and Flaws | line 2770 | Character options and hooks. |
| Abilities | line 7114 | Skills and mundane capabilities. |
| Covenants | line 7792 | Shared home and campaign base. |
| Hermetic Magic | line 8735 | Core magic system. |
| Laboratory | line 10262 | Seasonal lab activities. |
| Spells | line 11959 | Spell lists and guidelines. |
| Long Term Events | line 15942 | Aging, warping, advancement. |
| Obstacles | line 16644 | Hazards, combat, damage, deprivation. |
| Realms | line 17362 | Magic, Faerie, Divine, Infernal, mundane supernatural context. |
| Bestiary | line 17743 | Creatures and stat blocks. |
| Mythic Europe | line 21400 | Historical and social setting. |
| Stories | line 21927 | Story structure and hooks. |
| Sagas | line 22123 | Campaign design and troupe patterns. |
| Reference Guide | line 22555 | Fast lookup for rules, spells, bestiary, and indexes. |

## Recommended Agentic Build Order

1. Generate `ars-magica-corpus-index.json` with title, edition, line count, completion state, heading tree, chapter spans, and license snippet per reviewed book.
2. Generate heading-subtree chunks for RAG, not fixed-size token chunks. Include source path, line start, line end, book, edition, chapter, and heading path.
3. Extract the Definitive core indexes into structured reference tables: virtues, flaws, abilities, spells, spell guidelines, bestiary, combat, magic, lab, and seasonal rules.
4. Extract `Covenants` into a covenant-builder knowledge pack: boons/hooks, governance, resources, covenfolk, wealth, vis sources, library, sanctum, labs.
5. Add parsers for stat blocks, story seeds, spell entries, virtue/flaw entries, and tribunal gazetteer entities.
6. Create focused skills for session prep, rules lookup, covenant design, character creation, seasonal advancement, story seed generation, and tribunal exploration.

## Candidate Skills

| Skill | Inputs | Outputs |
|---|---|---|
| `ars-magica-rules-guide` | Rules question plus context | Definitive Edition answer with citations and edition warnings. |
| `ars-magica-character-helper` | Player concept, house, role, complexity | Character creation checklist, virtue/flaw suggestions, ability priorities. |
| `ars-magica-covenant-builder` | Tribunal, aura, season, group tone, resources | Covenant dossier, boons/hooks, labs, library, vis, covenfolk, story hooks. |
| `ars-magica-seasonal-advancement` | Character state, season activity, resources | Advancement/lab checklist and unresolved decisions. |
| `ars-magica-storyguide` | Saga location, faction, realm, desired tone | Session brief, NPCs, complications, hooks, lore citations. |
| `ars-magica-tribunal-gazetteer` | Region or tribunal | Places, covenants, magi, conflicts, rumors, travel hooks. |
| `ars-magica-conversion-auditor` | 3e/4e passage or book | Notes on lore salvage, likely mechanical conflicts, DE conversion warnings. |

## Working Rules For Future Agents

Do not assume every Ars Magica sourcebook is present. This sparse checkout currently contains only root files and `reviewed/`.

Prefer `rg` and heading-aware extraction over broad full-file reads. The Definitive core file is large.

When answering rules questions, cite `reviewed/Ars Magica - Definitive Edition (Core Rules).md` first. Bring in 5e sourcebooks only as secondary support.

When using 3e/4e material, explicitly mark it as legacy and avoid presenting mechanics as current.

When building generated artifacts, preserve source citations as path plus line span wherever possible.
