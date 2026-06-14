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
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
RESOURCES = SKILL_DIR / "resources"
REFERENCES = SKILL_DIR / "references"
TOC_DIR = REFERENCES / "toc"
DB_PATH = RESOURCES / "ars_magica.sqlite"
DOCS_DATA = REPO_ROOT / "docs" / "data"
CORE_PATH = REPO_ROOT / "reviewed" / "Ars Magica - Definitive Edition (Core Rules).md"

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


@dataclass
class CoreExtraction:
    virtues: list[dict[str, Any]]
    flaws: list[dict[str, Any]]
    abilities: list[dict[str, Any]]
    spells: list[dict[str, Any]]


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


def make_heading_map(headings: list[Heading]) -> dict[str, Heading]:
    return {h.id: h for h in headings}


def descendants_of(headings: list[Heading], parent: Heading) -> list[Heading]:
    return [h for h in headings if parent.line_start < h.line_start <= parent.line_end]


def body_lines(lines: list[str], heading: Heading) -> list[str]:
    return lines[heading.line_start : heading.line_end]


def clean_htmlish(text: str) -> str:
    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    return text.strip()


def join_body(lines: list[str]) -> str:
    text = clean_htmlish("\n".join(lines))
    return text.strip()


def parse_meta_line(line: str) -> tuple[str | None, list[str], str]:
    cleaned = clean_htmlish(line).strip()
    cleaned = cleaned.strip("*").strip()
    cleaned = cleaned.replace(". ", ", ").replace("*", "")
    parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    magnitude = parts[0] if parts else None
    return magnitude, parts[1:], cleaned


def parse_virtue_or_flaw_entries(
    kind: str,
    lines: list[str],
    headings: list[Heading],
    chapter_title: str,
    section_title: str,
) -> list[dict[str, Any]]:
    chapter = next(h for h in headings if h.title == chapter_title)
    section = next(h for h in headings if h.title == section_title and chapter.line_start <= h.line_start <= chapter.line_end)
    entries: list[dict[str, Any]] = []
    for heading in descendants_of(headings, section):
        if heading.level != 4:
            continue
        entry_lines = body_lines(lines, heading)
        meta_line = entry_lines[0].strip() if entry_lines else ""
        magnitude, categories, meta = parse_meta_line(meta_line)
        description = join_body(entry_lines[1:]).strip()
        entries.append(
            {
                "id": slugify(f"{kind}-{heading.title}-{heading.line_start}"),
                "name": heading.title,
                "kind": kind,
                "magnitude": magnitude,
                "categories": categories,
                "meta": meta,
                "heading_path": " > ".join(heading.heading_path),
                "description": description,
                "source_path": CORE_PATH.relative_to(REPO_ROOT).as_posix(),
                "line_start": heading.line_start,
                "line_end": heading.line_end,
                "citation": f"{CORE_PATH.relative_to(REPO_ROOT).as_posix()}:{heading.line_start}-{heading.line_end}",
            }
        )
    return entries


def parse_abilities(lines: list[str], headings: list[Heading]) -> list[dict[str, Any]]:
    chapter = next(h for h in headings if h.title == "Chapter 5: Abilities")
    section = next(h for h in headings if h.title == "Ability List" and chapter.line_start <= h.line_start <= chapter.line_end)
    entries: list[dict[str, Any]] = []
    for heading in descendants_of(headings, section):
        if heading.level != 4:
            continue
        raw = join_body(body_lines(lines, heading))
        ability_type = None
        type_match = re.search(r"\((General|Academic|Arcane|Martial|Supernatural)\)\s*$", raw, re.MULTILINE)
        if type_match:
            ability_type = type_match.group(1)
        specialties = None
        specialties_match = re.search(r"\*Specialt(?:ies|y)\*:? ?(.+?)(?:\((?:General|Academic|Arcane|Martial|Supernatural)\))?\s*$", raw, re.S | re.I)
        if specialties_match:
            specialties = " ".join(specialties_match.group(1).split())
        description = raw
        if specialties_match:
            description = raw[: specialties_match.start()].strip()
        if type_match and description.endswith(type_match.group(0)):
            description = description[: -len(type_match.group(0))].strip()
        entries.append(
            {
                "id": slugify(f"ability-{heading.title}-{heading.line_start}"),
                "name": heading.title,
                "is_marked": "*" in heading.title,
                "ability_type": ability_type,
                "specialties": specialties,
                "heading_path": " > ".join(heading.heading_path),
                "description": description,
                "body": raw,
                "source_path": CORE_PATH.relative_to(REPO_ROOT).as_posix(),
                "line_start": heading.line_start,
                "line_end": heading.line_end,
                "citation": f"{CORE_PATH.relative_to(REPO_ROOT).as_posix()}:{heading.line_start}-{heading.line_end}",
            }
        )
    return entries


def nearest_spell_group(heading: Heading) -> tuple[str | None, int | None]:
    for part in reversed(heading.heading_path):
        if re.fullmatch(r"LEVEL\s+\d+", part):
            return part, int(part.split()[1])
        if part == "GENERAL":
            return part, None
    return None, None


def parse_spell_parameters(line: str) -> dict[str, Any]:
    cleaned = clean_htmlish(line).replace("\n", " ").strip()
    result: dict[str, Any] = {"parameter_line": cleaned, "range": None, "duration": None, "target": None, "ritual": False}
    if "R:" not in cleaned:
        return result
    for label, key in [("R:", "range"), ("D:", "duration"), ("T:", "target")]:
        match = re.search(rf"{re.escape(label)}\s*([^,]+)", cleaned)
        if match:
            result[key] = match.group(1).strip()
    result["ritual"] = "Ritual" in cleaned
    return result


def find_spell_parameter_index(entry_lines: list[str]) -> int | None:
    for idx, line in enumerate(entry_lines):
        cleaned = clean_htmlish(line).replace("\n", " ").strip()
        if not cleaned:
            continue
        if cleaned.startswith("R:"):
            return idx
    return None


def parse_spells(lines: list[str], headings: list[Heading]) -> list[dict[str, Any]]:
    chapter = next(h for h in headings if h.title == "Chapter 9: Spells")
    spell_sections = [
        h
        for h in descendants_of(headings, chapter)
        if h.title.endswith(" Spells") and re.fullmatch(r"(Creo|Intellego|Muto|Perdo|Rego) [A-Za-z]+ Spells", h.title)
    ]
    entries: list[dict[str, Any]] = []
    for section in spell_sections:
        technique, form, _ = section.title.split(" ", 2)
        for heading in descendants_of(headings, section):
            if heading.id == section.id:
                continue
            if heading.title == "GENERAL" or re.fullmatch(r"LEVEL\s+\d+", heading.title):
                continue
            if re.match(r"^(Creo|Intellego|Muto|Perdo|Rego) [A-Za-z]+ Spells$", heading.title):
                continue
            entry_lines = body_lines(lines, heading)
            if not entry_lines:
                continue
            param_index = find_spell_parameter_index(entry_lines)
            if param_index is None:
                continue
            params = parse_spell_parameters(entry_lines[param_index])
            if not params["parameter_line"].startswith("R:"):
                continue
            idx = param_index + 1
            requisites = None
            if idx < len(entry_lines) and clean_htmlish(entry_lines[idx]).startswith("Req:"):
                requisites = clean_htmlish(entry_lines[idx])[4:].strip()
                idx += 1
            design_notes = None
            tail = [line for line in entry_lines[idx:] if line.strip()]
            if tail and re.fullmatch(r"\(.+\)", clean_htmlish(tail[-1]), re.S):
                design_notes = clean_htmlish(tail[-1]).strip()[1:-1].strip()
                tail = tail[:-1]
            description = join_body(tail)
            group_title, spell_level = nearest_spell_group(heading)
            entries.append(
                {
                    "id": slugify(f"spell-{technique}-{form}-{heading.title}-{heading.line_start}"),
                    "name": heading.title,
                    "technique": technique,
                    "form": form,
                    "spell_level": spell_level,
                    "level_label": group_title,
                    "range": params["range"],
                    "duration": params["duration"],
                    "target": params["target"],
                    "ritual": params["ritual"],
                    "requisites": requisites,
                    "parameter_line": params["parameter_line"],
                    "design_notes": design_notes,
                    "heading_path": " > ".join(heading.heading_path),
                    "description": description,
                    "source_path": CORE_PATH.relative_to(REPO_ROOT).as_posix(),
                    "line_start": heading.line_start,
                    "line_end": heading.line_end,
                    "citation": f"{CORE_PATH.relative_to(REPO_ROOT).as_posix()}:{heading.line_start}-{heading.line_end}",
                }
            )
    return entries


def extract_core_data(core_book: dict[str, Any]) -> CoreExtraction:
    lines = read_lines(REPO_ROOT / core_book["path"])
    headings = [Heading(**heading) for heading in core_book["headings"]]
    return CoreExtraction(
        virtues=parse_virtue_or_flaw_entries("virtue", lines, headings, "Chapter 4: Virtues and Flaws", "Virtues"),
        flaws=parse_virtue_or_flaw_entries("flaw", lines, headings, "Chapter 4: Virtues and Flaws", "Flaws"),
        abilities=parse_abilities(lines, headings),
        spells=parse_spells(lines, headings),
    )


def build_records(max_chars: int) -> tuple[list[dict], list[dict], CoreExtraction]:
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
    core_book = next(b for b in books if b["path"] == CORE_PATH.relative_to(REPO_ROOT).as_posix())
    return books, chunks, extract_core_data(core_book)


def write_json(books: list[dict], chunks: list[dict], core_data: CoreExtraction, export_chunks: bool) -> None:
    RESOURCES.mkdir(parents=True, exist_ok=True)
    TOC_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DATA.mkdir(parents=True, exist_ok=True)
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
    chunks_path = RESOURCES / "chunks.json"
    if export_chunks:
        chunks_path.write_text(json.dumps({"chunks": chunks}, indent=2, ensure_ascii=False) + "\n")
    elif chunks_path.exists():
        chunks_path.unlink()
    library_payload = {
        "books": [
            {
                "id": b["id"],
                "path": b["path"],
                "title": b["title"],
                "edition": b["edition"],
                "priority": b["priority"],
                "line_count": b["line_count"],
                "sha256": b["sha256"],
                "chapter_count": len(b["chapters"]),
                "heading_count": len(b["headings"]),
                "headings": b["headings"],
                "chapters": b["chapters"],
            }
            for b in books
        ],
        "summary": {
            "book_count": len(books),
            "chunk_count": len(chunks),
            "de_count": sum(1 for b in books if b["edition"] == "DE"),
            "five_e_count": sum(1 for b in books if b["edition"] == "5e"),
        },
    }
    core_payload = {
        "book": {
            "path": CORE_PATH.relative_to(REPO_ROOT).as_posix(),
            "title": next(b["title"] for b in books if b["path"] == CORE_PATH.relative_to(REPO_ROOT).as_posix()),
            "edition": "DE",
        },
        "summary": {
            "virtue_count": len(core_data.virtues),
            "flaw_count": len(core_data.flaws),
            "ability_count": len(core_data.abilities),
            "spell_count": len(core_data.spells),
        },
        "virtues": core_data.virtues,
        "flaws": core_data.flaws,
        "abilities": core_data.abilities,
        "spells": core_data.spells,
    }
    (DOCS_DATA / "library.json").write_text(json.dumps(library_payload, indent=2, ensure_ascii=False) + "\n")
    (DOCS_DATA / "core-data.json").write_text(json.dumps(core_payload, indent=2, ensure_ascii=False) + "\n")


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


def build_sqlite(books: list[dict], chunks: list[dict], core_data: CoreExtraction) -> None:
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
        CREATE TABLE core_virtues (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          magnitude TEXT,
          categories_json TEXT NOT NULL,
          meta TEXT NOT NULL,
          heading_path TEXT NOT NULL,
          description TEXT NOT NULL,
          source_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          citation TEXT NOT NULL
        );
        CREATE TABLE core_flaws (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          magnitude TEXT,
          categories_json TEXT NOT NULL,
          meta TEXT NOT NULL,
          heading_path TEXT NOT NULL,
          description TEXT NOT NULL,
          source_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          citation TEXT NOT NULL
        );
        CREATE TABLE core_abilities (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          is_marked INTEGER NOT NULL,
          ability_type TEXT,
          specialties TEXT,
          heading_path TEXT NOT NULL,
          description TEXT NOT NULL,
          body TEXT NOT NULL,
          source_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          citation TEXT NOT NULL
        );
        CREATE TABLE core_spells (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          technique TEXT NOT NULL,
          form TEXT NOT NULL,
          spell_level INTEGER,
          level_label TEXT,
          spell_range TEXT,
          duration TEXT,
          target TEXT,
          ritual INTEGER NOT NULL,
          requisites TEXT,
          parameter_line TEXT NOT NULL,
          design_notes TEXT,
          heading_path TEXT NOT NULL,
          description TEXT NOT NULL,
          source_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          citation TEXT NOT NULL
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
    for row in core_data.virtues:
        conn.execute(
            """INSERT INTO core_virtues(id,name,magnitude,categories_json,meta,heading_path,description,source_path,line_start,line_end,citation)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["name"],
                row["magnitude"],
                json.dumps(row["categories"], ensure_ascii=False),
                row["meta"],
                row["heading_path"],
                row["description"],
                row["source_path"],
                row["line_start"],
                row["line_end"],
                row["citation"],
            ),
        )
    for row in core_data.flaws:
        conn.execute(
            """INSERT INTO core_flaws(id,name,magnitude,categories_json,meta,heading_path,description,source_path,line_start,line_end,citation)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["name"],
                row["magnitude"],
                json.dumps(row["categories"], ensure_ascii=False),
                row["meta"],
                row["heading_path"],
                row["description"],
                row["source_path"],
                row["line_start"],
                row["line_end"],
                row["citation"],
            ),
        )
    for row in core_data.abilities:
        conn.execute(
            """INSERT INTO core_abilities(id,name,is_marked,ability_type,specialties,heading_path,description,body,source_path,line_start,line_end,citation)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["name"],
                int(row["is_marked"]),
                row["ability_type"],
                row["specialties"],
                row["heading_path"],
                row["description"],
                row["body"],
                row["source_path"],
                row["line_start"],
                row["line_end"],
                row["citation"],
            ),
        )
    for row in core_data.spells:
        conn.execute(
            """INSERT INTO core_spells(id,name,technique,form,spell_level,level_label,spell_range,duration,target,ritual,requisites,parameter_line,design_notes,heading_path,description,source_path,line_start,line_end,citation)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["name"],
                row["technique"],
                row["form"],
                row["spell_level"],
                row["level_label"],
                row["range"],
                row["duration"],
                row["target"],
                int(row["ritual"]),
                row["requisites"],
                row["parameter_line"],
                row["design_notes"],
                row["heading_path"],
                row["description"],
                row["source_path"],
                row["line_start"],
                row["line_end"],
                row["citation"],
            ),
        )
    conn.commit()
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-chars", type=int, default=18000)
    parser.add_argument("--export-chunks-json", action="store_true")
    args = parser.parse_args()
    books, chunks, core_data = build_records(args.max_chars)
    write_json(books, chunks, core_data, args.export_chunks_json)
    write_tocs(books)
    build_sqlite(books, chunks, core_data)
    print(
        " ".join(
            [
                f"books={len(books)}",
                f"chunks={len(chunks)}",
                f"virtues={len(core_data.virtues)}",
                f"flaws={len(core_data.flaws)}",
                f"abilities={len(core_data.abilities)}",
                f"spells={len(core_data.spells)}",
                f"db={DB_PATH}",
            ]
        )
    )


if __name__ == "__main__":
    main()
