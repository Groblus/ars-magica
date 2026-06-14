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
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(embedding float[{DIMENSIONS}])"
    )
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
