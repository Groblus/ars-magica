from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from generation.generate_views import (
    APPROVED,
    CANDIDATE,
    FULL_RIG,
    QUICK_RIG,
    View,
    merge_manifest,
    nearest_generated,
    ordered_views,
    view_filename,
    view_prompt,
)
from generation.prepare_reconstruction_inputs import prepare_inputs


class GenerateViewsTests(unittest.TestCase):
    def test_ordered_views_starts_with_smallest_camera_moves(self) -> None:
        names = [view.name for view in ordered_views(FULL_RIG)[:4]]
        self.assertEqual(names, ["left_8", "right_8", "low_center", "high_center"])

    def test_view_filename_is_stable(self) -> None:
        self.assertEqual(view_filename(7, View("left_10", -10, 0)), "007_left_10.png")

    def test_prompt_uses_approved_adjacent_reference_language(self) -> None:
        prompt = view_prompt(View("left_10", -10, 0), has_adjacent_reference=True)
        self.assertIn("nearest approved adjacent view", prompt)
        self.assertIn("moved 10 degrees to the left", prompt)

    def test_nearest_generated_uses_camera_distance(self) -> None:
        view = View("target", 12, 0)
        nearest = nearest_generated(view, [View("far", -25, 0), View("near", 10, 0)])
        self.assertIsNotNone(nearest)
        self.assertEqual(nearest.name, "near")

    def test_manifest_merge_preserves_review_state_and_existing_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            existing = {
                "views": [
                    {"name": "left_10", "review_state": APPROVED, "status": "generated", "file": "approved/custom.png"}
                ]
            }
            manifest = merge_manifest(
                existing,
                rig=QUICK_RIG,
                model="model",
                size="1024x1024",
                quality="high",
                hero_path=output / "hero.jpg",
                output=output,
            )
            records = {record["name"]: record for record in manifest["views"]}
            self.assertEqual(records["left_10"]["review_state"], APPROVED)
            self.assertEqual(records["left_10"]["file"], "approved/custom.png")
            self.assertEqual(records["right_10"]["review_state"], CANDIDATE)

    def test_prepare_reconstruction_inputs_only_copies_approved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "approved").mkdir()
            (root / "candidates").mkdir()
            (root / "approved" / "000_hero.jpg").write_bytes(b"hero")
            (root / "approved" / "001_left.png").write_bytes(b"approved")
            (root / "candidates" / "002_right.png").write_bytes(b"candidate")
            manifest = {
                "views": [
                    {"name": "hero", "review_state": "source", "file": "approved/000_hero.jpg"},
                    {"name": "left", "review_state": "approved", "file": "approved/001_left.png"},
                    {"name": "right", "review_state": "candidate", "file": "candidates/002_right.png"},
                ]
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            copied = prepare_inputs(manifest_path, root / "reconstruction-input")
            self.assertEqual([path.name for path in copied], ["000_hero.jpg", "001_left.png"])


if __name__ == "__main__":
    unittest.main()
