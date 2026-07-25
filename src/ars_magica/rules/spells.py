"""Spell level construction helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .audit import AuditResult, Component, ValidationResult, cite

LEVELS_CITATION = cite(11963, 11973)
RDT_CITATION = cite(11975, 12009)
RITUAL_LIMITS_CITATION = cite(12279, 12295)
REQUISITES_CITATION = cite(12297, 12319)


RangeName = Literal["Personal", "Touch", "Eye", "Voice", "Sight", "Arcane Connection"]
DurationName = Literal["Momentary", "Concentration", "Diameter", "Sun", "Ring", "Moon", "Year"]
TargetName = Literal[
    "Individual",
    "Circle",
    "Part",
    "Group",
    "Room",
    "Structure",
    "Boundary",
    "Taste",
    "Touch",
    "Smell",
    "Hearing",
    "Vision",
]


RANGE_MAGNITUDES: dict[str, int] = {
    "Personal": 0,
    "Touch": 1,
    "Eye": 1,
    "Voice": 2,
    "Sight": 3,
    "Arcane Connection": 4,
}

DURATION_MAGNITUDES: dict[str, int] = {
    "Momentary": 0,
    "Concentration": 1,
    "Diameter": 1,
    "Sun": 2,
    "Ring": 2,
    "Moon": 3,
    "Year": 4,
}

TARGET_MAGNITUDES: dict[str, int] = {
    "Individual": 0,
    "Circle": 0,
    "Taste": 0,
    "Part": 1,
    "Touch": 1,
    "Group": 2,
    "Room": 2,
    "Smell": 2,
    "Structure": 3,
    "Hearing": 3,
    "Boundary": 4,
    "Vision": 4,
}


@dataclass(frozen=True)
class RequisiteDecision:
    """Caller-supplied requisite level adjustment."""

    name: str
    purpose: Literal["necessary", "enhancing", "cosmetic", "undecided"]
    magnitudes: int = 0


def spell_magnitude(level: int) -> AuditResult:
    """Return spell magnitude, rounded up."""

    if level < 1:
        raise ValueError("Spell level must be at least 1.")
    magnitude = (level + 4) // 5
    return AuditResult(
        value=magnitude,
        components=(Component("Spell Level", level, LEVELS_CITATION),),
        warnings=(),
        citations=(LEVELS_CITATION,),
    )


def adjust_spell_level(level: int, magnitude_delta: int) -> AuditResult:
    """Adjust a spell level by magnitudes using the below-level-5 rule."""

    if level < 1:
        raise ValueError("Spell level must be at least 1.")
    current = level
    components: list[Component] = [Component("Starting Level", level, RDT_CITATION)]
    warnings: list[str] = []
    if magnitude_delta > 0:
        for step in range(magnitude_delta):
            increment = 1 if current < 5 else 5
            current += increment
            components.append(Component(f"Magnitude Increase {step + 1}", increment, RDT_CITATION))
    else:
        for step in range(abs(magnitude_delta)):
            decrement = 1 if current <= 5 else 5
            current = max(1, current - decrement)
            components.append(Component(f"Magnitude Decrease {step + 1}", -decrement, RDT_CITATION))
            if current == 1 and step + 1 < abs(magnitude_delta):
                warnings.append("Further reductions were clamped at minimum spell level 1.")
                break
    return AuditResult(
        value=current,
        components=tuple(components),
        warnings=tuple(warnings),
        citations=(RDT_CITATION,),
        metadata={"magnitude_delta": magnitude_delta},
    )


def construct_spell_level(
    *,
    base_level: int,
    range_name: RangeName = "Personal",
    duration_name: DurationName = "Momentary",
    target_name: TargetName = "Individual",
    size_magnitudes: int = 0,
    requisites: tuple[RequisiteDecision, ...] = (),
    ritual: bool | None = None,
    guideline_requires_ritual: bool = False,
    spectacular_requires_ritual: bool = False,
) -> AuditResult:
    """Construct a spell level from a guideline level and explicit adjustments."""

    if base_level < 1:
        raise ValueError("base_level must be at least 1.")
    if size_magnitudes < 0:
        raise ValueError("size_magnitudes must be non-negative.")

    requisite_magnitudes = 0
    warnings: list[str] = []
    components = [
        Component("Base Guideline Level", base_level, LEVELS_CITATION),
        Component(f"Range {range_name}", RANGE_MAGNITUDES[range_name], RDT_CITATION),
        Component(f"Duration {duration_name}", DURATION_MAGNITUDES[duration_name], RDT_CITATION),
        Component(f"Target {target_name}", TARGET_MAGNITUDES[target_name], RDT_CITATION),
    ]
    if size_magnitudes:
        components.append(Component("Size Magnitudes", size_magnitudes, LEVELS_CITATION))

    for requisite in requisites:
        if requisite.purpose == "undecided":
            warnings.append(
                f"Requisite {requisite.name!r} is undecided; caller must choose whether it changes level."
            )
        elif requisite.purpose == "enhancing" and requisite.magnitudes <= 0:
            warnings.append(
                f"Enhancing requisite {requisite.name!r} needs an explicit positive magnitude adjustment."
            )
        elif requisite.purpose in {"necessary", "cosmetic"} and requisite.magnitudes != 0:
            warnings.append(
                f"Requisite {requisite.name!r} is marked {requisite.purpose} but has non-zero magnitudes."
            )
        requisite_magnitudes += requisite.magnitudes
        components.append(
            Component(
                f"Requisite {requisite.name} ({requisite.purpose})",
                requisite.magnitudes,
                REQUISITES_CITATION,
            )
        )

    magnitude_delta = (
        RANGE_MAGNITUDES[range_name]
        + DURATION_MAGNITUDES[duration_name]
        + TARGET_MAGNITUDES[target_name]
        + size_magnitudes
        + requisite_magnitudes
    )
    adjusted = adjust_spell_level(base_level, magnitude_delta)
    final_level = int(adjusted.value)

    ritual_needed = (
        guideline_requires_ritual
        or spectacular_requires_ritual
        or duration_name == "Year"
        or target_name == "Boundary"
        or final_level > 50
    )
    if ritual is None and ritual_needed:
        warnings.append("This spell appears to require Ritual status; pass ritual=True to confirm.")
    if ritual is False and ritual_needed:
        warnings.append("Inputs describe a spell that Core Rules say must be Ritual.")
    if ritual and final_level < 20:
        components.append(
            Component("Ritual Minimum Level", 20 - final_level, RITUAL_LIMITS_CITATION)
        )
        final_level = 20

    return AuditResult(
        value=final_level,
        components=tuple(components),
        warnings=tuple(warnings) + adjusted.warnings,
        citations=(LEVELS_CITATION, RDT_CITATION, REQUISITES_CITATION, RITUAL_LIMITS_CITATION),
        metadata={
            "magnitude_delta": magnitude_delta,
            "ritual_needed": ritual_needed,
            "ritual": ritual,
        },
    )


def validate_spell_constraints(
    *,
    level: int,
    duration_name: DurationName,
    target_name: TargetName,
    ritual: bool,
) -> ValidationResult:
    """Check unambiguous Ritual constraints for a designed spell."""

    warnings: list[str] = []
    if not ritual and duration_name == "Year":
        warnings.append("Formulaic and Spontaneous spells may not have Year duration.")
    if not ritual and target_name == "Boundary":
        warnings.append("Formulaic and Spontaneous spells may not have Boundary target.")
    if not ritual and level > 50:
        warnings.append("Formulaic and Spontaneous spells may not have level greater than 50.")
    if ritual and level < 20:
        warnings.append("Ritual spells are always at least level 20.")
    return ValidationResult(
        valid=not warnings,
        warnings=tuple(warnings),
        citations=(RITUAL_LIMITS_CITATION,),
    )
