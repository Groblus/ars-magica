"""Laboratory total and seasonal progress helpers."""

from __future__ import annotations

from collections.abc import Sequence
from math import ceil

from .audit import AuditResult, Component, audit_sum, cite
from .casting import effective_art_score

LAB_TOTAL_CITATION = cite(10272, 10278)
LAB_SETUP_CITATION = cite(10280, 10284)
VIS_CITATION = cite(10300, 10318)
SPELL_INVENTION_CITATION = cite(10340, 10350)
LAB_SUMMARY_CITATION = cite(23328, 23364)


def lab_total(
    *,
    technique: int,
    form: int,
    intelligence: int,
    magic_theory: int,
    aura_modifier: int = 0,
    technique_requisites: Sequence[int] = (),
    form_requisites: Sequence[int] = (),
    other_modifiers: Sequence[Component] = (),
) -> AuditResult:
    """Calculate Technique + Form + Intelligence + Magic Theory + Aura Modifier."""

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
        Component("Technique", effective_technique.value, LAB_TOTAL_CITATION),
        Component("Form", effective_form.value, LAB_TOTAL_CITATION),
        Component("Intelligence", intelligence, LAB_TOTAL_CITATION),
        Component("Magic Theory", magic_theory, LAB_TOTAL_CITATION),
        Component("Aura Modifier", aura_modifier, LAB_TOTAL_CITATION),
    ) + tuple(other_modifiers)
    return audit_sum(
        components,
        warnings=effective_technique.warnings + effective_form.warnings,
        citations=(LAB_TOTAL_CITATION,),
        metadata={
            "technique_requisites": tuple(technique_requisites),
            "form_requisites": tuple(form_requisites),
        },
    )


def laboratory_setup_penalty(*, seasons_spent_setting_up: int) -> AuditResult:
    """Return the lab total penalty from initial laboratory setup."""

    if seasons_spent_setting_up < 0:
        raise ValueError("seasons_spent_setting_up must be non-negative.")
    penalty = -3 if seasons_spent_setting_up == 1 else 0
    warnings = ()
    if seasons_spent_setting_up == 0:
        warnings = ("No laboratory has been set up, so lab activities may be impossible.",)
    return AuditResult(
        value=penalty,
        components=(Component("Laboratory setup penalty", penalty, LAB_SETUP_CITATION),),
        warnings=warnings,
        citations=(LAB_SETUP_CITATION,),
        metadata={"seasons_spent_setting_up": seasons_spent_setting_up},
    )


def vis_limit(*, magic_theory: int) -> AuditResult:
    """Calculate seasonal vis use limit."""

    return AuditResult(
        value=magic_theory * 2,
        components=(Component("Magic Theory x 2", magic_theory * 2, VIS_CITATION),),
        warnings=(),
        citations=(VIS_CITATION,),
    )


def vis_extraction(*, creo_vim_lab_total: int) -> AuditResult:
    """Calculate Vim vis extracted from a magical aura in one season."""

    pawns = 0 if creo_vim_lab_total <= 0 else ceil(creo_vim_lab_total / 10)
    warnings = ()
    if creo_vim_lab_total <= 0:
        warnings = ("Non-positive Creo Vim Lab Total extracts no vis in this helper.",)
    return AuditResult(
        value=pawns,
        components=(Component("Creo Vim Lab Total / 10 rounded up", pawns, VIS_CITATION),),
        warnings=warnings,
        citations=(VIS_CITATION,),
        metadata={"creo_vim_lab_total": creo_vim_lab_total},
    )


def seasonal_lab_progress(
    *,
    lab_total_value: int,
    project_level: int,
    accumulated: int = 0,
    kind: str = "project",
) -> AuditResult:
    """Calculate points accumulated this season and completion metadata."""

    if project_level < 1:
        raise ValueError("project_level must be at least 1.")
    if accumulated < 0:
        raise ValueError("accumulated must be non-negative.")
    progress = lab_total_value - project_level
    warnings: list[str] = []
    if progress <= 0:
        warnings.append(
            f"Lab Total must exceed {kind} level to make progress under the encoded rule."
        )
        new_total = accumulated
        seasons_remaining = None
    else:
        new_total = accumulated + progress
        remaining = max(project_level - new_total, 0)
        seasons_remaining = ceil(remaining / progress) if remaining else 0
    return AuditResult(
        value=max(progress, 0),
        components=(
            Component("Lab Total", lab_total_value, SPELL_INVENTION_CITATION),
            Component(f"{kind.title()} Level", -project_level, SPELL_INVENTION_CITATION),
        ),
        warnings=tuple(warnings),
        citations=(SPELL_INVENTION_CITATION, LAB_SUMMARY_CITATION),
        metadata={
            "accumulated_before": accumulated,
            "accumulated_after": new_total,
            "complete": new_total >= project_level,
            "seasons_remaining_after_this": seasons_remaining,
        },
    )


def instilled_effect_vis_cost(*, effect_level: int) -> AuditResult:
    """Calculate vis cost for instilling an invested-device effect."""

    if effect_level < 1:
        raise ValueError("effect_level must be at least 1.")
    pawns = ceil(effect_level / 10)
    return AuditResult(
        value=pawns,
        components=(Component("Effect level / 10 rounded up", pawns, LAB_SUMMARY_CITATION),),
        warnings=(),
        citations=(LAB_SUMMARY_CITATION,),
        metadata={"effect_level": effect_level},
    )


def charged_item_charges(*, lab_total_value: int, effect_level: int) -> AuditResult:
    """Calculate charged item charges from Lab Total excess."""

    if effect_level < 1:
        raise ValueError("effect_level must be at least 1.")
    if lab_total_value < effect_level:
        charges = 0
        warnings = ("Lab Total is below effect level, so no charges are created.",)
    elif lab_total_value == effect_level:
        charges = 1
        warnings = ()
    else:
        charges = ceil((lab_total_value - effect_level) / 5)
        warnings = ()
    return AuditResult(
        value=charges,
        components=(
            Component("Lab Total", lab_total_value, LAB_SUMMARY_CITATION),
            Component("Effect Level", -effect_level, LAB_SUMMARY_CITATION),
        ),
        warnings=warnings,
        citations=(LAB_SUMMARY_CITATION,),
    )


def longevity_ritual(
    *,
    creo_corpus_lab_total: int,
    subject_age: int,
) -> AuditResult:
    """Calculate Longevity Ritual bonus and vis cost metadata."""

    if subject_age < 0:
        raise ValueError("subject_age must be non-negative.")
    bonus = 0 if creo_corpus_lab_total <= 0 else ceil(creo_corpus_lab_total / 5)
    vis_cost = ceil(subject_age / 5)
    return AuditResult(
        value=bonus,
        components=(
            Component("Creo Corpus Lab Total / 5 rounded up", bonus, LAB_SUMMARY_CITATION),
        ),
        warnings=(),
        citations=(LAB_SUMMARY_CITATION,),
        metadata={"vis_cost": vis_cost, "subject_age": subject_age},
    )
