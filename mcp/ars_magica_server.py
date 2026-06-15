#!/usr/bin/env python3
"""FastMCP tools for the local Ars Magica reference database."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from fastmcp import FastMCP


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "skills" / "ars-magica-corpus-navigator" / "resources" / "ars_magica.sqlite"

mcp = FastMCP("ars-magica-reference")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    return [dict(row) for row in cursor.fetchall()]


def safe_limit(limit: int, default: int = 8, maximum: int = 50) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        value = default
    return max(1, min(maximum, value))


@mcp.tool()
def search_rules(query: str, limit: int = 8) -> list[dict[str, Any]]:
    """Search DE/5e heading-aware rule chunks with citations."""
    limit = safe_limit(limit)
    with connect() as conn:
        try:
            cursor = conn.execute(
                """
                SELECT c.section_id, b.title AS book, c.heading_path, c.line_start, c.line_end,
                       c.citation, snippet(chunks_fts, 0, '[', ']', ' ... ', 18) AS snippet
                FROM chunks_fts
                JOIN chunks c ON c.id = chunks_fts.rowid
                JOIN books b ON b.id = c.book_id
                WHERE chunks_fts MATCH ?
                ORDER BY bm25(chunks_fts)
                LIMIT ?
                """,
                (query, limit),
            )
        except sqlite3.OperationalError:
            like = f"%{query}%"
            cursor = conn.execute(
                """
                SELECT c.section_id, b.title AS book, c.heading_path, c.line_start, c.line_end,
                       c.citation, substr(c.text, 1, 420) AS snippet
                FROM chunks c
                JOIN books b ON b.id = c.book_id
                WHERE c.text LIKE ? OR c.heading_path LIKE ?
                ORDER BY c.line_start
                LIMIT ?
                """,
                (like, like, limit),
            )
        return rows(cursor)


@mcp.tool()
def get_section(section_id: str) -> dict[str, Any]:
    """Return one indexed section plus its chunk text."""
    with connect() as conn:
        section = conn.execute(
            """
            SELECT s.id, b.title AS book, b.path, s.heading, s.heading_level, s.heading_path,
                   s.line_start, s.line_end
            FROM sections s
            JOIN books b ON b.id = s.book_id
            WHERE s.id = ?
            """,
            (section_id,),
        ).fetchone()
        if section is None:
            return {"error": "section not found", "section_id": section_id}
        chunk_rows = conn.execute(
            """
            SELECT chunk_index, text, citation
            FROM chunks
            WHERE section_id = ?
            ORDER BY chunk_index
            """,
            (section_id,),
        ).fetchall()
        data = dict(section)
        data["chunks"] = [dict(row) for row in chunk_rows]
        return data


@mcp.tool()
def list_book_toc(book_query: str = "", limit: int = 50) -> list[dict[str, Any]]:
    """List top-level table-of-contents sections for matching books."""
    limit = safe_limit(limit, default=50, maximum=200)
    like = f"%{book_query}%"
    with connect() as conn:
        return rows(
            conn.execute(
                """
                SELECT b.title AS book, b.path, s.id AS section_id, s.heading, s.heading_level,
                       s.heading_path, s.line_start, s.line_end
                FROM sections s
                JOIN books b ON b.id = s.book_id
                WHERE (? = '' OR b.title LIKE ? OR b.path LIKE ?)
                  AND s.heading_level <= 2
                ORDER BY b.priority, b.title, s.line_start
                LIMIT ?
                """,
                (book_query, like, like, limit),
            )
        )


@mcp.tool()
def find_spell(
    query: str = "",
    technique: str = "",
    form: str = "",
    max_level: int | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Find Definitive Edition spell entries by name, Art, and level."""
    limit = safe_limit(limit, default=20)
    clauses = ["1 = 1"]
    params: list[Any] = []
    if query:
        clauses.append("(name LIKE ? OR description LIKE ?)")
        params.extend([f"%{query}%", f"%{query}%"])
    if technique:
        clauses.append("technique = ?")
        params.append(technique)
    if form:
        clauses.append("form = ?")
        params.append(form)
    if max_level is not None:
        clauses.append("(spell_level IS NOT NULL AND spell_level <= ?)")
        params.append(max_level)
    params.append(limit)
    with connect() as conn:
        return rows(
            conn.execute(
                f"""
                SELECT name, technique, form, spell_level, level_label, spell_range, duration,
                       target, ritual, parameter_line, design_notes, description, citation
                FROM core_spells
                WHERE {' AND '.join(clauses)}
                ORDER BY technique, form, spell_level, name
                LIMIT ?
                """,
                params,
            )
        )


def lookup_named(table: str, name: str, limit: int = 20) -> list[dict[str, Any]]:
    limit = safe_limit(limit, default=20)
    with connect() as conn:
        return rows(
            conn.execute(
                f"""
                SELECT name, magnitude, categories_json, meta, heading_path, description, citation
                FROM {table}
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY name
                LIMIT ?
                """,
                (f"%{name}%", f"%{name}%", limit),
            )
        )


@mcp.tool()
def lookup_virtue(name: str, limit: int = 20) -> list[dict[str, Any]]:
    """Lookup Definitive Edition virtues with citation."""
    return lookup_named("core_virtues", name, limit)


@mcp.tool()
def lookup_flaw(name: str, limit: int = 20) -> list[dict[str, Any]]:
    """Lookup Definitive Edition flaws with citation."""
    return lookup_named("core_flaws", name, limit)


@mcp.tool()
def lookup_ability(name: str, limit: int = 20) -> list[dict[str, Any]]:
    """Lookup Definitive Edition abilities with citation."""
    limit = safe_limit(limit, default=20)
    with connect() as conn:
        return rows(
            conn.execute(
                """
                SELECT name, is_marked, ability_type, specialties, heading_path, description, citation
                FROM core_abilities
                WHERE name LIKE ? OR description LIKE ? OR body LIKE ?
                ORDER BY name
                LIMIT ?
                """,
                (f"%{name}%", f"%{name}%", f"%{name}%", limit),
            )
        )


@mcp.tool()
def lookup_covenant_option(query: str, kind: str = "", limit: int = 20) -> list[dict[str, Any]]:
    """Lookup covenant boons/hooks from the 5e Covenants extraction."""
    limit = safe_limit(limit, default=20)
    clauses = ["(name LIKE ? OR summary LIKE ? OR category LIKE ?)"]
    params: list[Any] = [f"%{query}%", f"%{query}%", f"%{query}%"]
    if kind:
        clauses.append("kind = ?")
        params.append(kind)
    params.append(limit)
    with connect() as conn:
        return rows(
            conn.execute(
                f"""
                SELECT name, kind, magnitude, category, summary, citation
                FROM covenant_boons_hooks
                WHERE {' AND '.join(clauses)}
                ORDER BY kind, category, name
                LIMIT ?
                """,
                params,
            )
        )


if __name__ == "__main__":
    mcp.run()
