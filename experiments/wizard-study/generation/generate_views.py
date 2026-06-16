from __future__ import annotations

import argparse
import base64
import json
import os
import time
from contextlib import ExitStack
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from openai import OpenAI


@dataclass(frozen=True, slots=True)
class View:
    name: str
    yaw_deg: float
    elevation_deg: float
    distance_scale: float = 1.0


QUICK_RIG: tuple[View, ...] = (
    View("hero", 0, 0),
    View("left_10", -10, 0),
    View("right_10", 10, 0),
    View("left_22", -22, 0),
    View("right_22", 22, 0),
    View("high_center", 0, 10),
    View("high_left", -15, 9),
    View("high_right", 15, 9),
)

FULL_RIG: tuple[View, ...] = (
    View("hero", 0, 0),
    View("left_8", -8, 0),
    View("right_8", 8, 0),
    View("left_16", -16, 0),
    View("right_16", 16, 0),
    View("left_26", -26, 0),
    View("right_26", 26, 0),
    View("left_36", -36, 0),
    View("right_36", 36, 0),
    View("high_center", 0, 11),
    View("high_left_14", -14, 10),
    View("high_right_14", 14, 10),
    View("high_left_27", -27, 9),
    View("high_right_27", 27, 9),
    View("low_center", 0, -8),
    View("low_left", -15, -7),
    View("low_right", 15, -7),
    View("close_center", 0, 1, 0.82),
)

SCENE_BIBLE = """
This is one fixed physical scene, not a redesign: a cozy late-medieval wizard-scholar's tower study in southern or central France. The room has warm irregular stone, dark old timber, a large open arched window, an impressive heavy wooden writing desk directly before the window, an open half-written manuscript, a quill resting beside it, a small piece of bread, and tea that suggests the scholar has briefly stepped away. Outside is the same sun-drenched hilly medieval French landscape with fields, trees, a small settlement, and distant ridges. The visual treatment is a refined semi-realistic traditional painting: natural proportions, rich but restrained detail, warm sunlight, harmonious colors, no cartoon stylization, no low-poly appearance, no modern objects.

The identity, dimensions, placement and orientation of every major object are fixed across every view. Keep the exact same desk, open book, quill, bread, window, shelves, walls, landscape landmarks, lighting direction, time of day and weather. Do not add, remove, duplicate or relocate objects. Do not put readable modern text, labels, borders, captions or diagrams into the image. Reveal only the hidden surfaces that a real camera move would expose.
""".strip()


def view_prompt(view: View, has_adjacent_reference: bool) -> str:
    horizontal = (
        "at the canonical central position"
        if view.yaw_deg == 0
        else f"moved {abs(view.yaw_deg):g} degrees to the {'left' if view.yaw_deg < 0 else 'right'} around the open book"
    )
    vertical = (
        "at the canonical eye height"
        if view.elevation_deg == 0
        else f"{abs(view.elevation_deg):g} degrees {'higher' if view.elevation_deg > 0 else 'lower'}"
    )
    distance = (
        "at the same distance"
        if view.distance_scale == 1
        else f"at {view.distance_scale:.2f} times the canonical camera distance, creating a modest forward dolly"
    )
    refs = (
        "Input image 1 is the canonical hero view. Input image 2 is the nearest already-generated adjacent view; use both to preserve geometry."
        if has_adjacent_reference
        else "The input image is the canonical hero view and is the authoritative reference for scene identity and style."
    )
    return f"""
{SCENE_BIBLE}

{refs}
Render a new full-frame view from a perspective camera {horizontal}, {vertical}, and {distance}. The camera continues to look at the centre of the open manuscript on the desk. Use an approximately 48 mm full-frame-equivalent lens with no fisheye distortion. Preserve a coherent vertical axis and realistic parallax. This is viewpoint synthesis of the same room, not an illustration inspired by it.
""".strip()


def ordered_views(rig: Iterable[View]) -> list[View]:
    return sorted(
        (view for view in rig if view.name != "hero"),
        key=lambda v: (abs(v.yaw_deg) + abs(v.elevation_deg), abs(v.yaw_deg), abs(v.elevation_deg)),
    )


def nearest_generated(view: View, generated: list[View]) -> View | None:
    if not generated:
        return None
    return min(
        generated,
        key=lambda other: (
            (view.yaw_deg - other.yaw_deg) ** 2
            + (view.elevation_deg - other.elevation_deg) ** 2
            + ((view.distance_scale - other.distance_scale) * 30) ** 2
        ),
    )


def decode_first_image(response: object) -> bytes:
    data = getattr(response, "data", None)
    if not data or not getattr(data[0], "b64_json", None):
        raise RuntimeError("The image response did not contain base64 image data.")
    return base64.b64decode(data[0].b64_json)


def generate_one(
    client: OpenAI,
    *,
    model: str,
    hero_path: Path,
    adjacent_path: Path | None,
    prompt: str,
    size: str,
    quality: str,
) -> bytes:
    with ExitStack() as stack:
        references = [stack.enter_context(hero_path.open("rb"))]
        if adjacent_path is not None:
            references.append(stack.enter_context(adjacent_path.open("rb")))
        response = client.images.edit(
            model=model,
            image=references,
            prompt=prompt,
            input_fidelity="high",
            size=size,
            quality=quality,
            output_format="png",
            n=1,
        )
    return decode_first_image(response)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate consistent multiview images of one painted room.")
    parser.add_argument("--hero", type=Path, default=Path(__file__).with_name("hero.jpg"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("output"))
    parser.add_argument("--preset", choices=("quick", "full"), default="quick")
    parser.add_argument("--model", default=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"))
    parser.add_argument("--size", default="1120x1408", help="For gpt-image-2, both dimensions must be divisible by 16.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "auto"), default="high")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is missing. Copy .env.example to .env and add your key.")
    if not args.hero.exists():
        raise SystemExit(f"Hero image not found: {args.hero}")

    args.output.mkdir(parents=True, exist_ok=True)
    images_dir = args.output / "images"
    images_dir.mkdir(exist_ok=True)
    hero_output = images_dir / "000_hero.jpg"
    if not hero_output.exists() or args.overwrite:
        hero_output.write_bytes(args.hero.read_bytes())

    rig = QUICK_RIG if args.preset == "quick" else FULL_RIG
    manifest_path = args.output / "manifest.json"
    manifest: dict[str, object] = {
        "model": args.model,
        "size": args.size,
        "quality": args.quality,
        "hero_source": str(args.hero.resolve()),
        "scene_bible": SCENE_BIBLE,
        "views": [
            {
                **asdict(rig[0]),
                "file": str(hero_output.relative_to(args.output)),
                "status": "source",
                "reference": None,
            }
        ],
    }

    client = OpenAI()
    generated: list[View] = []
    generated_paths: dict[str, Path] = {}

    for index, view in enumerate(ordered_views(rig), start=1):
        output_path = images_dir / f"{index:03d}_{view.name}.png"
        adjacent = nearest_generated(view, generated)
        adjacent_path = generated_paths.get(adjacent.name) if adjacent else None
        prompt = view_prompt(view, adjacent_path is not None)

        record = {
            **asdict(view),
            "file": str(output_path.relative_to(args.output)),
            "reference": adjacent.name if adjacent else None,
            "prompt": prompt,
            "status": "pending",
        }

        if output_path.exists() and not args.overwrite:
            print(f"skip {view.name}: {output_path} exists")
            record["status"] = "existing"
            generated.append(view)
            generated_paths[view.name] = output_path
            manifest["views"].append(record)  # type: ignore[union-attr]
            continue

        for attempt in range(1, args.max_retries + 1):
            try:
                print(f"generate {view.name} (attempt {attempt}/{args.max_retries})")
                content = generate_one(
                    client,
                    model=args.model,
                    hero_path=hero_output,
                    adjacent_path=adjacent_path,
                    prompt=prompt,
                    size=args.size,
                    quality=args.quality,
                )
                output_path.write_bytes(content)
                record["status"] = "generated"
                generated.append(view)
                generated_paths[view.name] = output_path
                break
            except Exception as exc:
                record["status"] = "failed"
                record["error"] = repr(exc)
                if attempt == args.max_retries:
                    print(f"failed {view.name}: {exc}")
                else:
                    delay = 2 ** attempt
                    print(f"retrying in {delay}s after: {exc}")
                    time.sleep(delay)

        manifest["views"].append(record)  # type: ignore[union-attr]
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {manifest_path}")
    print("Review the images and remove inconsistent views before reconstruction.")


if __name__ == "__main__":
    main()
