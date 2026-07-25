#!/usr/bin/env python3
"""Build OpenAI text-embedding-3-large embeddings for navigator chunks."""

from __future__ import annotations

import argparse
import os
import sqlite3
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
DEFAULT_DB_PATH = SKILL_DIR / "resources" / "ars_magica.sqlite"
ENV_DB_PATH = "ARS_MAGICA_DB_PATH"
SCHEMA_VERSION = 1
SQLITE_HEADER = b"SQLite format 3\x00"
LFS_POINTER_HEADER = b"version https://git-lfs.github.com/spec/v1"
MODEL = "text-embedding-3-large"
DIMENSIONS = 3072
REQUIRED_CORE_TABLES = frozenset(
    {
        "books",
        "sections",
        "chunks",
        "core_spells",
        "core_virtues",
        "core_flaws",
        "core_abilities",
        "covenant_boons_hooks",
    }
)


def db_path() -> Path:
    return Path(os.environ.get(ENV_DB_PATH, DEFAULT_DB_PATH)).expanduser()


def validate_database(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise RuntimeError(f"database file is missing: {path}")
    try:
        with path.open("rb") as database_file:
            header = database_file.read(128)
    except OSError as error:
        raise RuntimeError(f"database file could not be read: {path}: {error}") from error
    if header.startswith(LFS_POINTER_HEADER):
        raise RuntimeError("database file is a Git LFS pointer; fetch LFS assets before building embeddings")
    if not header.startswith(SQLITE_HEADER):
        raise RuntimeError(f"database file is not a SQLite database: {path}")

    try:
        conn = sqlite3.connect(path)
        table_names = {
            str(row[0])
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        missing_tables = sorted(REQUIRED_CORE_TABLES - table_names)
        if missing_tables:
            raise RuntimeError(
                "database is missing required corpus tables: " + ", ".join(missing_tables)
            )
        if "metadata" not in table_names:
            return conn

        metadata_columns = {
            str(row[1]) for row in conn.execute("PRAGMA table_info(metadata)")
        }
        if not {"key", "value"}.issubset(metadata_columns):
            raise RuntimeError("database metadata must contain key and value columns")
        version_rows = conn.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version' LIMIT 2"
        ).fetchall()
        if len(version_rows) != 1 or version_rows[0][0] != str(SCHEMA_VERSION):
            raise RuntimeError(
                f"unsupported database schema version; expected {SCHEMA_VERSION}"
            )
        return conn
    except Exception:
        if "conn" in locals():
            conn.close()
        raise


def load_env() -> None:
    env = REPO_ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def require_deps():
    try:
        from openai import OpenAI
    except Exception as exc:
        print("Missing dependency: openai. Install before embeddings: pip install openai", file=sys.stderr)
        raise SystemExit(2) from exc
    try:
        import sqlite_vec
    except Exception as exc:
        print("Missing dependency: sqlite_vec/sqlite-vec. Install sqlite-vector support before embeddings.", file=sys.stderr)
        raise SystemExit(2) from exc
    return OpenAI, sqlite_vec


def pack(values: list[float]) -> bytes:
    return struct.pack(f"{len(values)}f", *values)


def restore_vec_from_embeddings(conn: sqlite3.Connection) -> int:
    rows = conn.execute(
        """
        SELECT DISTINCT c.id, e.embedding, e.model, e.dimensions
        FROM chunks c
        JOIN embeddings e ON e.content_hash = c.content_hash
        WHERE e.model = ? AND e.dimensions = ?
        ORDER BY c.id
        """,
        (MODEL, DIMENSIONS),
    ).fetchall()
    restored = 0
    for chunk_id, blob, model, dimensions in rows:
        conn.execute("INSERT OR REPLACE INTO vec_chunks(rowid, embedding) VALUES(?, ?)", (chunk_id, blob))
        conn.execute(
            "UPDATE chunks SET embedding_model=?, embedding_dimensions=? WHERE id=?",
            (model, dimensions, chunk_id),
        )
        restored += 1
    conn.commit()
    return restored


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    load_env()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY missing. Put it in .env or environment.")
    OpenAI, sqlite_vec = require_deps()
    client = OpenAI()
    conn = validate_database(db_path())
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(embedding float[{DIMENSIONS}])"
    )
    restored = restore_vec_from_embeddings(conn)
    if restored:
        print(f"restored_vec={restored}")
    rows = conn.execute(
        """
        SELECT c.id, c.text, c.content_hash
        FROM chunks c
        LEFT JOIN embeddings e ON e.chunk_id = c.id AND e.content_hash = c.content_hash AND e.model = ?
        WHERE e.chunk_id IS NULL
        ORDER BY c.id
        """,
        (MODEL,),
    ).fetchall()
    if args.limit:
        rows = rows[: args.limit]
    total = 0
    for idx in range(0, len(rows), args.batch_size):
        batch = rows[idx : idx + args.batch_size]
        response = client.embeddings.create(
            model=MODEL,
            input=[r[1] for r in batch],
            dimensions=DIMENSIONS,
        )
        now = datetime.now(timezone.utc).isoformat()
        for row, item in zip(batch, response.data):
            chunk_id, _text, content_hash = row
            vec = item.embedding
            if len(vec) != DIMENSIONS:
                raise RuntimeError(f"bad dimensions for chunk {chunk_id}: {len(vec)}")
            blob = pack(vec)
            conn.execute(
                """INSERT OR REPLACE INTO embeddings(chunk_id,model,dimensions,embedding,content_hash,created_at)
                VALUES(?,?,?,?,?,?)""",
                (chunk_id, MODEL, DIMENSIONS, blob, content_hash, now),
            )
            conn.execute("INSERT OR REPLACE INTO vec_chunks(rowid, embedding) VALUES(?, ?)", (chunk_id, blob))
            conn.execute(
                "UPDATE chunks SET embedding_model=?, embedding_dimensions=? WHERE id=?",
                (MODEL, DIMENSIONS, chunk_id),
            )
            total += 1
        conn.commit()
        print(f"embedded={total}/{len(rows)}")
    conn.close()


if __name__ == "__main__":
    main()
