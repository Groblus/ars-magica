#!/usr/bin/env python3
"""Search Ars Magica navigator SQLite database."""

from __future__ import annotations

import argparse
import os
import sqlite3
import struct
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
DB_PATH = SKILL_DIR / "resources" / "ars_magica.sqlite"
MODEL = "text-embedding-3-large"
DIMENSIONS = 3072


def load_env() -> None:
    env = REPO_ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def pack(values: list[float]) -> bytes:
    return struct.pack(f"{len(values)}f", *values)


def search_fts(conn: sqlite3.Connection, query: str, limit: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT c.id, b.title, b.edition, b.priority, c.heading_path, c.citation,
               snippet(chunks_fts, 0, '[', ']', ' ... ', 18) AS excerpt,
               bm25(chunks_fts) AS score
        FROM chunks_fts
        JOIN chunks c ON c.id = chunks_fts.rowid
        JOIN books b ON b.id = c.book_id
        WHERE chunks_fts MATCH ?
        ORDER BY b.priority ASC, score ASC
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()


def search_like(conn: sqlite3.Connection, query: str, limit: int) -> list[sqlite3.Row]:
    pattern = f"%{query}%"
    return conn.execute(
        """
        SELECT c.id, b.title, b.edition, b.priority, c.heading_path, c.citation,
               substr(replace(c.text, char(10), ' '), 1, 260) AS excerpt,
               999.0 AS score
        FROM chunks c
        JOIN books b ON b.id = c.book_id
        WHERE c.text LIKE ? OR c.heading_path LIKE ? OR b.title LIKE ?
        ORDER BY b.priority ASC, c.line_start ASC
        LIMIT ?
        """,
        (pattern, pattern, pattern, limit),
    ).fetchall()


def query_embedding(query: str) -> bytes:
    load_env()
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY missing for vector search")
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError("openai package missing; use .venv or install dependency") from exc
    client = OpenAI()
    response = client.embeddings.create(model=MODEL, input=query, dimensions=DIMENSIONS)
    embedding = response.data[0].embedding
    if len(embedding) != DIMENSIONS:
        raise RuntimeError(f"expected {DIMENSIONS} dimensions, got {len(embedding)}")
    return pack(embedding)


def enable_vec(conn: sqlite3.Connection) -> None:
    try:
        import sqlite_vec
    except Exception as exc:
        raise RuntimeError("sqlite_vec package missing; use .venv or install sqlite-vec") from exc
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)


def search_vector(conn: sqlite3.Connection, query: str, limit: int) -> list[sqlite3.Row]:
    enable_vec(conn)
    vector = query_embedding(query)
    return conn.execute(
        """
        SELECT c.id, b.title, b.edition, b.priority, c.heading_path, c.citation,
               substr(replace(c.text, char(10), ' '), 1, 260) AS excerpt,
               v.distance AS score
        FROM vec_chunks v
        JOIN chunks c ON c.id = v.rowid
        JOIN books b ON b.id = c.book_id
        WHERE v.embedding MATCH ? AND k = ?
        ORDER BY b.priority ASC, v.distance ASC
        """,
        (vector, limit),
    ).fetchall()


def search_hybrid(conn: sqlite3.Connection, query: str, limit: int) -> list[sqlite3.Row]:
    fts = search_fts(conn, query, limit * 2)
    try:
        vec = search_vector(conn, query, limit * 2)
    except RuntimeError as exc:
        print(f"vector unavailable: {exc}", file=sys.stderr)
        vec = []
    scores: dict[int, float] = {}
    rows: dict[int, sqlite3.Row] = {}
    for rank, row in enumerate(fts, 1):
        scores[row["id"]] = scores.get(row["id"], 0.0) + 1.0 / (60 + rank)
        rows[row["id"]] = row
    for rank, row in enumerate(vec, 1):
        scores[row["id"]] = scores.get(row["id"], 0.0) + 1.0 / (60 + rank)
        rows[row["id"]] = row
    ranked = sorted(rows.values(), key=lambda r: (-scores[r["id"]], r["priority"], r["score"]))
    return ranked[:limit]


def print_rows(rows: list[sqlite3.Row]) -> None:
    for row in rows:
        print(f"- {row['title']} ({row['edition']})")
        print(f"  heading: {row['heading_path']}")
        print(f"  citation: {row['citation']}")
        print(f"  score: {row['score']}")
        print(f"  excerpt: {row['excerpt']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--fts", action="store_true")
    parser.add_argument("--vector", action="store_true")
    parser.add_argument("--hybrid", action="store_true")
    args = parser.parse_args()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if args.vector:
        rows = search_vector(conn, args.query, args.limit)
    elif args.hybrid:
        rows = search_hybrid(conn, args.query, args.limit)
    else:
        try:
            rows = search_fts(conn, args.query, args.limit)
        except sqlite3.OperationalError:
            rows = []
        if not rows:
            rows = search_like(conn, args.query, args.limit)
    print_rows(rows)


if __name__ == "__main__":
    main()
