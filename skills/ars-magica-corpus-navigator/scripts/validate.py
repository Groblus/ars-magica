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
DOCS_DATA = REPO_ROOT / "docs" / "data"
CORE_PATH = "reviewed/Ars Magica - Definitive Edition (Core Rules).md"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def require_fields(obj: dict, fields: list[str], label: str) -> None:
    missing = [field for field in fields if field not in obj]
    if missing:
        fail(f"{label} missing fields: {', '.join(missing)}")


def main() -> None:
    allowed_path = RESOURCES / "allowed-books.json"
    heading_path = RESOURCES / "heading-index.json"
    library_path = DOCS_DATA / "library.json"
    core_data_path = DOCS_DATA / "core-data.json"
    if not allowed_path.exists():
        fail("missing allowed-books.json")
    if not heading_path.exists():
        fail("missing heading-index.json")
    if not DB_PATH.exists():
        fail("missing ars_magica.sqlite")
    if not library_path.exists():
        fail("missing docs/data/library.json")
    if not core_data_path.exists():
        fail("missing docs/data/core-data.json")

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
    library = json.loads(library_path.read_text())
    core_data = json.loads(core_data_path.read_text())
    core = next((b for b in index["books"] if b["edition"] == "DE"), None)
    if not core:
        fail("missing DE core")
    core_headings = {h["title"] for h in core["headings"]}
    for required in ["Chapter 7: Hermetic Magic", "Chapter 8: Laboratory", "Chapter 9: Spells", "Reference Guide"]:
        if required not in core_headings:
            fail(f"missing core heading: {required}")
    if library["summary"]["book_count"] != len(allowed):
        fail("library.json book count mismatch")
    library_books = library.get("books")
    if not isinstance(library_books, list) or not library_books:
        fail("library.json missing books")
    for idx, book in enumerate(library_books):
        require_fields(
            book,
            ["id", "path", "title", "edition", "priority", "line_count", "heading_count", "chapter_count", "headings", "chapters"],
            f"library book {idx}",
        )
        if not isinstance(book["headings"], list) or not book["headings"]:
            fail(f"library book {idx} missing heading array data")
        if not isinstance(book["chapters"], list) or not book["chapters"]:
            fail(f"library book {idx} missing chapter array data")
        if book["heading_count"] != len(book["headings"]):
            fail(f"library book {idx} heading_count mismatch")
        if book["chapter_count"] != len(book["chapters"]):
            fail(f"library book {idx} chapter_count mismatch")
        sample_heading = book["headings"][0]
        require_fields(
            sample_heading,
            ["id", "title", "slug", "level", "line_start", "line_end", "heading_path", "section_type"],
            f"library heading {idx}",
        )
        if not isinstance(sample_heading["heading_path"], list) or not sample_heading["heading_path"]:
            fail(f"library heading {idx} invalid heading_path")
        if not isinstance(sample_heading["level"], int) or sample_heading["level"] < 1:
            fail(f"library heading {idx} invalid level")
        if not isinstance(sample_heading["line_start"], int) or not isinstance(sample_heading["line_end"], int):
            fail(f"library heading {idx} invalid line span")
        sample_chapter = book["chapters"][0]
        require_fields(sample_chapter, ["id", "title", "level", "line_start", "line_end", "heading_path", "section_type"], f"library chapter {idx}")
        if sample_chapter["section_type"] != "chapter":
            fail(f"library chapter {idx} missing chapter section_type")
    if core_data["book"]["path"] != CORE_PATH:
        fail("core-data book path mismatch")
    if core_data["summary"]["virtue_count"] <= 50:
        fail("virtue extraction too small")
    if core_data["summary"]["flaw_count"] <= 50:
        fail("flaw extraction too small")
    if core_data["summary"]["ability_count"] <= 20:
        fail("ability extraction too small")
    if core_data["summary"]["spell_count"] <= 200:
        fail("spell extraction too small")
    for key in ["virtues", "flaws", "abilities", "spells"]:
        if len(core_data[key]) != core_data["summary"][f"{key[:-1] if key != 'abilities' else 'ability'}_count"]:
            fail(f"core-data count mismatch for {key}")
    core_contract = {
        "virtues": ["id", "name", "magnitude", "categories", "description", "source_path", "line_start", "line_end"],
        "flaws": ["id", "name", "magnitude", "categories", "description", "source_path", "line_start", "line_end"],
        "abilities": ["id", "name", "ability_type", "description", "source_path", "line_start", "line_end"],
        "spells": ["id", "name", "technique", "form", "range", "duration", "target", "description", "source_path", "line_start", "line_end"],
    }
    for bucket, fields in core_contract.items():
        sample = core_data[bucket][0]
        require_fields(sample, fields, f"core-data {bucket}")
        if not sample["description"]:
            fail(f"core-data {bucket} empty description")
        if sample["source_path"] != CORE_PATH:
            fail(f"core-data {bucket} bad source_path")
        if not isinstance(sample["line_start"], int) or not isinstance(sample["line_end"], int):
            fail(f"core-data {bucket} invalid line span")
    if not isinstance(core_data["virtues"][0]["categories"], list):
        fail("core-data virtues categories not list")
    if not isinstance(core_data["flaws"][0]["categories"], list):
        fail("core-data flaws categories not list")
    if not isinstance(core_data["spells"][0]["ritual"], bool):
        fail("core-data spells ritual not bool")

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
    virtue_count = conn.execute("SELECT count(*) FROM core_virtues").fetchone()[0]
    flaw_count = conn.execute("SELECT count(*) FROM core_flaws").fetchone()[0]
    ability_count = conn.execute("SELECT count(*) FROM core_abilities").fetchone()[0]
    spell_count = conn.execute("SELECT count(*) FROM core_spells").fetchone()[0]
    if virtue_count != core_data["summary"]["virtue_count"]:
        fail(f"virtue count mismatch db={virtue_count} json={core_data['summary']['virtue_count']}")
    if flaw_count != core_data["summary"]["flaw_count"]:
        fail(f"flaw count mismatch db={flaw_count} json={core_data['summary']['flaw_count']}")
    if ability_count != core_data["summary"]["ability_count"]:
        fail(f"ability count mismatch db={ability_count} json={core_data['summary']['ability_count']}")
    if spell_count != core_data["summary"]["spell_count"]:
        fail(f"spell count mismatch db={spell_count} json={core_data['summary']['spell_count']}")
    bad_core_sources = conn.execute(
        """
        SELECT count(*) FROM (
          SELECT source_path FROM core_virtues
          UNION ALL SELECT source_path FROM core_flaws
          UNION ALL SELECT source_path FROM core_abilities
          UNION ALL SELECT source_path FROM core_spells
        ) WHERE source_path != ?
        """,
        (CORE_PATH,),
    ).fetchone()[0]
    if bad_core_sources:
        fail(f"unexpected structured source rows={bad_core_sources}")
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
    sample_core = conn.execute("SELECT citation FROM core_virtues LIMIT 5").fetchall()
    sample_core += conn.execute("SELECT citation FROM core_flaws LIMIT 5").fetchall()
    sample_core += conn.execute("SELECT citation FROM core_abilities LIMIT 5").fetchall()
    sample_core += conn.execute("SELECT citation FROM core_spells LIMIT 5").fetchall()
    for (citation,) in sample_core:
        path_part, span = citation.rsplit(":", 1)
        start_s, end_s = span.split("-", 1)
        lines = (REPO_ROOT / path_part).read_text(encoding="utf-8", errors="replace").splitlines()
        if int(start_s) < 1 or int(end_s) > len(lines):
            fail(f"structured citation out of bounds: {citation}")
    conn.close()
    print(
        f"OK: books={book_count} chunks={chunk_count} virtues={virtue_count} flaws={flaw_count} "
        f"abilities={ability_count} spells={spell_count}"
    )


if __name__ == "__main__":
    main()
