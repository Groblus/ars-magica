"""Command-line tools for deterministic mechanics and printable materials."""

from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
from fractions import Fraction
import json
from pathlib import Path
from typing import Any, Sequence

from .rules import (
    adventure_source_quality,
    advancement_total,
    apply_experience,
    exposure_source_quality,
    practice_source_quality,
    score_from_xp,
    simple_die,
    stress_die,
    teaching_source_quality,
    training_source_quality,
    xp_to_buy_score,
)
from .publishing import (
    inspect_template_requirements,
    list_templates,
    package_material,
    render_html,
)


def _parse_int_list(value: str | None) -> list[int]:
    if not value:
        return []
    return [int(part.strip()) for part in value.split(",") if part.strip()]


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


def _emit(value: Any, *, as_json: bool = True) -> None:
    if as_json:
        print(json.dumps(_jsonable(value), ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(value)


def _read_spec(path: str) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dice_simple(args: argparse.Namespace) -> int:
    _emit(simple_die(roll=args.roll, seed=args.seed), as_json=True)
    return 0


def dice_stress(args: argparse.Namespace) -> int:
    _emit(
        stress_die(
            rolls=_parse_int_list(args.rolls),
            botch_rolls=_parse_int_list(args.botch_rolls),
            botch_dice=args.botch_dice,
            can_botch=not args.no_botch,
            seed=args.seed,
        ),
        as_json=True,
    )
    return 0


def advancement_xp_to_score(args: argparse.Namespace) -> int:
    _emit(xp_to_buy_score(args.kind, args.score), as_json=True)
    return 0


def advancement_score_progress(args: argparse.Namespace) -> int:
    _emit(score_from_xp(args.kind, args.total_xp), as_json=True)
    return 0


def advancement_apply_experience(args: argparse.Namespace) -> int:
    _emit(
        apply_experience(
            kind=args.kind,
            current_xp=args.current_xp,
            gained_xp=args.gained_xp,
            gain_limit=args.gain_limit,
        ),
        as_json=True,
    )
    return 0


def advancement_total_command(args: argparse.Namespace) -> int:
    _emit(
        advancement_total(
            source_quality=args.source_quality,
            virtue_bonus=args.virtue_bonus,
            flaw_penalty=args.flaw_penalty,
            other_modifier=args.other_modifier,
        ),
        as_json=True,
    )
    return 0


def advancement_exposure(args: argparse.Namespace) -> int:
    _emit(exposure_source_quality(split_between_subjects=args.split_between_subjects), as_json=True)
    return 0


def advancement_practice(args: argparse.Namespace) -> int:
    _emit(practice_source_quality(quality=args.quality), as_json=True)
    return 0


def advancement_training(args: argparse.Namespace) -> int:
    _emit(training_source_quality(master_score=args.master_score), as_json=True)
    return 0


def advancement_teaching(args: argparse.Namespace) -> int:
    _emit(
        teaching_source_quality(
            communication=args.communication,
            teaching=args.teaching,
            single_student_bonus=args.single_student_bonus,
        ),
        as_json=True,
    )
    return 0


def advancement_adventure(args: argparse.Namespace) -> int:
    _emit(adventure_source_quality(quality=args.quality), as_json=True)
    return 0


def templates_list(args: argparse.Namespace) -> int:
    _emit(list_templates(), as_json=True)
    return 0


def templates_inspect(args: argparse.Namespace) -> int:
    _emit(inspect_template_requirements(args.template), as_json=True)
    return 0


def render_html_command(args: argparse.Namespace) -> int:
    html = render_html(_read_spec(args.spec))
    if args.output:
        Path(args.output).write_text(html, encoding="utf-8")
        _emit({"output": str(Path(args.output))}, as_json=True)
    else:
        print(html)
    return 0


def package_command(args: argparse.Namespace) -> int:
    path = package_material(_read_spec(args.spec), args.destination, include_pdf=args.include_pdf)
    _emit({"package": str(path)}, as_json=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ars-magica",
        description="Deterministic Ars Magica mechanics and publishing utilities.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    dice = subcommands.add_parser("dice", help="Roll simple or stress dice.")
    dice_commands = dice.add_subparsers(dest="dice_command", required=True)

    simple = dice_commands.add_parser("simple", help="Roll a simple die; 0 counts as 10.")
    simple.add_argument("--roll", type=int, choices=range(0, 10), metavar="0-9")
    simple.add_argument("--seed", type=int)
    simple.set_defaults(func=dice_simple)

    stress = dice_commands.add_parser("stress", help="Roll a stress die with optional botch dice.")
    stress.add_argument("--rolls", help="Comma-separated stress rolls, e.g. 1,1,5.")
    stress.add_argument("--botch-rolls", help="Comma-separated botch rolls used after an initial 0.")
    stress.add_argument("--botch-dice", type=int, default=1)
    stress.add_argument("--no-botch", action="store_true", help="Treat the stress roll as unable to botch.")
    stress.add_argument("--seed", type=int)
    stress.set_defaults(func=dice_stress)

    advancement = subcommands.add_parser(
        "advancement",
        help="Calculate seasonal advancement and experience results.",
    )
    advancement_commands = advancement.add_subparsers(dest="advancement_command", required=True)

    xp_to_score = advancement_commands.add_parser("xp-to-score", help="Calculate XP needed to buy a score from zero.")
    xp_to_score.add_argument("kind", choices=("art", "ability"))
    xp_to_score.add_argument("score", type=int)
    xp_to_score.set_defaults(func=advancement_xp_to_score)

    score_progress = advancement_commands.add_parser("score-progress", help="Derive score and next-score progress from total XP.")
    score_progress.add_argument("kind", choices=("art", "ability"))
    score_progress.add_argument("total_xp", type=int)
    score_progress.set_defaults(func=advancement_score_progress)

    apply_xp = advancement_commands.add_parser("apply-xp", help="Apply XP to a score, optionally capped by source level.")
    apply_xp.add_argument("kind", choices=("art", "ability"))
    apply_xp.add_argument("current_xp", type=int)
    apply_xp.add_argument("gained_xp", type=int)
    apply_xp.add_argument("--gain-limit", type=int)
    apply_xp.set_defaults(func=advancement_apply_experience)

    total = advancement_commands.add_parser("total", help="Calculate an advancement total from source quality and modifiers.")
    total.add_argument("source_quality", type=int)
    total.add_argument("--virtue-bonus", type=int, default=0)
    total.add_argument("--flaw-penalty", type=int, default=0)
    total.add_argument("--other-modifier", type=int, default=0)
    total.set_defaults(func=advancement_total_command)

    exposure = advancement_commands.add_parser("exposure", help="Calculate Exposure Source Quality per subject.")
    exposure.add_argument("--split-between-subjects", type=int, choices=(1, 2), default=1)
    exposure.set_defaults(func=advancement_exposure)

    practice = advancement_commands.add_parser("practice", help="Return Practice Source Quality.")
    practice.add_argument("--quality", type=int, default=4)
    practice.set_defaults(func=advancement_practice)

    training = advancement_commands.add_parser("training", help="Calculate Training Source Quality and gain limit.")
    training.add_argument("master_score", type=int)
    training.set_defaults(func=advancement_training)

    teaching = advancement_commands.add_parser("teaching", help="Calculate Teaching Source Quality.")
    teaching.add_argument("communication", type=int)
    teaching.add_argument("teaching", type=int)
    teaching.add_argument("--single-student-bonus", type=int, choices=(0, 3, 6), default=0)
    teaching.set_defaults(func=advancement_teaching)

    adventure = advancement_commands.add_parser("adventure", help="Return Adventure Source Quality with range warnings.")
    adventure.add_argument("quality", type=int)
    adventure.set_defaults(func=advancement_adventure)

    templates = subcommands.add_parser("templates", help="Discover printable material templates.")
    template_commands = templates.add_subparsers(dest="template_command", required=True)
    template_list = template_commands.add_parser("list", help="List available templates.")
    template_list.set_defaults(func=templates_list)
    template_inspect = template_commands.add_parser("inspect", help="Inspect one template contract.")
    template_inspect.add_argument("template")
    template_inspect.set_defaults(func=templates_inspect)

    render = subcommands.add_parser("render-html", help="Render a material spec JSON file to HTML.")
    render.add_argument("spec")
    render.add_argument("-o", "--output")
    render.set_defaults(func=render_html_command)

    package = subcommands.add_parser("package", help="Package a material spec as a deterministic ZIP.")
    package.add_argument("spec")
    package.add_argument("destination")
    package.add_argument("--include-pdf", action="store_true", help="Include PDF output; requires WeasyPrint.")
    package.set_defaults(func=package_command)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
