"""Conservative consistency validators for clear mechanics."""

from __future__ import annotations

from collections.abc import Mapping

from .audit import ValidationResult, cite
from .spells import DurationName, TargetName, validate_spell_constraints

NON_NEGATIVE_CITATION = cite(15948, 15955)


def validate_non_negative_scores(scores: Mapping[str, int]) -> ValidationResult:
    """Ensure scores and XP-like values are non-negative."""

    warnings = tuple(f"{name} is negative." for name, value in scores.items() if value < 0)
    return ValidationResult(
        valid=not warnings,
        warnings=warnings,
        citations=(NON_NEGATIVE_CITATION,),
    )


def validate_spell(
    *,
    level: int,
    duration_name: DurationName,
    target_name: TargetName,
    ritual: bool,
) -> ValidationResult:
    """Alias for spell constraint validation."""

    return validate_spell_constraints(
        level=level,
        duration_name=duration_name,
        target_name=target_name,
        ritual=ritual,
    )
