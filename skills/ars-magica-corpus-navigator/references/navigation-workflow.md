# Navigation Workflow

1. Identify the user's topic: core rule, character option, covenant, House, Realm, tribunal, mundane society, story/saga, or reference lookup.
2. Check `sourcebook-routing.md` for likely books.
3. Use `search.py` or `heading-index.json` to locate sections.
4. Open only relevant source spans.
5. Expand to parent heading if local context is incomplete.
6. Answer from Definitive Edition first for rules, then 5e support.

Good lookup pattern:

```bash
python3 skills/ars-magica-corpus-navigator/scripts/search.py "penetration magic resistance" --hybrid --limit 8
```

Then read the cited source lines.

## Rebuild Environment

Use the system Python for non-embedding artifacts:

```bash
python3 skills/ars-magica-corpus-navigator/scripts/build_index.py
```

Use the local venv for vector artifacts:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv venv .venv
UV_CACHE_DIR=/tmp/uv-cache uv pip install --python .venv/bin/python openai sqlite-vec
.venv/bin/python skills/ars-magica-corpus-navigator/scripts/build_embeddings.py
```

`build_embeddings.py` reads `OPENAI_API_KEY` from `.env` or the environment.
