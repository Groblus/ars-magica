#!/usr/bin/env python3
"""FastMCP tools for Ars Magica corpus lookup, mechanics, and publishing."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import asdict, is_dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, cast

from fastmcp import FastMCP

from ars_magica.publishing import (
    OptionalDependencyError,
    build_manifest,
    inspect_template_requirements,
    list_templates,
    package_material,
    render_html,
)
from ars_magica.rules import (
    advancement_total,
    adventure_source_quality,
    apply_experience,
    casting_score,
    construct_spell_level,
    exposure_source_quality,
    formulaic_casting_total,
    lab_total,
    penetration_bonus,
    penetration_total,
    practice_source_quality,
    score_from_xp,
    simple_die,
    stress_die,
    teaching_source_quality,
    training_source_quality,
    xp_to_buy_score,
)
from ars_magica.rules.advancement import ScoreKind
from ars_magica.rules.spells import DurationName, RangeName, TargetName

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = (
    ROOT / "skills" / "ars-magica-corpus-navigator" / "resources" / "ars_magica.sqlite"
)
SQLITE_HEADER = b"SQLite format 3\x00"
LFS_POINTER_HEADER = b"version https://git-lfs.github.com/spec/v1"
EXPECTED_SCHEMA_VERSION = 1
REQUIRED_CORPUS_TABLES = frozenset(
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

mcp = FastMCP("ars-magica-reference")


class DatabaseUnavailableError(RuntimeError):
    """Raised when corpus database cannot satisfy runtime contract."""


def database_path() -> Path:
    """Return configured corpus database path."""
    configured_path = os.environ.get("ARS_MAGICA_DB_PATH")
    if configured_path:
        return Path(configured_path).expanduser()
    return DEFAULT_DB_PATH


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _database_unavailable(
    error: Exception | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    path = database_path() if path is None else path
    details = str(error) if error is not None else None
    if isinstance(error, DatabaseUnavailableError):
        reason = str(error)
    elif not path.exists():
        reason = "database file is missing"
    else:
        try:
            with path.open("rb") as database_file:
                header = database_file.read(128)
        except OSError as read_error:
            reason = f"database file could not be read: {read_error}"
        else:
            if header.startswith(LFS_POINTER_HEADER):
                reason = (
                    "database file is a Git LFS pointer; fetch LFS assets before using corpus tools"
                )
            elif not header.startswith(SQLITE_HEADER):
                reason = "database file is not a SQLite database"
            else:
                reason = "database-backed corpus lookup failed"
    return {
        "error": "ars_magica_database_unavailable",
        "reason": reason,
        "path": str(path),
        "details": details,
    }


def _validate_corpus_database(conn: sqlite3.Connection) -> None:
    table_rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    table_names = {str(row[0]) for row in table_rows}
    missing_tables = sorted(REQUIRED_CORPUS_TABLES - table_names)
    if missing_tables:
        raise DatabaseUnavailableError(
            "database is missing required corpus tables: " + ", ".join(missing_tables)
        )

    if "metadata" not in table_names:
        return

    metadata_columns = {
        str(row[1]) for row in conn.execute("PRAGMA table_info(metadata)").fetchall()
    }
    if not {"key", "value"}.issubset(metadata_columns):
        raise DatabaseUnavailableError("database metadata must contain key and value columns")

    version_rows = conn.execute(
        "SELECT value FROM metadata WHERE key = 'schema_version' LIMIT 2"
    ).fetchall()
    if len(version_rows) != 1 or version_rows[0][0] is None:
        raise DatabaseUnavailableError("database metadata schema_version is malformed")

    raw_version = version_rows[0][0]
    try:
        schema_version = int(raw_version)
    except (TypeError, ValueError) as error:
        raise DatabaseUnavailableError("database metadata schema_version is malformed") from error
    if str(raw_version).strip() != str(schema_version):
        raise DatabaseUnavailableError("database metadata schema_version is malformed")
    if schema_version != EXPECTED_SCHEMA_VERSION:
        raise DatabaseUnavailableError(
            f"unsupported database schema version: {schema_version}; expected {EXPECTED_SCHEMA_VERSION}"
        )


def connect() -> sqlite3.Connection:
    path = database_path()
    unavailable = _database_unavailable(path=path)
    if unavailable["reason"] != "database-backed corpus lookup failed":
        raise DatabaseUnavailableError(unavailable["reason"])

    conn: sqlite3.Connection | None = None
    try:
        uri = f"{path.resolve().as_uri()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("SELECT 1")
        _validate_corpus_database(conn)
        return conn
    except (OSError, sqlite3.Error) as error:
        if conn is not None:
            conn.close()
        raise DatabaseUnavailableError(_database_unavailable(error, path)["reason"]) from error
    except DatabaseUnavailableError:
        if conn is not None:
            conn.close()
        raise


def rows(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    return [dict(row) for row in cursor.fetchall()]


def safe_limit(limit: int, default: int = 8, maximum: int = 50) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        value = default
    return max(1, min(maximum, value))


@mcp.tool()
def search_rules(query: str, limit: int = 8) -> list[dict[str, Any]] | dict[str, Any]:
    """Search DE/5e heading-aware rule chunks with citations."""
    limit = safe_limit(limit)
    try:
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
    except (RuntimeError, sqlite3.Error, OSError) as error:
        return _database_unavailable(error)


@mcp.tool()
def get_section(section_id: str) -> dict[str, Any]:
    """Return one indexed section plus its chunk text."""
    try:
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
    except (RuntimeError, sqlite3.Error, OSError) as error:
        return _database_unavailable(error)


@mcp.tool()
def list_book_toc(book_query: str = "", limit: int = 50) -> list[dict[str, Any]] | dict[str, Any]:
    """List top-level table-of-contents sections for matching books."""
    limit = safe_limit(limit, default=50, maximum=200)
    like = f"%{book_query}%"
    try:
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
    except (RuntimeError, sqlite3.Error, OSError) as error:
        return _database_unavailable(error)


@mcp.tool()
def find_spell(
    query: str = "",
    technique: str = "",
    form: str = "",
    max_level: int | None = None,
    limit: int = 20,
) -> list[dict[str, Any]] | dict[str, Any]:
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
    try:
        with connect() as conn:
            return rows(
                conn.execute(
                    f"""
                    SELECT name, technique, form, spell_level, level_label, spell_range, duration,
                           target, ritual, parameter_line, design_notes, description, citation
                    FROM core_spells
                    WHERE {" AND ".join(clauses)}
                    ORDER BY technique, form, spell_level, name
                    LIMIT ?
                    """,
                    params,
                )
            )
    except (RuntimeError, sqlite3.Error, OSError) as error:
        return _database_unavailable(error)


def lookup_named(table: str, name: str, limit: int = 20) -> list[dict[str, Any]] | dict[str, Any]:
    limit = safe_limit(limit, default=20)
    try:
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
    except (RuntimeError, sqlite3.Error, OSError) as error:
        return _database_unavailable(error)


@mcp.tool()
def lookup_virtue(name: str, limit: int = 20) -> list[dict[str, Any]] | dict[str, Any]:
    """Lookup Definitive Edition virtues with citation."""
    return lookup_named("core_virtues", name, limit)


@mcp.tool()
def lookup_flaw(name: str, limit: int = 20) -> list[dict[str, Any]] | dict[str, Any]:
    """Lookup Definitive Edition flaws with citation."""
    return lookup_named("core_flaws", name, limit)


@mcp.tool()
def lookup_ability(name: str, limit: int = 20) -> list[dict[str, Any]] | dict[str, Any]:
    """Lookup Definitive Edition abilities with citation."""
    limit = safe_limit(limit, default=20)
    try:
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
    except (RuntimeError, sqlite3.Error, OSError) as error:
        return _database_unavailable(error)


@mcp.tool()
def lookup_covenant_option(
    query: str, kind: str = "", limit: int = 20
) -> list[dict[str, Any]] | dict[str, Any]:
    """Lookup covenant boons/hooks from the 5e Covenants extraction."""
    limit = safe_limit(limit, default=20)
    clauses = ["(name LIKE ? OR summary LIKE ? OR category LIKE ?)"]
    params: list[Any] = [f"%{query}%", f"%{query}%", f"%{query}%"]
    if kind:
        clauses.append("kind = ?")
        params.append(kind)
    params.append(limit)
    try:
        with connect() as conn:
            return rows(
                conn.execute(
                    f"""
                    SELECT name, kind, magnitude, category, summary, citation
                    FROM covenant_boons_hooks
                    WHERE {" AND ".join(clauses)}
                    ORDER BY kind, category, name
                    LIMIT ?
                    """,
                    params,
                )
            )
    except (RuntimeError, sqlite3.Error, OSError) as error:
        return _database_unavailable(error)


@mcp.tool()
def roll_simple_die(roll: int | None = None, seed: int | None = None) -> dict[str, Any]:
    """Roll a simple die; 0 counts as 10. Returns trace and Core Rules citations."""
    try:
        return _jsonable(simple_die(roll=roll, seed=seed))
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def roll_stress_die(
    rolls: list[int] | None = None,
    botch_rolls: list[int] | None = None,
    botch_dice: int = 1,
    can_botch: bool = True,
    seed: int | None = None,
) -> dict[str, Any]:
    """Roll a stress die with explicit or seeded rolls. Returns trace and citations."""
    try:
        return _jsonable(
            stress_die(
                rolls=() if rolls is None else rolls,
                botch_rolls=() if botch_rolls is None else botch_rolls,
                botch_dice=botch_dice,
                can_botch=can_botch,
                seed=seed,
            )
        )
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def calculate_casting_score(
    technique: int,
    form: int,
    stamina: int,
    encumbrance: int = 0,
    aura_modifier: int = 0,
) -> dict[str, Any]:
    """Calculate Technique + Form + Stamina - Encumbrance + Aura Modifier."""
    return _jsonable(
        casting_score(
            technique=technique,
            form=form,
            stamina=stamina,
            encumbrance=encumbrance,
            aura_modifier=aura_modifier,
        )
    )


@mcp.tool()
def calculate_formulaic_casting(
    casting_score_total: int,
    spell_level: int,
    die_roll: int | None = None,
    die_seed: int | None = None,
) -> dict[str, Any]:
    """Resolve Formulaic casting with a simple die and preserved citations."""
    return _jsonable(
        formulaic_casting_total(
            casting_score_total=casting_score_total,
            die=simple_die(roll=die_roll, seed=die_seed),
            spell_level=spell_level,
        )
    )


@mcp.tool()
def calculate_penetration(
    casting_total: int,
    spell_level: int,
    penetration_ability: int,
    multiplier: int = 1,
    multiplier_bonus: int = 0,
    magic_resistance: int | None = None,
    forceless: bool = False,
) -> dict[str, Any]:
    """Calculate Penetration Total and optional Magic Resistance comparison."""
    bonus = penetration_bonus(
        penetration_ability=penetration_ability,
        multiplier=multiplier,
        multiplier_bonus=multiplier_bonus,
    )
    outcome = penetration_total(
        casting_total=casting_total,
        spell_level=spell_level,
        penetration_bonus_total=int(bonus.value),
        magic_resistance=magic_resistance,
        forceless=forceless,
    )
    data = _jsonable(outcome)
    data["penetration_bonus"] = _jsonable(bonus)
    return data


@mcp.tool()
def design_spell_level(
    base_level: int,
    range_name: str = "Personal",
    duration_name: str = "Momentary",
    target_name: str = "Individual",
    size_magnitudes: int = 0,
    ritual: bool | None = None,
) -> dict[str, Any]:
    """Construct a spell level from base guideline and R/D/T choices."""
    try:
        # FastMCP receives JSON strings; construct_spell_level validates legal literal values.
        return _jsonable(
            construct_spell_level(
                base_level=base_level,
                range_name=cast(RangeName, range_name),
                duration_name=cast(DurationName, duration_name),
                target_name=cast(TargetName, target_name),
                size_magnitudes=size_magnitudes,
                ritual=ritual,
            )
        )
    except (KeyError, ValueError) as error:
        return {"error": str(error)}


@mcp.tool()
def calculate_lab_total(
    technique: int,
    form: int,
    intelligence: int,
    magic_theory: int,
    aura_modifier: int = 0,
) -> dict[str, Any]:
    """Calculate Technique + Form + Intelligence + Magic Theory + Aura Modifier."""
    return _jsonable(
        lab_total(
            technique=technique,
            form=form,
            intelligence=intelligence,
            magic_theory=magic_theory,
            aura_modifier=aura_modifier,
        )
    )


@mcp.tool()
def calculate_xp_to_buy_score(kind: str, score: int) -> dict[str, Any]:
    """Calculate XP required to buy an Art or Ability score from zero."""
    try:
        # FastMCP receives JSON strings; xp_to_buy_score validates legal score kinds.
        return _jsonable(xp_to_buy_score(cast(ScoreKind, kind), score))
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def calculate_score_progress(kind: str, total_xp: int) -> dict[str, Any]:
    """Derive an Art or Ability score and progress to its next score from total XP."""
    try:
        # FastMCP receives JSON strings; score_from_xp validates legal score kinds.
        return _jsonable(score_from_xp(cast(ScoreKind, kind), total_xp))
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def apply_advancement_experience(
    kind: str,
    current_xp: int,
    gained_xp: int,
    gain_limit: int | None = None,
) -> dict[str, Any]:
    """Apply experience to an Art or Ability, with an optional source gain limit."""
    try:
        return _jsonable(
            apply_experience(
                # FastMCP receives JSON strings; apply_experience validates legal score kinds.
                kind=cast(ScoreKind, kind),
                current_xp=current_xp,
                gained_xp=gained_xp,
                gain_limit=gain_limit,
            )
        )
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def calculate_advancement_total(
    source_quality: int,
    virtue_bonus: int = 0,
    flaw_penalty: int = 0,
    other_modifier: int = 0,
) -> dict[str, Any]:
    """Calculate Source Quality + Virtues - Flaws + other modifier."""
    return _jsonable(
        advancement_total(
            source_quality=source_quality,
            virtue_bonus=virtue_bonus,
            flaw_penalty=flaw_penalty,
            other_modifier=other_modifier,
        )
    )


@mcp.tool()
def calculate_exposure_source_quality(split_between_subjects: int = 1) -> dict[str, Any]:
    """Calculate Exposure Source Quality per subject."""
    try:
        return _jsonable(exposure_source_quality(split_between_subjects=split_between_subjects))
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def calculate_practice_source_quality(quality: int = 4) -> dict[str, Any]:
    """Return Practice Source Quality, warning outside the normal range."""
    return _jsonable(practice_source_quality(quality=quality))


@mcp.tool()
def calculate_training_source_quality(master_score: int) -> dict[str, Any]:
    """Calculate Training Source Quality and report its source gain limit."""
    try:
        return _jsonable(training_source_quality(master_score=master_score))
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def calculate_teaching_source_quality(
    communication: int,
    teaching: int,
    single_student_bonus: int = 0,
) -> dict[str, Any]:
    """Calculate Teaching Source Quality from teacher and student-count inputs."""
    try:
        return _jsonable(
            teaching_source_quality(
                communication=communication,
                teaching=teaching,
                single_student_bonus=single_student_bonus,
            )
        )
    except ValueError as error:
        return {"error": str(error)}


@mcp.tool()
def calculate_adventure_source_quality(quality: int) -> dict[str, Any]:
    """Return Adventure Source Quality with guidance on its normal range."""
    return _jsonable(adventure_source_quality(quality=quality))


@mcp.tool()
def list_publishing_templates() -> list[dict[str, Any]]:
    """List checked-in printable material templates."""
    return list_templates()


@mcp.tool()
def inspect_publishing_template(template: str) -> dict[str, Any]:
    """Inspect the structured input contract for one publishing template."""
    try:
        return inspect_template_requirements(template)
    except Exception as error:
        return {"error": str(error)}


@mcp.tool()
def render_material_html(spec: dict[str, Any]) -> dict[str, Any]:
    """Render a material spec to self-contained HTML. Requires the publishing extra."""
    try:
        html = render_html(spec)
        return {"html": html, "manifest": build_manifest(spec)}
    except OptionalDependencyError as error:
        return {"error": "optional_dependency_missing", "details": str(error)}
    except Exception as error:
        return {"error": str(error)}


@mcp.tool()
def package_material_zip(
    spec: dict[str, Any],
    destination: str,
    include_pdf: bool = False,
) -> dict[str, Any]:
    """Write a deterministic material ZIP and return its path and manifest."""
    try:
        path = package_material(spec, destination, include_pdf=include_pdf)
        return {"package": str(path), "manifest": build_manifest(spec)}
    except OptionalDependencyError as error:
        return {"error": "optional_dependency_missing", "details": str(error)}
    except Exception as error:
        return {"error": str(error)}


if __name__ == "__main__":
    mcp.run()
