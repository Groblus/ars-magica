from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ars_magica.rules.advancement import (
    adventure_source_quality,
    advancement_total,
    apply_experience,
    exposure_source_quality,
    score_from_xp,
    teaching_source_quality,
    training_source_quality,
    validate_adventure_allocations,
    validate_single_xp_source,
    xp_to_buy_score,
    xp_to_raise_next,
)
from ars_magica.rules.audit import Component
from ars_magica.rules.laboratory import (
    charged_item_charges,
    instilled_effect_vis_cost,
    lab_total,
    laboratory_setup_penalty,
    longevity_ritual,
    seasonal_lab_progress,
    vis_extraction,
    vis_limit,
)
from ars_magica.rules.validation import validate_non_negative_scores


def test_lab_total_matches_inventing_spells_example_components():
    total = lab_total(
        technique=5,
        form=5,
        intelligence=5,
        magic_theory=3,
        aura_modifier=5,
        other_modifiers=(Component("Puissant Magic Theory", 2),),
    )

    assert total.value == 25
    assert "reviewed/Ars Magica - Definitive Edition (Core Rules).md:10272-10278" in total.citations


def test_seasonal_lab_progress_reports_completion_metadata():
    first = seasonal_lab_progress(lab_total_value=25, project_level=20, kind="spell")
    fourth = seasonal_lab_progress(
        lab_total_value=25,
        project_level=20,
        accumulated=15,
        kind="spell",
    )

    assert first.value == 5
    assert first.metadata["complete"] is False
    assert first.metadata["seasons_remaining_after_this"] == 3
    assert fourth.metadata["complete"] is True
    assert fourth.metadata["accumulated_after"] == 20


def test_lab_progress_warns_when_lab_total_does_not_exceed_level():
    result = seasonal_lab_progress(lab_total_value=20, project_level=20, kind="spell")

    assert result.value == 0
    assert result.metadata["complete"] is False
    assert result.warnings


def test_vis_and_lab_helpers():
    assert laboratory_setup_penalty(seasons_spent_setting_up=1).value == -3
    assert vis_limit(magic_theory=4).value == 8
    assert vis_extraction(creo_vim_lab_total=21).value == 3
    assert instilled_effect_vis_cost(effect_level=21).value == 3
    assert charged_item_charges(lab_total_value=30, effect_level=21).value == 2
    ritual = longevity_ritual(creo_corpus_lab_total=31, subject_age=37)
    assert ritual.value == 7
    assert ritual.metadata["vis_cost"] == 8


def test_xp_tables_for_arts_and_abilities():
    assert xp_to_buy_score("art", 5).value == 15
    assert xp_to_buy_score("ability", 5).value == 75
    assert xp_to_raise_next("art", 5).value == 6
    assert xp_to_raise_next("ability", 5).value == 30
    assert score_from_xp("ability", 80).score == 5
    assert score_from_xp("ability", 80).xp_into_score == 5


def test_advancement_total_and_xp_application_with_gain_limit():
    total = advancement_total(source_quality=10, virtue_bonus=3, flaw_penalty=1)
    capped = apply_experience(kind="art", current_xp=14, gained_xp=int(total.value), gain_limit=5)

    assert total.value == 12
    assert capped.total_xp == 15
    assert capped.score == 5
    assert capped.warnings


def test_source_quality_helpers_and_validators():
    assert exposure_source_quality(split_between_subjects=2).value == 1
    assert adventure_source_quality(quality=4).warnings
    assert training_source_quality(master_score=1).warnings
    assert teaching_source_quality(communication=2, teaching=4, single_student_bonus=6).value == 15

    adventure = validate_adventure_allocations(
        allocations={"Awareness": 5, "Latin": 5},
        source_quality=10,
    )
    too_much = validate_adventure_allocations(
        allocations={"Awareness": 6, "Latin": 4},
        source_quality=10,
    )
    one_source = validate_single_xp_source(source_count=1)
    two_sources = validate_single_xp_source(source_count=2)

    assert adventure.valid is True
    assert too_much.valid is False
    assert one_source.valid is True
    assert two_sources.valid is False


def test_non_negative_score_validator():
    result = validate_non_negative_scores({"Creo": 5, "Vim": -1})

    assert result.valid is False
    assert result.warnings == ("Vim is negative.",)
