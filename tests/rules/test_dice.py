import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ars_magica.rules.dice import apply_die_to_modifier, simple_die, stress_die


def test_simple_die_zero_counts_as_ten():
    result = simple_die(roll=0)

    assert result.value == 10
    assert result.botched is False
    assert "reviewed/Ars Magica - Definitive Edition (Core Rules).md:468-520" in result.citations


def test_stress_die_doubles_each_one_until_terminal_roll():
    result = stress_die(rolls=[1, 1, 5], botch_dice=1)

    assert result.value == 20
    assert result.botched is False
    assert [entry.roll for entry in result.trace] == [1, 1, 5]
    total = apply_die_to_modifier(modifier=9, die=result)
    assert total.value == 29


def test_stress_zero_without_botch_adds_zero():
    result = stress_die(rolls=[0], botch_rolls=[7], botch_dice=1)

    assert result.value == 0
    assert result.botched is False
    assert result.botch_count == 0
    total = apply_die_to_modifier(modifier=9, die=result)
    assert total.value == 9


def test_stress_zero_with_botch_caps_positive_total_at_zero():
    result = stress_die(rolls=[0], botch_rolls=[0, 4, 0], botch_dice=3)

    assert result.value == 0
    assert result.botched is True
    assert result.botch_count == 2
    total = apply_die_to_modifier(modifier=9, die=result)
    assert total.value == 0
    assert total.metadata["botch_count"] == 2
    assert total.warnings


def test_seeded_stress_die_is_reproducible():
    first = stress_die(seed=17, botch_dice=2)
    second = stress_die(seed=17, botch_dice=2)

    assert first.value == second.value
    assert first.trace == second.trace
