#!/usr/bin/env python3
"""Build Ars Magica DE/5e navigator resources and SQLite FTS database."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
RESOURCES = SKILL_DIR / "resources"
REFERENCES = SKILL_DIR / "references"
TOC_DIR = REFERENCES / "toc"
DB_PATH = RESOURCES / "ars_magica.sqlite"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CHAPTER_RE = re.compile(
    r"^(chapter\s+([0-9]+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen)\s*:?\s*.*|introduction\b.*|appendix(?:\s+[a-z])?\s*:?\s*.*|appendices\b.*|reference guide\b.*)$",
    re.I,
)

PRIORITIES = {
    "Ars Magica - Definitive Edition (Core Rules).md": 0,
    "Ars Magica 5e - Covenants.md": 1,
    "Ars Magica 5e - Houses of Hermes - True Lineages.md": 1,
    "Ars Magica 5e - Houses of Hermes - Societates.md": 1,
    "Ars Magica 5e - Houses of Hermes - Mystery Cults.md": 2,
    "Ars Magica 5e - Realms of Power - Magic.md": 2,
    "Ars Magica 5e - Lords of Men.md": 2,
    "Ars Magica 5e - The Church.md": 2,
}


@dataclass
class Heading:
    id: str
    slug: str
    title: str
    level: int
    line_start: int
    line_end: int
    heading_path: list[str]
    parent_id: str | None
    ordinal: int
    section_type: str


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value.lower(), flags=re.UNICODE)
    return re.sub(r"[-\s]+", "-", value).strip("-") or "section"


def allowed_paths() -> list[Path]:
    reviewed = REPO_ROOT / "reviewed"
    paths = [reviewed / "Ars Magica - Definitive Edition (Core Rules).md"]
    paths.extend(sorted(reviewed.glob("Ars Magica 5e - *.md")))
    return [p for p in paths if p.exists()]


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def title_from(path: Path, raw: list[dict]) -> str:
    ignored = {"credits", "contents", "table of contents"}
    for item in raw:
        title = item["title"].strip()
        if item["level"] == 1 and title.lower() not in ignored:
            if not title.lower().startswith("chapter "):
                return title
            break
    return path.stem


def parse_headings(path: Path, lines: list[str]) -> tuple[str, list[Heading]]:
    book_slug = slugify(path.stem)
    raw: list[dict] = []
    for idx, line in enumerate(lines, 1):
        match = HEADING_RE.match(line)
        if match:
            raw.append(
                {
                    "title": match.group(2).strip(),
                    "level": len(match.group(1)),
                    "line_start": idx,
                }
            )

    for i, item in enumerate(raw):
        line_end = len(lines)
        for nxt in raw[i + 1 :]:
            if nxt["level"] <= item["level"]:
                line_end = nxt["line_start"] - 1
                break
        item["line_end"] = line_end

    stack: list[dict] = []
    headings: list[Heading] = []
    for ordinal, item in enumerate(raw, 1):
        stack = [h for h in stack if h["level"] < item["level"]]
        parent = stack[-1] if stack else None
        stack.append(item)
        heading_path = [h["title"] for h in stack]
        section_type = "chapter" if CHAPTER_RE.match(item["title"]) else "section"
        hid = f"{book_slug}:{item['line_start']}"
        headings.append(
            Heading(
                id=hid,
                slug=slugify(item["title"]),
                title=item["title"],
                level=item["level"],
                line_start=item["line_start"],
                line_end=item["line_end"],
                heading_path=heading_path,
                parent_id=f"{book_slug}:{parent['line_start']}" if parent else None,
                ordinal=ordinal,
                section_type=section_type,
            )
        )
    return title_from(path, raw), headings


def chunk_section(path: Path, lines: list[str], heading: Heading, max_chars: int) -> list[dict]:
    start = heading.line_start
    end = heading.line_end
    chunk_lines = lines[start - 1 : end]
    text = "\n".join(chunk_lines).strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [
            {
                "line_start": start,
                "line_end": end,
                "text": text,
            }
        ]

    chunks: list[dict] = []
    current: list[str] = []
    current_start = start
    for offset, line in enumerate(chunk_lines, start):
        if current and sum(len(x) + 1 for x in current) + len(line) > max_chars:
            chunks.append(
                {
                    "line_start": current_start,
                    "line_end": offset - 1,
                    "text": "\n".join(current).strip(),
                }
            )
            current = []
            current_start = offset
        current.append(line)
    if current:
        chunks.append(
            {
                "line_start": current_start,
                "line_end": end,
                "text": "\n".join(current).strip(),
            }
        )
    return chunks


def build_records(max_chars: int) -> tuple[list[dict], list[dict]]:
    books: list[dict] = []
    chunks: list[dict] = []
    for book_id, path in enumerate(allowed_paths(), 1):
        rel = path.relative_to(REPO_ROOT).as_posix()
        lines = read_lines(path)
        title, headings = parse_headings(path, lines)
        edition = "DE" if "Definitive Edition" in path.name else "5e"
        priority = PRIORITIES.get(path.name, 3)
        book = {
            "id": book_id,
            "path": rel,
            "title": title,
            "edition": edition,
            "priority": priority,
            "line_count": len(lines),
            "sha256": file_sha(path),
            "headings": [h.__dict__ for h in headings],
            "chapters": [h.__dict__ for h in headings if h.section_type == "chapter"],
        }
        books.append(book)

        for h in headings:
            if h.level > 4:
                continue
            for chunk_index, c in enumerate(chunk_section(path, lines, h, max_chars), 1):
                content_hash = hashlib.sha256(c["text"].encode("utf-8")).hexdigest()
                chunks.append(
                    {
                        "book_id": book_id,
                        "section_id": h.id,
                        "chunk_index": chunk_index,
                        "text": c["text"],
                        "line_start": c["line_start"],
                        "line_end": c["line_end"],
                        "heading_path": " > ".join(h.heading_path),
                        "citation": f"{rel}:{c['line_start']}-{c['line_end']}",
                        "content_hash": content_hash,
                    }
                )
    return books, chunks


def write_json(books: list[dict], chunks: list[dict]) -> None:
    RESOURCES.mkdir(parents=True, exist_ok=True)
    TOC_DIR.mkdir(parents=True, exist_ok=True)
    allowed = [
        {
            "path": b["path"],
            "title": b["title"],
            "edition": b["edition"],
            "priority": b["priority"],
            "line_count": b["line_count"],
            "sha256": b["sha256"],
        }
        for b in books
    ]
    (RESOURCES / "allowed-books.json").write_text(json.dumps(allowed, indent=2, ensure_ascii=False) + "\n")
    (RESOURCES / "heading-index.json").write_text(json.dumps({"books": books}, indent=2, ensure_ascii=False) + "\n")
    (RESOURCES / "chunks.json").write_text(json.dumps({"chunks": chunks}, indent=2, ensure_ascii=False) + "\n")


def write_tocs(books: list[dict]) -> None:
    index_lines = ["# Ars Magica DE/5e Table of Contents", ""]
    for b in books:
        toc_name = slugify(Path(b["path"]).stem) + ".md"
        index_lines.append(f"- [{b['title']}](toc/{toc_name})")
        lines = [f"# {b['title']}", "", f"- Source: `{b['path']}`", f"- Edition: `{b['edition']}`", ""]
        for h in b["headings"]:
            indent = "  " * max(0, h["level"] - 1)
            label = " / ".join(h["heading_path"])
            lines.append(f"{indent}- `{h['line_start']}-{h['line_end']}` [{h['title']}](../../../{b['path']}#L{h['line_start']})")
            if h["level"] == 1 and label != h["title"]:
                lines[-1] += f" _{label}_"
        (TOC_DIR / toc_name).write_text("\n".join(lines) + "\n")
    (REFERENCES / "toc.md").write_text("\n".join(index_lines) + "\n")


def build_sqlite(books: list[dict], chunks: list[dict]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE books (
          id INTEGER PRIMARY KEY,
          path TEXT NOT NULL UNIQUE,
          title TEXT NOT NULL,
          edition TEXT NOT NULL CHECK (edition IN ('DE','5e')),
          priority INTEGER NOT NULL,
          line_count INTEGER NOT NULL,
          sha256 TEXT NOT NULL
        );
        CREATE TABLE sections (
          id TEXT PRIMARY KEY,
          book_id INTEGER NOT NULL REFERENCES books(id),
          parent_id TEXT REFERENCES sections(id),
          heading TEXT NOT NULL,
          heading_level INTEGER NOT NULL,
          heading_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          ordinal INTEGER NOT NULL,
          section_type TEXT NOT NULL,
          UNIQUE(book_id, line_start)
        );
        CREATE TABLE chunks (
          id INTEGER PRIMARY KEY,
          book_id INTEGER NOT NULL REFERENCES books(id),
          section_id TEXT NOT NULL REFERENCES sections(id),
          chunk_index INTEGER NOT NULL,
          text TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          heading_path TEXT NOT NULL,
          citation TEXT NOT NULL,
          content_hash TEXT NOT NULL,
          embedding_model TEXT,
          embedding_dimensions INTEGER,
          UNIQUE(section_id, chunk_index)
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
          text,
          title,
          heading_path,
          citation UNINDEXED,
          tokenize='unicode61 remove_diacritics 2'
        );
        CREATE TABLE embeddings (
          chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id),
          model TEXT NOT NULL,
          dimensions INTEGER NOT NULL,
          embedding BLOB NOT NULL,
          content_hash TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """
    )
    for b in books:
        conn.execute(
            "INSERT INTO books(id,path,title,edition,priority,line_count,sha256) VALUES(?,?,?,?,?,?,?)",
            (b["id"], b["path"], b["title"], b["edition"], b["priority"], b["line_count"], b["sha256"]),
        )
        for h in b["headings"]:
            conn.execute(
                """INSERT INTO sections(id,book_id,parent_id,heading,heading_level,heading_path,line_start,line_end,ordinal,section_type)
                VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    h["id"],
                    b["id"],
                    h["parent_id"],
                    h["title"],
                    h["level"],
                    " > ".join(h["heading_path"]),
                    h["line_start"],
                    h["line_end"],
                    h["ordinal"],
                    h["section_type"],
                ),
            )
    title_by_id = {b["id"]: b["title"] for b in books}
    for c in chunks:
        cur = conn.execute(
            """INSERT INTO chunks(book_id,section_id,chunk_index,text,line_start,line_end,heading_path,citation,content_hash)
            VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                c["book_id"],
                c["section_id"],
                c["chunk_index"],
                c["text"],
                c["line_start"],
                c["line_end"],
                c["heading_path"],
                c["citation"],
                c["content_hash"],
            ),
        )
        rowid = cur.lastrowid
        conn.execute(
            "INSERT INTO chunks_fts(rowid,text,title,heading_path,citation) VALUES(?,?,?,?,?)",
            (rowid, c["text"], title_by_id[c["book_id"]], c["heading_path"], c["citation"]),
        )
    conn.commit()
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-chars", type=int, default=18000)
    args = parser.parse_args()
    books, chunks = build_records(args.max_chars)
    write_json(books, chunks)
    write_tocs(books)
    build_sqlite(books, chunks)
    print(f"books={len(books)} chunks={len(chunks)} db={DB_PATH}")


if __name__ == "__main__":
    main()
