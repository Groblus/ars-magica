# Ars Magica Agentic Reference Lab

[![skills.sh](https://skills.sh/b/Groblus/ars-magica)](https://skills.sh/Groblus/ars-magica)

Private exploratory fork of the Ars Magica Open License Markdown corpus, focused on making the **Definitive Edition** and **5th Edition** books useful to AI agents and human readers.

## Browse

- Landing page: `docs/index.html`
- Human inventory report: `docs/report.html`
- Browser reference library: `docs/library.html`
- First-session packet: `docs/first-session.html`
- Agent guide: `AGENTS.md`
- Claude redirect: `CLAUDE.md`
- Corpus navigator skill: `skills/ars-magica-corpus-navigator/`
- Focused play skills: `skills/ars-magica-character-helper/`, `skills/ars-magica-covenant-builder/`, `skills/ars-magica-spell-lab-assistant/`, `skills/ars-magica-storyguide-prep/`
- Local MCP server: `mcp/ars_magica_server.py`
- Generated book TOCs: `skills/ars-magica-corpus-navigator/references/toc.md`

If GitHub Pages is enabled, the landing page should publish at:

```text
https://groblus.github.io/ars-magica/
```

## Install Skill

The repo follows the skills.sh convention of storing skills under `skills/<skill-name>/SKILL.md`.

Install with the Skills CLI:

```bash
npx skills add Groblus/ars-magica
```

Available skills are:

```text
ars-magica-corpus-navigator
ars-magica-character-helper
ars-magica-covenant-builder
ars-magica-spell-lab-assistant
ars-magica-storyguide-prep
```

The navigator skill provides citation-first corpus lookup. The focused skills use it for character concepts, covenant design, spell/lab assistance, and storyguide prep. All use Definitive Edition as the rules authority and 5e books as compatible supplements. They explicitly exclude 3e/4e material for now.

## RAG Setup

The navigator skill includes a generated retrieval database:

```text
skills/ars-magica-corpus-navigator/resources/ars_magica.sqlite
```

It contains:

- `20` allowed books: Definitive Edition core plus 19 5e books.
- `9,967` heading-aware chunks.
- `1,953` structured rules/play entries across virtues, flaws, abilities, spells, spell guidelines, lab references, combat tables, and covenant boons/hooks.
- SQLite FTS5 search.
- OpenAI `text-embedding-3-large` embeddings at `3072` dimensions.
- sqlite-vector table for vector search.

Examples:

```bash
python3 skills/ars-magica-corpus-navigator/scripts/search.py "penetration magic resistance" --limit 5
.venv/bin/python skills/ars-magica-corpus-navigator/scripts/search.py "faerie aura" --vector --limit 5
.venv/bin/python skills/ars-magica-corpus-navigator/scripts/search.py "Tremere politics" --hybrid --limit 5
```

## MCP Server

Run the local FastMCP server to expose the SQLite index as agent-callable tools:

```bash
python3 mcp/ars_magica_server.py
```

The server provides tools for FTS rule search, section retrieval, book TOCs, spells, virtues, flaws, abilities, and covenant options. It uses only the local SQLite database and makes no OpenAI calls.

## Rebuild

Generate TOCs, JSON indexes, SQLite, and FTS:

```bash
python3 skills/ars-magica-corpus-navigator/scripts/build_index.py
```

Generate embeddings:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv venv .venv
UV_CACHE_DIR=/tmp/uv-cache uv pip install --python .venv/bin/python openai sqlite-vec
.venv/bin/python skills/ars-magica-corpus-navigator/scripts/build_embeddings.py
```

`build_embeddings.py` reads `OPENAI_API_KEY` from `.env` or the environment.

Validate:

```bash
python3 skills/ars-magica-corpus-navigator/scripts/validate.py
python3 /home/olive/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ars-magica-corpus-navigator
```

## Source Material

This fork is based on the Ars Magica Open License Markdown corpus by OriginalMadman/YR7. The root license is preserved in `LICENSE.md`.

The original upstream project describes the full 53-book conversion effort. This sparse checkout currently includes a reviewed subset and adds agent-facing navigation, indexes, and retrieval tooling.
