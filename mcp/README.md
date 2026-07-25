# Ars Magica MCP Server

Local FastMCP server for Ars Magica corpus lookup, deterministic mechanics, and printable-material publishing.

```bash
python3 mcp/ars_magica_server.py
```

Install extras in a consumer environment before running the server:

```bash
python3 -m pip install -e '.[mcp,publishing]'
```

## Tool groups

Corpus database tools preserve the existing SQLite-backed reference surface: `search_rules`, `get_section`, `list_book_toc`, `find_spell`, `lookup_virtue`, `lookup_flaw`, `lookup_ability`, and `lookup_covenant_option`.

Mechanics tools are deterministic and do not require the corpus database: `roll_simple_die`, `roll_stress_die`, `calculate_casting_score`, `calculate_formulaic_casting`, `calculate_penetration`, `design_spell_level`, and `calculate_lab_total`.

Advancement tools are also database-independent and preserve the rules engine's components, warnings, metadata, and Core Rules citations: `calculate_xp_to_buy_score`, `calculate_score_progress`, `apply_advancement_experience`, `calculate_advancement_total`, `calculate_exposure_source_quality`, `calculate_practice_source_quality`, `calculate_training_source_quality`, `calculate_teaching_source_quality`, and `calculate_adventure_source_quality`.

Publishing tools discover and render checked-in print templates: `list_publishing_templates`, `inspect_publishing_template`, `render_material_html`, and `package_material_zip`.

If the SQLite database is missing or present only as a Git LFS pointer, only database-backed calls return `ars_magica_database_unavailable`; mechanics and publishing tools remain usable.

## Database deployment contract

Set `ARS_MAGICA_DB_PATH` in deployment and automation to declare the generated
SQLite artifact location. Keep the repository's canonical
`skills/ars-magica-corpus-navigator/resources/ars_magica.sqlite` LFS object
read-only. Build an embedding-free FTS database in an isolated temporary
checkout, validate it, then deploy that artifact to the configured path.

Database consumers must verify supported corpus schema and builder versions
before querying. Missing, LFS-pointer, or incompatible databases return
`ars_magica_database_unavailable`; database-independent mechanics, advancement,
and publishing calls remain available. Vector embeddings are optional:
embedding-free FTS lookup works without `OPENAI_API_KEY`, `openai`, or
`sqlite-vec`.
