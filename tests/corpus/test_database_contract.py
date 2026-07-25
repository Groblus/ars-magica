"""Focused runtime-contract coverage for corpus SQLite databases."""

from __future__ import annotations

import importlib.util
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

FAST_MCP_AVAILABLE = importlib.util.find_spec("fastmcp") is not None
if FAST_MCP_AVAILABLE:
    SERVER_PATH = Path(__file__).resolve().parents[2] / "mcp" / "ars_magica_server.py"
    SERVER_SPEC = importlib.util.spec_from_file_location("ars_magica_mcp_database", SERVER_PATH)
    assert SERVER_SPEC is not None and SERVER_SPEC.loader is not None
    server = importlib.util.module_from_spec(SERVER_SPEC)
    SERVER_SPEC.loader.exec_module(server)


@unittest.skipUnless(FAST_MCP_AVAILABLE, "requires the optional fastmcp dependency")
class DatabaseContractTests(unittest.TestCase):
    def database_result(self, path: Path) -> dict[str, object]:
        with patch.dict(os.environ, {"ARS_MAGICA_DB_PATH": str(path)}):
            result = server.search_rules.fn("magic")
        self.assertIsInstance(result, dict)
        return result

    def make_corpus_database(self, path: Path, schema_version: int | None = None) -> None:
        with sqlite3.connect(path) as conn:
            for table in server.REQUIRED_CORPUS_TABLES:
                conn.execute(f'CREATE TABLE "{table}" (id INTEGER)')
            if schema_version is not None:
                conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                conn.execute(
                    "INSERT INTO metadata (key, value) VALUES ('schema_version', ?)",
                    (str(schema_version),),
                )

    def make_synthetic_corpus_database(self, path: Path) -> None:
        """Create tiny, non-corpus database for MCP integration coverage."""
        with sqlite3.connect(path) as conn:
            for table in server.REQUIRED_CORPUS_TABLES:
                conn.execute(f'CREATE TABLE "{table}" (id INTEGER)')
                for column in (
                    "name TEXT",
                    "description TEXT",
                    "category TEXT",
                    "type TEXT",
                    "magnitude TEXT",
                    "categories_json TEXT",
                    "meta TEXT",
                    "heading_path TEXT",
                    "citation TEXT",
                    "source_file TEXT",
                    "source_path TEXT",
                    "source_start_line INTEGER",
                    "source_end_line INTEGER",
                ):
                    conn.execute(f'ALTER TABLE "{table}" ADD COLUMN {column}')
                conn.execute(
                    f'INSERT INTO "{table}" '
                    "(id, name, description, category, type, source_file, source_path, "
                    "source_start_line, source_end_line, magnitude, categories_json, meta, heading_path, citation) VALUES "
                    "(1, 'Synthetic Virtue', 'Test-only structured record.', 'Virtue', "
                    "'Minor', 'synthetic.md', 'synthetic.md', 10, 12, 'Minor', '[\"Virtue\"]', "
                    "'{}', 'Synthetic virtue', 'synthetic.md:10-12')"
                )
            conn.execute("DROP TABLE IF EXISTS metadata")
            conn.execute("DROP TABLE IF EXISTS books")
            conn.execute("DROP TABLE IF EXISTS sections")
            conn.execute("DROP TABLE IF EXISTS chunks")
            conn.execute("DROP TABLE IF EXISTS chunks_fts")
            conn.execute("DROP TABLE IF EXISTS virtues")
            conn.execute("DROP TABLE IF EXISTS virtues_fts")
            conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            conn.execute("INSERT INTO metadata (key, value) VALUES ('schema_version', '1')")
            conn.execute(
                "CREATE TABLE books ("
                "id INTEGER PRIMARY KEY, title TEXT, path TEXT, source_path TEXT, slug TEXT)"
            )
            conn.execute(
                "CREATE TABLE sections ("
                "id INTEGER PRIMARY KEY, book_id INTEGER, heading TEXT, title TEXT, "
                "level INTEGER, start_line INTEGER, end_line INTEGER, path TEXT)"
            )
            conn.execute(
                "CREATE TABLE chunks ("
                "id INTEGER PRIMARY KEY, book_id INTEGER, section_id INTEGER, heading TEXT, "
                "heading_path TEXT, content TEXT, text TEXT, start_line INTEGER, end_line INTEGER, "
                "line_start INTEGER, line_end INTEGER, citation TEXT)"
            )
            conn.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(content)")
            conn.execute(
                "CREATE TABLE virtues ("
                "id INTEGER PRIMARY KEY, name TEXT, category TEXT, type TEXT, "
                "description TEXT, source_file TEXT, source_start_line INTEGER, "
                "source_end_line INTEGER, magnitude TEXT, categories_json TEXT, meta TEXT, "
                "heading_path TEXT, citation TEXT)"
            )
            conn.execute("CREATE VIRTUAL TABLE virtues_fts USING fts5(name, description)")
            conn.execute(
                "INSERT INTO books (id, title, path, source_path, slug) "
                "VALUES (1, 'Synthetic Book', 'synthetic.md', 'synthetic.md', 'synthetic-book')"
            )
            conn.execute(
                "INSERT INTO sections (id, book_id, heading, title, level, start_line, end_line, path) "
                "VALUES (1, 1, 'Synthetic section', 'Synthetic section', 1, 1, 9, 'Synthetic section')"
            )
            chunks = [
                (1, "First scene", "Synthetic magic appears here.", 1, 3),
                (2, "Second scene", "Synthetic laboratory notes.", 4, 6),
                (3, "Third scene", "Synthetic covenant records.", 7, 9),
            ]
            for chunk_id, heading, content, start_line, end_line in chunks:
                conn.execute(
                    "INSERT INTO chunks "
                    "(id, book_id, section_id, heading, heading_path, content, text, start_line, end_line, "
                    "line_start, line_end, citation) VALUES (?, 1, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        chunk_id,
                        heading,
                        heading,
                        content,
                        content,
                        start_line,
                        end_line,
                        start_line,
                        end_line,
                        f"synthetic.md:{start_line}-{end_line}",
                    ),
                )
                conn.execute(
                    "INSERT INTO chunks_fts (rowid, content) VALUES (?, ?)",
                    (chunk_id, content),
                )
            conn.execute(
                "INSERT INTO virtues "
                "(id, name, category, type, description, source_file, source_start_line, source_end_line, "
                "magnitude, categories_json, meta, heading_path, citation) "
                "VALUES (1, 'Synthetic Virtue', 'General', 'Minor', "
                "'Test-only structured record.', 'synthetic.md', 10, 12, 'Minor', '[\"Virtue\"]', "
                "'{}', 'Synthetic virtue', 'synthetic.md:10-12')"
            )
            conn.execute(
                "INSERT INTO virtues_fts (rowid, name, description) "
                "VALUES (1, 'Synthetic Virtue', 'Test-only structured record.')"
            )

    def test_lfs_pointer_is_localized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.sqlite"
            path.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:test\n")
            result = self.database_result(path)
        self.assertEqual(result["error"], "ars_magica_database_unavailable")
        self.assertIn("Git LFS pointer", str(result["reason"]))

    def test_invalid_file_is_localized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.sqlite"
            path.write_text("not sqlite")
            result = self.database_result(path)
        self.assertEqual(result["error"], "ars_magica_database_unavailable")
        self.assertEqual(result["reason"], "database file is not a SQLite database")

    def test_unsupported_schema_version_is_localized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.sqlite"
            self.make_corpus_database(path, schema_version=2)
            result = self.database_result(path)
        self.assertEqual(result["error"], "ars_magica_database_unavailable")
        self.assertEqual(
            result["reason"],
            "unsupported database schema version: 2; expected 1",
        )

    def test_versioned_database_with_expected_schema_connects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.sqlite"
            self.make_corpus_database(path, schema_version=1)
            with (
                patch.dict(os.environ, {"ARS_MAGICA_DB_PATH": str(path)}),
                server.connect() as conn,
            ):
                self.assertEqual(
                    conn.execute(
                        "SELECT value FROM metadata WHERE key = 'schema_version'"
                    ).fetchone()[0],
                    "1",
                )

    def test_legacy_database_with_required_tables_connects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.sqlite"
            self.make_corpus_database(path)
            with (
                patch.dict(os.environ, {"ARS_MAGICA_DB_PATH": str(path)}),
                server.connect() as conn,
            ):
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM books").fetchone()[0], 0)

    def test_synthetic_database_supports_search_and_structured_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.sqlite"
            self.make_synthetic_corpus_database(path)
            with patch.dict(os.environ, {"ARS_MAGICA_DB_PATH": str(path)}):
                search = server.search_rules.fn("magic")
                virtue = server.lookup_virtue.fn("Synthetic Virtue")
        self.assertNotIn("error", search)
        self.assertIn("Synthetic", str(search))
        self.assertNotIn("error", virtue)
        self.assertIn("Synthetic Virtue", str(virtue))


if __name__ == "__main__":
    unittest.main()
