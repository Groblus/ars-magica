"""Deterministic simple and stress dice for Ars Magica."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Literal, Sequence

from .audit import AuditResult, Component, cite


DICE_CITATION = cite(468, 520)


@dataclass(frozen=True)
class RollTraceEntry:
    """One physical die in a roll trace."""

    kind: Literal["simple", "stress_initial", "stress_reroll", "botch"]
    roll: int
    value: int
    multiplier: int = 1


@dataclass(frozen=True)
class DieRollResult:
    """A die result with full trace and botch information."""

    value: int
    botched: bool
    botch_count: int
    trace: tuple[RollTraceEntry, ...]
    components: tuple[Component, ...]
    warnings: tuple[str, ...]
    citations: tuple[str, ...]


class _RollSource:
    def __init__(self, supplied: Sequence[int], rng: Random | None) -> None:
        self._supplied = tuple(supplied)
        self._index = 0
        self._rng = rng

    def take(self) -> int:
        if self._index < len(self._supplied):
            roll = self._supplied[self._index]
            self._index += 1
        elif self._rng is not None:
            roll = self._rng.randrange(10)
        else:
            raise ValueError("Not enough supplied rolls and no seed was provided.")
        if roll < 0 or roll > 9:
            raise ValueError(f"Ars Magica dice are ten-sided and use rolls 0-9, got {roll}.")
        return roll


def simple_die(*, roll: int | None = None, seed: int | None = None) -> DieRollResult:
    """Resolve a simple die; 0 counts as 10."""

    supplied = () if roll is None else (roll,)
    source = _RollSource(supplied, None if seed is None else Random(seed))
    raw = source.take()
    value = 10 if raw == 0 else raw
    trace = (RollTraceEntry(kind="simple", roll=raw, value=value),)
    return DieRollResult(
        value=value,
        botched=False,
        botch_count=0,
        trace=trace,
        components=(Component("simple die", value, DICE_CITATION),),
        warnings=(),
        citations=(DICE_CITATION,),
    )


def stress_die(
    *,
    rolls: Sequence[int] = (),
    botch_rolls: Sequence[int] = (),
    botch_dice: int = 1,
    can_botch: bool = True,
    seed: int | None = None,
) -> DieRollResult:
    """Resolve a stress die from explicit rolls or a seeded RNG.

    The ``rolls`` sequence supplies the initial stress die and any rerolls caused
    by initial or subsequent 1s. The ``botch_rolls`` sequence supplies botch dice
    when the initial stress roll is 0. If either sequence is exhausted, ``seed``
    supplies remaining dice deterministically.
    """

    if botch_dice < 0:
        raise ValueError("botch_dice must be non-negative.")

    rng = None if seed is None else Random(seed)
    source = _RollSource(rolls, rng)
    botch_source = _RollSource(botch_rolls, rng)
    trace: list[RollTraceEntry] = []
    warnings: list[str] = []

    initial = source.take()
    trace.append(RollTraceEntry(kind="stress_initial", roll=initial, value=initial))

    if initial == 0:
        if not can_botch or botch_dice == 0:
            if not can_botch:
                warnings.append("This stress roll was marked as unable to botch.")
            if botch_dice == 0:
                warnings.append("No botch dice were supplied, so the roll cannot botch.")
            return DieRollResult(
                value=0,
                botched=False,
                botch_count=0,
                trace=tuple(trace),
                components=(Component("stress die", 0, DICE_CITATION),),
                warnings=tuple(warnings),
                citations=(DICE_CITATION,),
            )

        botch_count = 0
        for _ in range(botch_dice):
            raw = botch_source.take()
            if raw == 0:
                botch_count += 1
            trace.append(RollTraceEntry(kind="botch", roll=raw, value=raw))
        return DieRollResult(
            value=0,
            botched=botch_count > 0,
            botch_count=botch_count,
            trace=tuple(trace),
            components=(Component("stress die", 0, DICE_CITATION),),
            warnings=tuple(warnings),
            citations=(DICE_CITATION,),
        )

    if initial != 1:
        return DieRollResult(
            value=initial,
            botched=False,
            botch_count=0,
            trace=tuple(trace),
            components=(Component("stress die", initial, DICE_CITATION),),
            warnings=(),
            citations=(DICE_CITATION,),
        )

    multiplier = 2
    while True:
        raw = source.take()
        if raw == 1:
            trace.append(
                RollTraceEntry(
                    kind="stress_reroll",
                    roll=raw,
                    value=0,
                    multiplier=multiplier,
                )
            )
            multiplier *= 2
            continue
        reroll_value = 10 if raw == 0 else raw
        value = reroll_value * multiplier
        trace.append(
            RollTraceEntry(
                kind="stress_reroll",
                roll=raw,
                value=value,
                multiplier=multiplier,
            )
        )
        return DieRollResult(
            value=value,
            botched=False,
            botch_count=0,
            trace=tuple(trace),
            components=(Component("stress die", value, DICE_CITATION),),
            warnings=(),
            citations=(DICE_CITATION,),
        )


def apply_die_to_modifier(*, modifier: int, die: DieRollResult) -> AuditResult:
    """Apply a die result to a fixed modifier, including botch total handling."""

    if die.botched:
        total = min(0, modifier)
        warnings = (
            "The roll botched; consequences beyond the capped total require storyguide adjudication.",
        )
    else:
        total = modifier + die.value
        warnings = ()
    return AuditResult(
        value=total,
        components=(
            Component("modifier", modifier, DICE_CITATION),
            Component("die", die.value, DICE_CITATION),
        ),
        warnings=warnings + die.warnings,
        citations=(DICE_CITATION,),
        metadata={"botched": die.botched, "botch_count": die.botch_count, "trace": die.trace},
    )
