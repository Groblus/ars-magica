#!/usr/bin/env python3
"""Validate generated Ars Magica navigator artifacts."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
RESOURCES = SKILL_DIR / "resources"
DB_PATH = RESOURCES / "ars_magica.sqlite"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    allowed_path = RESOURCES / "allowed-books.json"
    heading_path = RESOURCES / "heading-index.json"
    if not allowed_path.exists():
        fail("missing allowed-books.json")
    if not heading_path.exists():
        fail("missing heading-index.json")
    if not DB_PATH.exists():
        fail("missing ars_magica.sqlite")

    allowed = json.loads(allowed_path.read_text())
    if len(allowed) != 20:
        fail(f"expected 20 allowed books, got {len(allowed)}")
    for item in allowed:
        p = item["path"]
        if " 3e " in p or " 4e " in p or "Ars Magica 3e" in p or "Ars Magica 4e" in p:
            fail(f"legacy path leaked: {p}")
        if not (REPO_ROOT / p).exists():
            fail(f"source path missing: {p}")

    index = json.loads(heading_path.read_text())
    core = next((b for b in index["books"] if b["edition"] == "DE"), None)
    if not core:
        fail("missing DE core")
    core_headings = {h["title"] for h in core["headings"]}
    for required in ["Chapter 7: Hermetic Magic", "Chapter 8: Laboratory", "Chapter 9: Spells", "Reference Guide"]:
        if required not in core_headings:
            fail(f"missing core heading: {required}")

    conn = sqlite3.connect(DB_PATH)
    book_count = conn.execute("SELECT count(*) FROM books").fetchone()[0]
    if book_count != 20:
        fail(f"db expected 20 books, got {book_count}")
    legacy_count = conn.execute("SELECT count(*) FROM books WHERE path LIKE '% 3e %' OR path LIKE '% 4e %'").fetchone()[0]
    if legacy_count:
        fail("legacy book in db")
    chunk_count = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    fts_count = conn.execute("SELECT count(*) FROM chunks_fts").fetchone()[0]
    if chunk_count == 0 or chunk_count != fts_count:
        fail(f"chunk/fts mismatch chunks={chunk_count} fts={fts_count}")
    embedding_count = conn.execute("SELECT count(*) FROM embeddings").fetchone()[0]
    if embedding_count:
        bad_embeddings = conn.execute(
            "SELECT count(*) FROM embeddings WHERE model != 'text-embedding-3-large' OR dimensions != 3072"
        ).fetchone()[0]
        if bad_embeddings:
            fail(f"bad embedding metadata rows={bad_embeddings}")
        if embedding_count != chunk_count:
            fail(f"partial embeddings embeddings={embedding_count} chunks={chunk_count}")

    sample = conn.execute("SELECT citation,text FROM chunks ORDER BY id LIMIT 25").fetchall()
    for citation, text in sample:
        path_part, span = citation.rsplit(":", 1)
        start_s, end_s = span.split("-", 1)
        lines = (REPO_ROOT / path_part).read_text(encoding="utf-8", errors="replace").splitlines()
        source = "\n".join(lines[int(start_s) - 1 : int(end_s)]).strip()
        if source != text.strip():
            fail(f"citation mismatch: {citation}")
    conn.close()
    print(f"OK: books={book_count} chunks={chunk_count}")


if __name__ == "__main__":
    main()
