"""Seasonal advancement and XP allocation primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

from .audit import AuditResult, Component, ValidationResult, cite


XP_TABLE_CITATION = cite(15944, 15983)
ADVANCEMENT_CITATION = cite(15985, 16004)
SEASONS_CITATION = cite(16005, 16013)
EXPOSURE_CITATION = cite(16015, 16027)
ADVENTURE_CITATION = cite(16028, 16036)
PRACTICE_CITATION = cite(16038, 16057)
TRAINING_CITATION = cite(16059, 16071)
TEACHING_CITATION = cite(16083, 16097)
BOOKS_CITATION = cite(16099, 16117)


ScoreKind = Literal["art", "ability"]


@dataclass(frozen=True)
class XpState:
    """Score state derived from total XP."""

    kind: ScoreKind
    total_xp: int
    score: int
    xp_into_score: int
    xp_to_next: int
    warnings: tuple[str, ...]
    citations: tuple[str, ...]


def xp_to_buy_score(kind: ScoreKind, score: int) -> AuditResult:
    """XP required to buy an Art or Ability score from zero."""

    if score < 0:
        raise ValueError("score must be non-negative.")
    triangular = score * (score + 1) // 2
    value = triangular if kind == "art" else triangular * 5
    return AuditResult(
        value=value,
        components=(Component(f"{kind} score {score}", value, XP_TABLE_CITATION),),
        warnings=(),
        citations=(XP_TABLE_CITATION,),
        metadata={"kind": kind, "score": score},
    )


def xp_to_raise_next(kind: ScoreKind, current_score: int) -> AuditResult:
    """XP required to increase current score by one."""

    if current_score < 0:
        raise ValueError("current_score must be non-negative.")
    next_score = current_score + 1
    value = next_score if kind == "art" else next_score * 5
    return AuditResult(
        value=value,
        components=(Component(f"Raise {kind} to {next_score}", value, XP_TABLE_CITATION),),
        warnings=(),
        citations=(XP_TABLE_CITATION,),
        metadata={"kind": kind, "current_score": current_score},
    )


def score_from_xp(kind: ScoreKind, total_xp: int) -> XpState:
    """Derive score and progress to next score from total XP."""

    if total_xp < 0:
        raise ValueError("total_xp must be non-negative.")
    score = 0
    while int(xp_to_buy_score(kind, score + 1).value) <= total_xp:
        score += 1
    spent = int(xp_to_buy_score(kind, score).value)
    next_cost = int(xp_to_raise_next(kind, score).value)
    return XpState(
        kind=kind,
        total_xp=total_xp,
        score=score,
        xp_into_score=total_xp - spent,
        xp_to_next=next_cost - (total_xp - spent),
        warnings=(),
        citations=(XP_TABLE_CITATION,),
    )


def advancement_total(
    *,
    source_quality: int,
    virtue_bonus: int = 0,
    flaw_penalty: int = 0,
    other_modifier: int = 0,
) -> AuditResult:
    """Calculate Source Quality + Virtues - Flaws."""

    return AuditResult(
        value=source_quality + virtue_bonus - flaw_penalty + other_modifier,
        components=(
            Component("Source Quality", source_quality, ADVANCEMENT_CITATION),
            Component("Virtue Bonus", virtue_bonus, ADVANCEMENT_CITATION),
            Component("Flaw Penalty", -flaw_penalty, ADVANCEMENT_CITATION),
            Component("Other Modifier", other_modifier, ADVANCEMENT_CITATION),
        ),
        warnings=(),
        citations=(ADVANCEMENT_CITATION,),
    )


def apply_experience(
    *,
    kind: ScoreKind,
    current_xp: int,
    gained_xp: int,
    gain_limit: int | None = None,
) -> XpState:
    """Apply XP with optional gain limit from a source."""

    if current_xp < 0 or gained_xp < 0:
        raise ValueError("XP values must be non-negative.")
    target_xp = current_xp + gained_xp
    warnings: list[str] = []
    if gain_limit is not None:
        cap = int(xp_to_buy_score(kind, gain_limit).value)
        if target_xp > cap:
            target_xp = cap
            warnings.append("Gain limit capped XP and prevents progress beyond the source level.")
    state = score_from_xp(kind, target_xp)
    return XpState(
        kind=state.kind,
        total_xp=state.total_xp,
        score=state.score,
        xp_into_score=state.xp_into_score,
        xp_to_next=state.xp_to_next,
        warnings=tuple(warnings),
        citations=(XP_TABLE_CITATION, SEASONS_CITATION),
    )


def exposure_source_quality(*, split_between_subjects: int = 1) -> AuditResult:
    """Return Exposure Source Quality per subject."""

    if split_between_subjects not in {1, 2}:
        raise ValueError("Exposure may be assigned to one subject or split between two.")
    quality = 2 if split_between_subjects == 1 else 1
    return AuditResult(
        value=quality,
        components=(Component("Exposure Source Quality", quality, EXPOSURE_CITATION),),
        warnings=(),
        citations=(EXPOSURE_CITATION,),
        metadata={"split_between_subjects": split_between_subjects},
    )


def adventure_source_quality(*, quality: int) -> AuditResult:
    """Return storyguide-set Adventure Source Quality, checking the stated range."""

    warnings = ()
    if quality < 5 or quality > 10:
        warnings = ("Adventure Source Quality is normally 5-10; this is a troupe/storyguide input.",)
    return AuditResult(
        value=quality,
        components=(Component("Adventure Source Quality", quality, ADVENTURE_CITATION),),
        warnings=warnings,
        citations=(ADVENTURE_CITATION,),
    )


def practice_source_quality(*, quality: int = 4) -> AuditResult:
    """Return Practice Source Quality, warning outside the stated range."""

    warnings = ()
    if quality < 4 or quality > 8:
        warnings = ("Practice Source Quality is normally 4-8 and usually 4.",)
    return AuditResult(
        value=quality,
        components=(Component("Practice Source Quality", quality, PRACTICE_CITATION),),
        warnings=warnings,
        citations=(PRACTICE_CITATION,),
    )


def training_source_quality(*, master_score: int) -> AuditResult:
    """Return Training Source Quality and gain-limit metadata."""

    if master_score < 0:
        raise ValueError("master_score must be non-negative.")
    warnings = ()
    if master_score < 2:
        warnings = ("A trainer needs at least score 2 in the Ability being taught.",)
    quality = master_score + 3
    return AuditResult(
        value=quality,
        components=(Component("Master score + 3", quality, TRAINING_CITATION),),
        warnings=warnings,
        citations=(TRAINING_CITATION,),
        metadata={"gain_limit": master_score},
    )


def teaching_source_quality(
    *,
    communication: int,
    teaching: int,
    single_student_bonus: int,
) -> AuditResult:
    """Return Teaching Source Quality from explicit student-count bonus."""

    if single_student_bonus not in {0, 3, 6}:
        raise ValueError("Teaching student-count bonus must be 0, 3, or 6.")
    return AuditResult(
        value=communication + teaching + 3 + single_student_bonus,
        components=(
            Component("Communication", communication, TEACHING_CITATION),
            Component("Teaching", teaching, TEACHING_CITATION),
            Component("Base", 3, TEACHING_CITATION),
            Component("Student-count bonus", single_student_bonus, TEACHING_CITATION),
        ),
        warnings=(),
        citations=(TEACHING_CITATION,),
    )


def validate_adventure_allocations(
    *,
    allocations: Mapping[str, int],
    source_quality: int,
) -> ValidationResult:
    """Validate adventure XP allocation limits."""

    warnings: list[str] = []
    if sum(allocations.values()) != source_quality:
        warnings.append("Adventure allocation total should equal the season's Source Quality.")
    for subject, points in allocations.items():
        if points > 5:
            warnings.append(f"{subject} receives more than five adventure Source Quality points.")
        if points < 0:
            warnings.append(f"{subject} has negative allocated points.")
    return ValidationResult(
        valid=not warnings,
        warnings=tuple(warnings),
        citations=(ADVENTURE_CITATION,),
    )


def validate_single_xp_source(*, source_count: int) -> ValidationResult:
    """Check that a season uses only one advancement source."""

    warnings = ()
    if source_count != 1:
        warnings = ("A character may only gain experience from one source in one season.",)
    return ValidationResult(
        valid=not warnings,
        warnings=warnings,
        citations=(ADVANCEMENT_CITATION,),
    )
