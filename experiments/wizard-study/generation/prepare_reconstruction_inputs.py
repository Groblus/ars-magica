from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


def approved_image_records(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in manifest.get("views", [])
        if isinstance(record, dict)
        and record.get("review_state") in {"source", "approved"}
        and record.get("file")
    ]


def prepare_inputs(manifest_path: Path, output_dir: Path, *, clean: bool = False) -> list[Path]:
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    if clean:
        for path in output_dir.iterdir():
            if path.is_file():
                path.unlink()
    copied: list[Path] = []
    for index, record in enumerate(approved_image_records(manifest)):
        source = root / str(record["file"])
        if not source.exists():
            raise FileNotFoundError(f"Approved source missing: {source}")
        suffix = source.suffix.lower() or ".png"
        target = output_dir / f"{index:03d}_{record['name']}{suffix}"
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy only approved wizard-study views into reconstruction input.")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("output") / "manifest.json")
    parser.add_argument("--output", type=Path, default=Path(__file__).parents[1] / "reconstruction" / "input")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    copied = prepare_inputs(args.manifest, args.output, clean=args.clean)
    print(f"copied {len(copied)} approved image(s) to {args.output}")


if __name__ == "__main__":
    main()
