import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ars_magica.rules.casting import (
    casting_score,
    formulaic_casting_total,
    penetration_bonus,
    penetration_total,
    ritual_casting_total,
)
from ars_magica.rules.dice import simple_die, stress_die
from ars_magica.rules.spells import (
    RequisiteDecision,
    adjust_spell_level,
    construct_spell_level,
    spell_magnitude,
    validate_spell_constraints,
)


def test_casting_score_uses_requisite_lower_form():
    score = casting_score(
        technique=12,
        form=13,
        stamina=2,
        aura_modifier=3,
        form_requisites=[6],
    )

    assert score.value == 23
    assert score.warnings == ("Form score limited by the lowest applicable requisite.",)
    assert "reviewed/Ars Magica - Definitive Edition (Core Rules).md:12309-12313" in score.citations


def test_formulaic_casting_success_fatigue_and_failure_thresholds():
    clean_success = formulaic_casting_total(
        casting_score_total=20,
        die=simple_die(roll=0),
        spell_level=30,
    )
    fatigued_success = formulaic_casting_total(
        casting_score_total=19,
        die=simple_die(roll=0),
        spell_level=30,
    )
    failure = formulaic_casting_total(
        casting_score_total=18,
        die=simple_die(roll=1),
        spell_level=30,
    )

    assert clean_success.spell_cast is True
    assert clean_success.fatigue_levels_lost == 0
    assert fatigued_success.spell_cast is True
    assert fatigued_success.fatigue_levels_lost == 1
    assert failure.spell_cast is False
    assert failure.fatigue_levels_lost == 1


def test_formulaic_casting_botch_sets_casting_total_to_zero():
    botch = stress_die(rolls=[0], botch_rolls=[0], botch_dice=1)
    positive_score = formulaic_casting_total(
        casting_score_total=20,
        die=botch,
        spell_level=5,
    )
    negative_score = formulaic_casting_total(
        casting_score_total=-5,
        die=botch,
        spell_level=5,
    )

    for result in (positive_score, negative_score):
        assert result.total == 0
        assert result.margin == -5
        assert result.spell_cast is False
        assert result.fatigue_levels_lost == 0
        assert result.botched is True
        assert result.botch_count == 1
        assert "reviewed/Ars Magica - Definitive Edition (Core Rules).md:9093-9093" in (
            result.citations
        )


def test_ritual_casting_uses_artes_liberales_and_philosophiae():
    result = ritual_casting_total(
        casting_score_total=20,
        artes_liberales=2,
        philosophiae=3,
        die=stress_die(rolls=[4], botch_dice=1),
        spell_level=30,
    )

    assert result.total == 29
    assert result.margin == -1
    assert result.spell_cast is True
    assert result.fatigue_levels_lost == 2


def test_penetration_total_and_forceless_casting():
    bonus = penetration_bonus(penetration_ability=3, multiplier=1, multiplier_bonus=2)
    result = penetration_total(
        casting_total=35,
        penetration_bonus_total=int(bonus.value),
        spell_level=20,
        magic_resistance=20,
    )
    forceless = penetration_total(
        casting_total=35,
        penetration_bonus_total=int(bonus.value),
        spell_level=20,
        magic_resistance=0,
        forceless=True,
    )

    assert bonus.value == 9
    assert result.total == 24
    assert result.penetrates is True
    assert forceless.total == 0
    assert forceless.penetrates is False


def test_spell_magnitude_rounds_up():
    assert spell_magnitude(1).value == 1
    assert spell_magnitude(5).value == 1
    assert spell_magnitude(6).value == 2


def test_adjust_spell_level_matches_core_variant_examples():
    raised = adjust_spell_level(15, 2)
    lowered = adjust_spell_level(15, -5)

    assert raised.value == 25
    assert lowered.value == 2


def test_construct_spell_level_from_base_and_rdt_requisites():
    result = construct_spell_level(
        base_level=3,
        range_name="Voice",
        duration_name="Sun",
        target_name="Group",
        requisites=(RequisiteDecision("Rego", "enhancing", 1),),
    )

    assert result.metadata["magnitude_delta"] == 7
    assert result.value == 30
    assert not result.warnings


def test_construct_spell_level_warns_for_undecided_requisite():
    result = construct_spell_level(
        base_level=10,
        requisites=(RequisiteDecision("Animal", "undecided", 0),),
    )

    assert result.value == 10
    assert "undecided" in result.warnings[0]


def test_ritual_constraints_are_reported_without_guessing():
    validation = validate_spell_constraints(
        level=55,
        duration_name="Year",
        target_name="Boundary",
        ritual=False,
    )
    ritual_level = construct_spell_level(
        base_level=5,
        ritual=True,
    )

    assert validation.valid is False
    assert len(validation.warnings) == 3
    assert ritual_level.value == 20
