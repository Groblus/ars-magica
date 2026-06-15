#!/usr/bin/env python3
"""Build Ars Magica DE/5e navigator resources and SQLite FTS database."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
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
    spell_guidelines: list[dict[str, Any]]
    lab_activities: list[dict[str, Any]]
    combat_tables: list[dict[str, Any]]
    covenant_boons_hooks: list[dict[str, Any]]


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


def first_paragraph(text: str, max_chars: int = 520) -> str:
    text = " ".join(text.strip().split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rsplit(" ", 1)[0] + "..."


def parse_markdown_table(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells:
            rows.append(cells)
    return rows


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


def parse_spell_guidelines(lines: list[str], headings: list[Heading]) -> list[dict[str, Any]]:
    chapter = next(h for h in headings if h.title == "Chapter 9: Spells")
    entries: list[dict[str, Any]] = []
    for heading in descendants_of(headings, chapter):
        if heading.level != 3 or not heading.title.endswith("Guidelines"):
            continue
        match = re.match(r"^(Creo|Intellego|Muto|Perdo|Rego)\s+([A-Za-z]+)\s+Guidelines$", heading.title)
        if not match:
            continue
        technique, form = match.groups()
        for row in parse_markdown_table(body_lines(lines, heading)):
            if len(row) < 2 or row[0].lower() == "level":
                continue
            effects = [part.strip(" •") for part in clean_htmlish(row[1]).split("\n") if part.strip(" •")]
            for effect_index, effect in enumerate(effects, 1):
                entries.append(
                    {
                        "id": slugify(f"guideline-{technique}-{form}-{row[0]}-{effect_index}-{heading.line_start}"),
                        "name": f"{technique} {form} {row[0]}",
                        "technique": technique,
                        "form": form,
                        "level": row[0],
                        "guideline": effect,
                        "heading_path": " > ".join(heading.heading_path),
                        "source_path": CORE_PATH.relative_to(REPO_ROOT).as_posix(),
                        "line_start": heading.line_start,
                        "line_end": heading.line_end,
                        "citation": f"{CORE_PATH.relative_to(REPO_ROOT).as_posix()}:{heading.line_start}-{heading.line_end}",
                    }
                )
    return entries


def parse_lab_activities(lines: list[str], headings: list[Heading]) -> list[dict[str, Any]]:
    chapter = next(h for h in headings if h.title == "Chapter 8: Laboratory")
    entries: list[dict[str, Any]] = []
    for heading in descendants_of(headings, chapter):
        if heading.level not in {3, 4}:
            continue
        if heading.title in {"Example: Inventing Spells", "Enchanted Item Example"}:
            continue
        text = join_body(body_lines(lines, heading))
        formulae = re.findall(r"\*\*([^*\n]*(?:TOTAL|LIMIT|LEVELS|CHARGES|ROLL|FACTOR|VIS)[^*\n]*):?\s*([^*]+?)\*\*", text)
        entries.append(
            {
                "id": slugify(f"lab-{heading.title}-{heading.line_start}"),
                "name": heading.title,
                "level": heading.level,
                "summary": first_paragraph(text),
                "formulae": [f"{label.strip()}: {' '.join(value.split())}" for label, value in formulae],
                "heading_path": " > ".join(heading.heading_path),
                "source_path": CORE_PATH.relative_to(REPO_ROOT).as_posix(),
                "line_start": heading.line_start,
                "line_end": heading.line_end,
                "citation": f"{CORE_PATH.relative_to(REPO_ROOT).as_posix()}:{heading.line_start}-{heading.line_end}",
            }
        )
    return entries


def parse_combat_tables(lines: list[str], headings: list[Heading]) -> list[dict[str, Any]]:
    chapter = next(h for h in headings if h.title == "Chapter 11: Obstacles")
    entries: list[dict[str, Any]] = []
    for heading in descendants_of(headings, chapter):
        table_rows = parse_markdown_table(body_lines(lines, heading))
        if not table_rows:
            continue
        if not any(term in heading.title.lower() for term in ["combat", "damage", "wound", "injur", "attack", "weapon"]):
            continue
        entries.append(
            {
                "id": slugify(f"combat-table-{heading.title}-{heading.line_start}"),
                "name": heading.title,
                "row_count": max(0, len(table_rows) - 1),
                "columns": table_rows[0],
                "rows": table_rows[1:],
                "heading_path": " > ".join(heading.heading_path),
                "source_path": CORE_PATH.relative_to(REPO_ROOT).as_posix(),
                "line_start": heading.line_start,
                "line_end": heading.line_end,
                "citation": f"{CORE_PATH.relative_to(REPO_ROOT).as_posix()}:{heading.line_start}-{heading.line_end}",
            }
        )
    return entries


def parse_covenant_boons_hooks(books: list[dict[str, Any]]) -> list[dict[str, Any]]:
    covenant_path = REPO_ROOT / "reviewed" / "Ars Magica 5e - Covenants.md"
    if not covenant_path.exists():
        return []
    covenant_book = next((b for b in books if b["path"] == covenant_path.relative_to(REPO_ROOT).as_posix()), None)
    if not covenant_book:
        return []
    lines = read_lines(covenant_path)
    headings = [Heading(**heading) for heading in covenant_book["headings"]]
    chapter = next((h for h in headings if h.title == "Chapter Two: Boons & Hooks"), None)
    if not chapter:
        return []

    entries: list[dict[str, Any]] = []
    current_category = ""
    current_kind = ""
    current_magnitude = ""
    source_path = covenant_path.relative_to(REPO_ROOT).as_posix()
    for idx in range(chapter.line_start, chapter.line_end):
        line = lines[idx - 1]
        hmatch = HEADING_RE.match(line)
        if hmatch:
            title = hmatch.group(2).strip()
            current_category = title
            current_kind = "boon" if "boon" in title.lower() else "hook" if "hook" in title.lower() else current_kind
            current_magnitude = "Major" if "major" in title.lower() else "Minor" if "minor" in title.lower() else "Free" if "free" in title.lower() else current_magnitude
            continue
        if not current_kind:
            continue
        match = re.match(r"^\*{0,2}_?\*{0,2}\s*\*\*?([^:*_]+?)\*\*?:\s*(.+)", line.strip())
        if not match:
            match = re.match(r"^\*?([^:*_][^:]{2,80}):\s*(Site|Buildings|Resources|Residents|External|Surroundings|Minor|Major|Free).*$", line.strip())
        if not match:
            continue
        name = re.sub(r"[*_]", "", match.group(1)).strip()
        if len(name) < 2 or name.lower() in {"hooks", "boons"}:
            continue
        description = match.group(2).strip() if len(match.groups()) > 1 else ""
        entries.append(
            {
                "id": slugify(f"covenant-{current_kind}-{name}-{idx}"),
                "name": name,
                "kind": current_kind,
                "magnitude": current_magnitude or ("Major" if "major" in description.lower() else "Minor" if "minor" in description.lower() else ""),
                "category": current_category,
                "summary": first_paragraph(clean_htmlish(description)),
                "source_path": source_path,
                "line_start": idx,
                "line_end": idx,
                "citation": f"{source_path}:{idx}-{idx}",
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
        spell_guidelines=parse_spell_guidelines(lines, headings),
        lab_activities=parse_lab_activities(lines, headings),
        combat_tables=parse_combat_tables(lines, headings),
        covenant_boons_hooks=[],
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
    core_data = extract_core_data(core_book)
    core_data.covenant_boons_hooks = parse_covenant_boons_hooks(books)
    return books, chunks, core_data


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
            "spell_guideline_count": len(core_data.spell_guidelines),
            "lab_activity_count": len(core_data.lab_activities),
            "combat_table_count": len(core_data.combat_tables),
            "covenant_boon_hook_count": len(core_data.covenant_boons_hooks),
        },
        "virtues": core_data.virtues,
        "flaws": core_data.flaws,
        "abilities": core_data.abilities,
        "spells": core_data.spells,
        "spell_guidelines": core_data.spell_guidelines,
        "lab_activities": core_data.lab_activities,
        "combat_tables": core_data.combat_tables,
        "covenant_boons_hooks": core_data.covenant_boons_hooks,
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


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','virtual table') AND name = ? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def load_sqlite_vec(conn: sqlite3.Connection) -> bool:
    try:
        import sqlite_vec
    except Exception:
        return False
    try:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        return True
    except Exception:
        try:
            conn.enable_load_extension(False)
        except Exception:
            pass
        return False


def snapshot_embeddings() -> dict[str, dict[str, Any]]:
    if not DB_PATH.exists():
        return {}
    conn = sqlite3.connect(DB_PATH)
    try:
        if not table_exists(conn, "embeddings"):
            return {}
        rows = conn.execute(
            """
            SELECT content_hash, model, dimensions, embedding, created_at
            FROM embeddings
            WHERE embedding IS NOT NULL
            ORDER BY created_at DESC, chunk_id DESC
            """
        ).fetchall()
    finally:
        conn.close()

    preserved: dict[str, dict[str, Any]] = {}
    for content_hash, model, dimensions, embedding, created_at in rows:
        preserved.setdefault(
            content_hash,
            {
                "model": model,
                "dimensions": dimensions,
                "embedding": embedding,
                "created_at": created_at,
            },
        )
    return preserved


def build_sqlite(books: list[dict], chunks: list[dict], core_data: CoreExtraction) -> dict[str, int]:
    preserved_embeddings = snapshot_embeddings()
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    vec_supported = load_sqlite_vec(conn)
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
        CREATE TABLE core_spell_guidelines (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          technique TEXT NOT NULL,
          form TEXT NOT NULL,
          level TEXT NOT NULL,
          guideline TEXT NOT NULL,
          heading_path TEXT NOT NULL,
          source_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          citation TEXT NOT NULL
        );
        CREATE TABLE core_lab_activities (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          heading_level INTEGER NOT NULL,
          summary TEXT NOT NULL,
          formulae_json TEXT NOT NULL,
          heading_path TEXT NOT NULL,
          source_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          citation TEXT NOT NULL
        );
        CREATE TABLE core_combat_tables (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          row_count INTEGER NOT NULL,
          columns_json TEXT NOT NULL,
          rows_json TEXT NOT NULL,
          heading_path TEXT NOT NULL,
          source_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          citation TEXT NOT NULL
        );
        CREATE TABLE covenant_boons_hooks (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          kind TEXT NOT NULL,
          magnitude TEXT,
          category TEXT NOT NULL,
          summary TEXT NOT NULL,
          source_path TEXT NOT NULL,
          line_start INTEGER NOT NULL,
          line_end INTEGER NOT NULL,
          citation TEXT NOT NULL
        );
        """
    )
    if vec_supported:
        conn.execute("CREATE VIRTUAL TABLE vec_chunks USING vec0(embedding float[3072])")
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
    restored_embeddings = 0
    restored_vec_rows = 0
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
        preserved = preserved_embeddings.get(c["content_hash"])
        if preserved:
            conn.execute(
                """INSERT INTO embeddings(chunk_id,model,dimensions,embedding,content_hash,created_at)
                VALUES(?,?,?,?,?,?)""",
                (
                    rowid,
                    preserved["model"],
                    preserved["dimensions"],
                    preserved["embedding"],
                    c["content_hash"],
                    preserved["created_at"] or datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.execute(
                "UPDATE chunks SET embedding_model=?, embedding_dimensions=? WHERE id=?",
                (preserved["model"], preserved["dimensions"], rowid),
            )
            restored_embeddings += 1
            if vec_supported:
                conn.execute(
                    "INSERT OR REPLACE INTO vec_chunks(rowid, embedding) VALUES(?, ?)",
                    (rowid, preserved["embedding"]),
                )
                restored_vec_rows += 1
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
    for row in core_data.spell_guidelines:
        conn.execute(
            """INSERT INTO core_spell_guidelines(id,name,technique,form,level,guideline,heading_path,source_path,line_start,line_end,citation)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["name"],
                row["technique"],
                row["form"],
                row["level"],
                row["guideline"],
                row["heading_path"],
                row["source_path"],
                row["line_start"],
                row["line_end"],
                row["citation"],
            ),
        )
    for row in core_data.lab_activities:
        conn.execute(
            """INSERT INTO core_lab_activities(id,name,heading_level,summary,formulae_json,heading_path,source_path,line_start,line_end,citation)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["name"],
                row["level"],
                row["summary"],
                json.dumps(row["formulae"], ensure_ascii=False),
                row["heading_path"],
                row["source_path"],
                row["line_start"],
                row["line_end"],
                row["citation"],
            ),
        )
    for row in core_data.combat_tables:
        conn.execute(
            """INSERT INTO core_combat_tables(id,name,row_count,columns_json,rows_json,heading_path,source_path,line_start,line_end,citation)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["name"],
                row["row_count"],
                json.dumps(row["columns"], ensure_ascii=False),
                json.dumps(row["rows"], ensure_ascii=False),
                row["heading_path"],
                row["source_path"],
                row["line_start"],
                row["line_end"],
                row["citation"],
            ),
        )
    for row in core_data.covenant_boons_hooks:
        conn.execute(
            """INSERT INTO covenant_boons_hooks(id,name,kind,magnitude,category,summary,source_path,line_start,line_end,citation)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                row["id"],
                row["name"],
                row["kind"],
                row["magnitude"],
                row["category"],
                row["summary"],
                row["source_path"],
                row["line_start"],
                row["line_end"],
                row["citation"],
            ),
        )
    conn.commit()
    conn.close()
    return {
        "preserved_embeddings": len(preserved_embeddings),
        "restored_embeddings": restored_embeddings,
        "restored_vec_rows": restored_vec_rows,
        "vec_supported": int(vec_supported),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-chars", type=int, default=18000)
    parser.add_argument("--export-chunks-json", action="store_true")
    args = parser.parse_args()
    books, chunks, core_data = build_records(args.max_chars)
    write_json(books, chunks, core_data, args.export_chunks_json)
    write_tocs(books)
    restore_stats = build_sqlite(books, chunks, core_data)
    print(
        " ".join(
            [
                f"books={len(books)}",
                f"chunks={len(chunks)}",
                f"virtues={len(core_data.virtues)}",
                f"flaws={len(core_data.flaws)}",
                f"abilities={len(core_data.abilities)}",
                f"spells={len(core_data.spells)}",
                f"guidelines={len(core_data.spell_guidelines)}",
                f"lab_activities={len(core_data.lab_activities)}",
                f"combat_tables={len(core_data.combat_tables)}",
                f"covenant_boons_hooks={len(core_data.covenant_boons_hooks)}",
                f"preserved_embeddings={restore_stats['preserved_embeddings']}",
                f"restored_embeddings={restore_stats['restored_embeddings']}",
                f"restored_vec_rows={restore_stats['restored_vec_rows']}",
                f"vec_supported={restore_stats['vec_supported']}",
                f"db={DB_PATH}",
            ]
        )
    )


if __name__ == "__main__":
    main()
