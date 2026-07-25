"""Casting score, casting total, and Penetration helpers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from .audit import AuditResult, Component, audit_sum, cite
from .dice import DieRollResult, apply_die_to_modifier

CASTING_SCORE_CITATION = cite(9089, 9089)
FORMULAIC_CITATION = cite(9099, 9115)
RITUAL_CITATION = cite(9117, 9137)
SPONTANEOUS_CITATION = cite(9139, 9151)
PENETRATION_CITATION = cite(9153, 9161)
SYMPATHETIC_CITATION = cite(9333, 9369)
FORCELESS_CITATION = cite(9350, 9354)
REQUISITE_CASTING_CITATION = cite(12309, 12313)


@dataclass(frozen=True)
class CastingOutcome:
    """A casting total plus spell success/fatigue outcome."""

    total: int
    margin: int
    spell_cast: bool
    fatigue_levels_lost: int
    components: tuple[Component, ...]
    warnings: tuple[str, ...]
    citations: tuple[str, ...]
    botched: bool = False
    botch_count: int = 0


@dataclass(frozen=True)
class PenetrationOutcome:
    """A Penetration total and optional Magic Resistance comparison."""

    total: int
    penetrates: bool | None
    components: tuple[Component, ...]
    warnings: tuple[str, ...]
    citations: tuple[str, ...]


def effective_art_score(
    *,
    primary_score: int,
    requisite_scores: Sequence[int] = (),
    art_kind: Literal["Technique", "Form"] = "Form",
) -> AuditResult:
    """Apply requisite limiting for one Technique or Form score."""

    components = [Component(f"primary {art_kind}", primary_score, REQUISITE_CASTING_CITATION)]
    components.extend(
        Component(f"requisite {art_kind} {index + 1}", score, REQUISITE_CASTING_CITATION)
        for index, score in enumerate(requisite_scores)
    )
    effective = min((primary_score,) + tuple(requisite_scores))
    warnings = ()
    if requisite_scores and effective < primary_score:
        warnings = (f"{art_kind} score limited by the lowest applicable requisite.",)
    return AuditResult(
        value=effective,
        components=tuple(components),
        warnings=warnings,
        citations=(REQUISITE_CASTING_CITATION,),
        metadata={"primary_score": primary_score, "requisite_scores": tuple(requisite_scores)},
    )


def casting_score(
    *,
    technique: int,
    form: int,
    stamina: int,
    encumbrance: int = 0,
    aura_modifier: int = 0,
    technique_requisites: Sequence[int] = (),
    form_requisites: Sequence[int] = (),
    other_modifiers: Sequence[Component] = (),
) -> AuditResult:
    """Calculate Technique + Form + Stamina - Encumbrance + Aura Modifier."""

    effective_technique = effective_art_score(
        primary_score=technique,
        requisite_scores=technique_requisites,
        art_kind="Technique",
    )
    effective_form = effective_art_score(
        primary_score=form,
        requisite_scores=form_requisites,
        art_kind="Form",
    )
    components = (
        Component("Technique", effective_technique.value, CASTING_SCORE_CITATION),
        Component("Form", effective_form.value, CASTING_SCORE_CITATION),
        Component("Stamina", stamina, CASTING_SCORE_CITATION),
        Component("Encumbrance", -encumbrance, CASTING_SCORE_CITATION),
        Component("Aura Modifier", aura_modifier, CASTING_SCORE_CITATION),
    ) + tuple(other_modifiers)
    return audit_sum(
        components,
        warnings=effective_technique.warnings + effective_form.warnings,
        citations=(CASTING_SCORE_CITATION, REQUISITE_CASTING_CITATION),
        metadata={
            "technique_requisites": tuple(technique_requisites),
            "form_requisites": tuple(form_requisites),
        },
    )


def formulaic_casting_total(
    *,
    casting_score_total: int,
    die: DieRollResult,
    spell_level: int,
) -> CastingOutcome:
    """Resolve Formulaic casting success and fatigue from a casting score and die."""

    total_result = apply_die_to_modifier(modifier=casting_score_total, die=die)
    total = int(total_result.value)
    margin = total - spell_level
    if die.botched:
        spell_cast = False
        fatigue = 0
        warnings = total_result.warnings + (
            "Formulaic botch consequences are not deterministic in this helper.",
        )
    elif margin >= 0:
        spell_cast = True
        fatigue = 0
        warnings = total_result.warnings
    elif margin >= -10:
        spell_cast = True
        fatigue = 1
        warnings = total_result.warnings
    else:
        spell_cast = False
        fatigue = 1
        warnings = total_result.warnings
    return CastingOutcome(
        total=total,
        margin=margin,
        spell_cast=spell_cast,
        fatigue_levels_lost=fatigue,
        components=(
            Component("Casting Score", casting_score_total, FORMULAIC_CITATION),
            Component("Die Roll", die.value, FORMULAIC_CITATION),
            Component("Spell Level", -spell_level, FORMULAIC_CITATION),
        ),
        warnings=warnings,
        citations=(FORMULAIC_CITATION,) + die.citations,
        botched=die.botched,
        botch_count=die.botch_count,
    )


def ritual_casting_total(
    *,
    casting_score_total: int,
    artes_liberales: int,
    philosophiae: int,
    die: DieRollResult,
    spell_level: int,
) -> CastingOutcome:
    """Resolve Ritual casting success and long-term fatigue."""

    fixed_total = casting_score_total + artes_liberales + philosophiae
    total_result = apply_die_to_modifier(modifier=fixed_total, die=die)
    total = int(total_result.value)
    margin = total - spell_level
    if die.botched:
        spell_cast = False
        fatigue = 0
        warnings = total_result.warnings + (
            "Ritual botch consequences are not deterministic in this helper.",
        )
    elif margin >= 0:
        spell_cast = True
        fatigue = 1
        warnings = total_result.warnings
    elif margin >= -5:
        spell_cast = True
        fatigue = 2
        warnings = total_result.warnings
    elif margin >= -10:
        spell_cast = True
        fatigue = 3
        warnings = total_result.warnings
    elif margin >= -15:
        spell_cast = False
        fatigue = 4
        warnings = total_result.warnings
    else:
        spell_cast = False
        fatigue = 5
        warnings = total_result.warnings
    return CastingOutcome(
        total=total,
        margin=margin,
        spell_cast=spell_cast,
        fatigue_levels_lost=fatigue,
        components=(
            Component("Casting Score", casting_score_total, RITUAL_CITATION),
            Component("Artes Liberales", artes_liberales, RITUAL_CITATION),
            Component("Philosophiae", philosophiae, RITUAL_CITATION),
            Component("Stress Die", die.value, RITUAL_CITATION),
            Component("Spell Level", -spell_level, RITUAL_CITATION),
        ),
        warnings=warnings,
        citations=(RITUAL_CITATION,) + die.citations,
        botched=die.botched,
        botch_count=die.botch_count,
    )


def spontaneous_casting_total(
    *,
    casting_score_total: int,
    die: DieRollResult | None = None,
    exerting: bool,
    rounding: Literal["floor", "ceil", "exact"] = "floor",
) -> AuditResult:
    """Calculate fatiguing or non-fatiguing Spontaneous casting total.

    The rule text states division by 2 or by 5. Rounding is an explicit caller
    decision because this helper does not assume a rounding convention.
    """

    denominator = 2 if exerting else 5
    numerator = casting_score_total + (0 if die is None else die.value)
    if exerting and die is None:
        raise ValueError("Fatiguing spontaneous magic requires a stress die result.")
    if not exerting and die is not None:
        raise ValueError("Non-fatiguing spontaneous magic does not use a die result.")

    exact = Fraction(numerator, denominator)
    if rounding == "exact":
        value = exact
        warnings = ()
    elif rounding == "floor":
        value = exact.numerator // exact.denominator
        warnings = (
            () if exact.denominator == 1 else ("Rounded spontaneous total down by caller policy.",)
        )
    else:
        value = -(-exact.numerator // exact.denominator)
        warnings = (
            () if exact.denominator == 1 else ("Rounded spontaneous total up by caller policy.",)
        )

    components = [Component("Casting Score", casting_score_total, SPONTANEOUS_CITATION)]
    if die is not None:
        components.append(Component("Stress Die", die.value, SPONTANEOUS_CITATION))
    components.append(
        Component(f"Divide by {denominator}", value - numerator, SPONTANEOUS_CITATION)
    )
    return AuditResult(
        value=value,
        components=tuple(components),
        warnings=warnings,
        citations=(SPONTANEOUS_CITATION,) + (() if die is None else die.citations),
        metadata={"exact": exact, "exerting": exerting, "rounding": rounding},
    )


def penetration_bonus(
    *,
    penetration_ability: int,
    multiplier: int = 1,
    multiplier_bonus: int = 0,
) -> AuditResult:
    """Calculate Penetration Ability times Penetration Multiplier."""

    if multiplier < 1:
        raise ValueError("Penetration multiplier must be at least 1.")
    final_multiplier = multiplier + multiplier_bonus
    if final_multiplier < 1:
        raise ValueError("Final Penetration multiplier must be at least 1.")
    return AuditResult(
        value=penetration_ability * final_multiplier,
        components=(
            Component("Penetration Ability", penetration_ability, SYMPATHETIC_CITATION),
            Component("Penetration Multiplier", final_multiplier, SYMPATHETIC_CITATION),
        ),
        warnings=(),
        citations=(SYMPATHETIC_CITATION,),
        metadata={"multiplier": final_multiplier},
    )


def penetration_total(
    *,
    casting_total: int,
    spell_level: int,
    penetration_bonus_total: int,
    magic_resistance: int | None = None,
    forceless: bool = False,
) -> PenetrationOutcome:
    """Calculate Penetration Total and optionally compare Magic Resistance."""

    raw_total = casting_total + penetration_bonus_total - spell_level
    warnings: tuple[str, ...] = ()
    citations = (PENETRATION_CITATION,)
    if forceless and raw_total > 0:
        total = 0
        warnings = ("Forceless casting caps Penetration Total at 0 by caller choice.",)
        citations += (FORCELESS_CITATION,)
    else:
        total = raw_total
    penetrates = None if magic_resistance is None else total > magic_resistance
    return PenetrationOutcome(
        total=total,
        penetrates=penetrates,
        components=(
            Component("Casting Total", casting_total, PENETRATION_CITATION),
            Component("Penetration Bonus", penetration_bonus_total, PENETRATION_CITATION),
            Component("Spell Level", -spell_level, PENETRATION_CITATION),
        ),
        warnings=warnings,
        citations=citations,
    )
