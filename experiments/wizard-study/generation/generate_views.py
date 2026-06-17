from __future__ import annotations

import argparse
import base64
import json
import os
import time
from contextlib import ExitStack
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


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

CANDIDATE = "candidate"
APPROVED = "approved"
REJECTED = "rejected"
SOURCE = "source"
PLANNED = "planned"
GENERATED = "generated"
EXISTING = "existing"
FAILED = "failed"


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
        "Input image 1 is the canonical hero view. Input image 2 is the nearest approved adjacent view; use both to preserve geometry."
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
        key=lambda v: (
            abs(v.distance_scale - 1.0) > 0,
            abs(v.yaw_deg) + abs(v.elevation_deg),
            v.yaw_deg == 0,
            abs(v.yaw_deg),
            abs(v.elevation_deg),
            v.name,
        ),
    )


def view_filename(index: int, view: View, suffix: str = ".png") -> str:
    return f"{index:03d}_{view.name}{suffix}"


def view_from_record(record: dict[str, Any]) -> View:
    return View(
        str(record["name"]),
        float(record["yaw_deg"]),
        float(record["elevation_deg"]),
        float(record.get("distance_scale", 1.0)),
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


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"views": []}
    return json.loads(path.read_text(encoding="utf-8"))


def records_by_name(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in manifest.get("views", []):
        if isinstance(record, dict) and record.get("name"):
            result[str(record["name"])] = record
    return result


def approved_records(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in manifest.get("views", [])
        if isinstance(record, dict) and record.get("review_state") in {SOURCE, APPROVED}
    ]


def approved_views(manifest: dict[str, Any]) -> list[View]:
    return [view_from_record(record) for record in approved_records(manifest) if "yaw_deg" in record]


def merge_manifest(
    existing: dict[str, Any],
    *,
    rig: tuple[View, ...],
    model: str,
    size: str,
    quality: str,
    hero_path: Path,
    output: Path,
) -> dict[str, Any]:
    by_name = records_by_name(existing)
    views: list[dict[str, Any]] = []
    hero_file = "approved/000_hero.jpg"

    hero_record = dict(by_name.get("hero", {}))
    hero_record.update(
        {
            **asdict(rig[0]),
            "file": hero_record.get("file", hero_file),
            "status": hero_record.get("status", SOURCE),
            "review_state": SOURCE,
            "reference": None,
        }
    )
    views.append(hero_record)

    generated_refs: list[View] = approved_views(existing)
    if not generated_refs:
        generated_refs = [rig[0]]

    for index, view in enumerate(ordered_views(rig), start=1):
        old = dict(by_name.get(view.name, {}))
        if old.get("review_state") in {APPROVED, REJECTED}:
            review_state = old["review_state"]
        else:
            review_state = CANDIDATE
        adjacent = nearest_generated(view, generated_refs)
        has_reference = adjacent is not None and adjacent.name != "hero"
        record = {
            **old,
            **asdict(view),
            "file": old.get("file", f"candidates/{view_filename(index, view)}"),
            "reference": old.get("reference", adjacent.name if has_reference else None),
            "prompt": view_prompt(view, has_reference),
            "status": old.get("status", PLANNED),
            "review_state": review_state,
        }
        views.append(record)

    return {
        **existing,
        "model": model,
        "size": size,
        "quality": quality,
        "hero_source": str(hero_path.resolve()),
        "scene_bible": SCENE_BIBLE,
        "output_root": str(output.resolve()),
        "views": views,
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def decode_first_image(response: object) -> bytes:
    data = getattr(response, "data", None)
    if not data or not getattr(data[0], "b64_json", None):
        raise RuntimeError("The image response did not contain base64 image data.")
    return base64.b64decode(data[0].b64_json)


def generate_one(
    client: object,
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


def ensure_dirs(output: Path) -> None:
    for dirname in ("approved", "candidates", "rejected"):
        (output / dirname).mkdir(parents=True, exist_ok=True)


def resolve_existing_file(output: Path, record: dict[str, Any]) -> Path | None:
    file_value = record.get("file")
    if not file_value:
        return None
    path = output / str(file_value)
    return path if path.exists() else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or plan consistent multiview images of one painted room.")
    parser.add_argument("--hero", type=Path, default=Path(__file__).with_name("hero.jpg"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("output"))
    parser.add_argument("--preset", choices=("quick", "full"), default="quick")
    parser.add_argument("--model", default=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"))
    parser.add_argument("--size", default="1120x1408", help="For gpt-image-2, both dimensions must be divisible by 16.")
    parser.add_argument("--quality", choices=("low", "medium", "high", "auto"), default="high")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Plan manifest records without requiring API keys or making network calls.")
    args = parser.parse_args()

    if not args.dry_run:
        from dotenv import load_dotenv
        from openai import OpenAI

        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            raise SystemExit("OPENAI_API_KEY is missing. Use --dry-run for planning without paid image calls.")
        if not args.hero.exists():
            raise SystemExit(f"Hero image not found: {args.hero}")
        client = OpenAI()
    else:
        client = None

    args.output.mkdir(parents=True, exist_ok=True)
    ensure_dirs(args.output)

    rig = QUICK_RIG if args.preset == "quick" else FULL_RIG
    manifest_path = args.output / "manifest.json"
    existing = load_manifest(manifest_path)
    manifest = merge_manifest(
        existing,
        rig=rig,
        model=args.model,
        size=args.size,
        quality=args.quality,
        hero_path=args.hero,
        output=args.output,
    )

    hero_output = args.output / "approved" / "000_hero.jpg"
    if args.hero.exists() and (not hero_output.exists() or args.overwrite):
        hero_output.write_bytes(args.hero.read_bytes())

    if args.dry_run:
        write_manifest(manifest_path, manifest)
        print(f"dry-run wrote {manifest_path}")
        print("No API key required and no image generation performed.")
        return

    generated = approved_views(manifest)
    approved_by_name = records_by_name({"views": approved_records(manifest)})

    for record in manifest["views"]:
        if record["name"] == "hero" or record.get("review_state") == REJECTED:
            continue
        if record.get("review_state") == APPROVED:
            continue

        view = view_from_record(record)
        output_path = args.output / record["file"]
        adjacent = nearest_generated(view, generated)
        adjacent_record = approved_by_name.get(adjacent.name) if adjacent else None
        adjacent_path = resolve_existing_file(args.output, adjacent_record) if adjacent_record else None

        if output_path.exists() and not args.overwrite:
            print(f"skip {view.name}: {output_path} exists")
            record["status"] = EXISTING
            continue

        for attempt in range(1, args.max_retries + 1):
            try:
                print(f"generate {view.name} (attempt {attempt}/{args.max_retries})")
                content = generate_one(
                    client,
                    model=args.model,
                    hero_path=hero_output,
                    adjacent_path=adjacent_path,
                    prompt=record["prompt"],
                    size=args.size,
                    quality=args.quality,
                )
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(content)
                record["status"] = GENERATED
                break
            except Exception as exc:
                record["status"] = FAILED
                record["error"] = repr(exc)
                if attempt == args.max_retries:
                    print(f"failed {view.name}: {exc}")
                else:
                    delay = 2**attempt
                    print(f"retrying in {delay}s after: {exc}")
                    time.sleep(delay)
        write_manifest(manifest_path, manifest)

    write_manifest(manifest_path, manifest)
    print(f"wrote {manifest_path}")
    print("Review candidates, then set review_state to approved or rejected before reconstruction.")


if __name__ == "__main__":
    main()
