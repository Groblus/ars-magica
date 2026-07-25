"""Focused runtime-contract coverage for corpus SQLite databases."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
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
                conn.execute("CREATE TABLE metadata (schema_version INTEGER NOT NULL)")
                conn.execute("INSERT INTO metadata (schema_version) VALUES (?)", (schema_version,))

    def test_lfs_pointer_is_localized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.sqlite"
            path.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:test\n")
            result = self.database_result(path)
        self.assertEqual(result["error"], "ars_magica_database_unavailable")
        self.assertIn("Git LFS pointer", result["reason"])

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
            with patch.dict(os.environ, {"ARS_MAGICA_DB_PATH": str(path)}):
                with server.connect() as conn:
                    self.assertEqual(conn.execute("SELECT schema_version FROM metadata").fetchone()[0], 1)

    def test_legacy_database_with_required_tables_connects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.sqlite"
            self.make_corpus_database(path)
            with patch.dict(os.environ, {"ARS_MAGICA_DB_PATH": str(path)}):
                with server.connect() as conn:
                    self.assertEqual(conn.execute("SELECT COUNT(*) FROM books").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
