---
name: ars-magica-corpus-navigator
description: Navigate the local Ars Magica Open License corpus as a reference shelf. Use when finding, citing, indexing, or answering from Ars Magica Definitive Edition and 5th Edition Markdown books; when routing questions to core rules, Houses, Realms, covenants, tribunal books, or mundane society books; or when using the generated SQLite/FTS/vector index. Excludes 3rd and 4th Edition material.
---

# Ars Magica Corpus Navigator

Use this skill to find cited sections in the local Ars Magica corpus. It is a navigator, not a rules memory dump: select likely books, inspect generated TOCs/indexes, read source line spans, then answer with citations.

## Hard Policy

- Use only Definitive Edition and 5th Edition books listed in `resources/allowed-books.json`.
- Treat `reviewed/Ars Magica - Definitive Edition (Core Rules).md` as the rules authority.
- Use 5e sourcebooks as compatible support.
- Do not use 3e or 4e books for this skill. If a user asks for them, say they are outside this navigator and need a legacy/conversion pass.
- Cite answers with `path:line_start-line_end` whenever source content is used.

## Navigation Workflow

1. Read `references/sourcebook-routing.md` to pick candidate books.
2. Use `resources/heading-index.json` or `scripts/search.py` to find sections.
3. Prefer Definitive Edition core for rules questions; add 5e sourcebooks only when the topic needs supplement depth.
4. Read the relevant source Markdown span before answering.
5. If a section is too narrow, expand one heading level outward before jumping to another book.
6. Answer with concise source citations and edition status.

## Fast Commands

From the repository root:

```bash
python3 skills/ars-magica-corpus-navigator/scripts/build_index.py
python3 skills/ars-magica-corpus-navigator/scripts/validate.py
python3 skills/ars-magica-corpus-navigator/scripts/search.py "laboratory total" --hybrid
```

Embeddings use OpenAI `text-embedding-3-large` at 3072 dimensions:

```bash
python3 skills/ars-magica-corpus-navigator/scripts/build_embeddings.py
```

`build_embeddings.py` reads `.env` manually. It requires `OPENAI_API_KEY`, the `openai` Python package, and `sqlite-vec`/`sqlite_vec` for vector indexing.

## References

- `references/book-map.md`: human-readable book shelf.
- `references/sourcebook-routing.md`: topic-to-book routing.
- `references/navigation-workflow.md`: lookup procedure.
- `references/citation-rules.md`: citation and edition rules.
- `references/toc/`: generated per-book tables of contents.
- `resources/allowed-books.json`: whitelist.
- `resources/heading-index.json`: generated heading tree.
- `resources/ars_magica.sqlite`: generated SQLite FTS/vector-ready database.
