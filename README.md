# Ars Magica Agentic Reference Lab

[![skills.sh](https://skills.sh/b/Groblus/ars-magica)](https://skills.sh/Groblus/ars-magica)

Private exploratory fork of the Ars Magica Open License Markdown corpus, focused on making the **Definitive Edition** and compatible **5th Edition** books useful to AI agents, storyguides, players, and software tools.

## What is in this repo

- Corpus browser and reports under `docs/`.
- Citation-first corpus navigator under `skills/ars-magica-corpus-navigator/`.
- Play and production skills under `skills/`.
- Pydantic domain contracts under `src/ars_magica/models/` and JSON Schemas under `schemas/v1/`.
- Deterministic, auditable mechanics under `src/ars_magica/rules/`.
- Printable material pipeline under `src/ars_magica/publishing/` and bundled `press/` resources.
- Local MCP server under `mcp/ars_magica_server.py`.
- CLI entry point `ars-magica`.

## Install for local development

Core models require Pydantic:

```bash
python3 -m pip install -e .
```

Publishing, MCP, and tests are optional extras:

```bash
python3 -m pip install -e '.[publishing,mcp,test]'
```

No lockfile is currently maintained in this repo.

## Local quality checks

Install the development tools and all CI extras:

```bash
python3 -m pip install -e '.[dev,test,mcp,publishing]'
```

Run the same checks as CI:

```bash
ruff check .
ruff format --check .
ty check
python -m pytest -q
```

CI keeps `GIT_LFS_SKIP_SMUDGE=1` and uses synthetic SQLite fixtures. It does
not download or rebuild the corpus database.

## CLI examples

```bash
ars-magica dice simple --roll 0
ars-magica dice stress --rolls 1,1,5 --botch-dice 1
ars-magica templates list
ars-magica templates inspect magus-character-sheet
ars-magica render-html examples/material.json -o material.html
ars-magica package examples/material.json build/material.zip
```

Material specs use checked-in templates, themes, and presets from `press/`:

```json
{
  "title": "A Test Magus",
  "template": "magus-character-sheet",
  "theme": "clear-ledger",
  "preset": "home-letter",
  "audience": "player",
  "content": {
    "identity": {"name": "Aelia", "house": "Bonisagus"},
    "characteristics": {},
    "arts": [],
    "abilities": []
  },
  "assets": [],
  "source_references": []
}
```

The same renderer accepts `ars_magica.models.ArtifactSpec` directly: use
`template_id`, `style_profile_id`, `print_preset_id`, and `data` instead of
the compact mapping keys. Source references can be precise strings such as
`reviewed/Core.md:500-510` or `SourceReference` values. Publishing filters
all content, assets, and citations recursively for the requested audience
before templates or ZIP packages receive them.

PDF rendering uses WeasyPrint 69. On macOS its Python package also needs
native Pango/GObject libraries. Install them first, for example:

```bash
brew install pango gobject-introspection libffi
```

Then follow the [WeasyPrint macOS installation instructions](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#macos) for library paths if `render_pdf` still reports a native-library error.

## Skills

Install with the Skills CLI:

```bash
npx skills add Groblus/ars-magica
```

Current skills include:

```text
ars-magica
ars-magica-corpus-navigator
ars-magica-rules-assistant
ars-magica-advancement-assistant
ars-magica-software-builder
ars-magica-publication-designer
ars-magica-character-helper
ars-magica-covenant-builder
ars-magica-spell-lab-assistant
ars-magica-storyguide-prep
```

The main skill routes work across corpus lookup, rules, advancement, software contracts, saga prep, and publication design. The navigator remains the citation layer. Mechanics helpers preserve source citations in returned results.

## RAG setup

The navigator skill expects a generated retrieval database:

```text
skills/ars-magica-corpus-navigator/resources/ars_magica.sqlite
```

It contains heading-aware chunks, structured rules/play entries, SQLite FTS5 search, and optional vector embeddings. If this file is absent or present only as a Git LFS pointer, database-backed MCP tools report a localized `ars_magica_database_unavailable` error while dice, mechanics, and publishing tools still work.

### Database location, rebuilds, and compatibility

`ARS_MAGICA_DB_PATH` is the deployment and automation contract for an
alternate generated database location. Keep the checked-in
`skills/ars-magica-corpus-navigator/resources/ars_magica.sqlite` LFS object
unchanged; it is a distributable artifact, not a rebuild target.

For an embedding-free rebuild, work in an isolated checkout under a temporary
directory, remove its LFS pointer, then build and validate there. This avoids
opening a pointer as SQLite and prevents local rebuilds from replacing the
canonical LFS object:

```bash
export ARS_MAGICA_DB_PATH="$TMPDIR/ars-magica-corpus/skills/ars-magica-corpus-navigator/resources/ars_magica.sqlite"
git clone --no-local . "$TMPDIR/ars-magica-corpus"
cd "$TMPDIR/ars-magica-corpus"
rm -f skills/ars-magica-corpus-navigator/resources/ars_magica.sqlite
python3 skills/ars-magica-corpus-navigator/scripts/build_index.py
python3 skills/ars-magica-corpus-navigator/scripts/validate.py
```

The SQLite contract is versioned with the corpus builder and schema. Consumers
must reject an unsupported or missing schema/version rather than query it.
Current `build_index.py` creates FTS and structured records without embeddings;
`build_embeddings.py` is an optional follow-up that requires `OPENAI_API_KEY`,
`openai`, and `sqlite-vec`. FTS-only lookup remains supported when embeddings
are absent.

Examples:

```bash
python3 skills/ars-magica-corpus-navigator/scripts/search.py "penetration magic resistance" --limit 5
.venv/bin/python skills/ars-magica-corpus-navigator/scripts/search.py "faerie aura" --vector --limit 5
.venv/bin/python skills/ars-magica-corpus-navigator/scripts/search.py "Tremere politics" --hybrid --limit 5
```

## MCP server

Run the local FastMCP server:

```bash
python3 mcp/ars_magica_server.py
```

The server exposes corpus database tools, deterministic mechanics, and publishing discovery/render tools. It makes no OpenAI calls.

## Rebuild corpus indexes

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

Do not rebuild over the checked-in LFS pointer. Use the isolated embedding-free
rebuild above for large local validation, then add embeddings only when vector
search is required. PR CI uses tiny synthetic SQLite fixtures instead of
rebuilding the corpus.

## Source material

This fork is based on the Ars Magica Open License Markdown corpus by OriginalMadman/YR7. The root license is preserved in `LICENSE.md`.

Use the Definitive core as the baseline rules authority. Use compatible 5th Edition supplements as supporting material when they are relevant and cited.
