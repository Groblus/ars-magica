"""Integration coverage for the advancement CLI and MCP adapters."""

from __future__ import annotations

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ars_magica.cli import main

FAST_MCP_AVAILABLE = importlib.util.find_spec("fastmcp") is not None
if FAST_MCP_AVAILABLE:
    server_path = Path(__file__).resolve().parents[2] / "mcp" / "ars_magica_server.py"
    server_spec = importlib.util.spec_from_file_location("ars_magica_mcp_server", server_path)
    assert server_spec is not None and server_spec.loader is not None
    server_module = importlib.util.module_from_spec(server_spec)
    server_spec.loader.exec_module(server_module)
    apply_advancement_experience = server_module.apply_advancement_experience.fn
    calculate_adventure_source_quality = server_module.calculate_adventure_source_quality.fn
    calculate_advancement_total = server_module.calculate_advancement_total.fn
    calculate_exposure_source_quality = server_module.calculate_exposure_source_quality.fn
    calculate_practice_source_quality = server_module.calculate_practice_source_quality.fn
    calculate_score_progress = server_module.calculate_score_progress.fn
    calculate_teaching_source_quality = server_module.calculate_teaching_source_quality.fn
    calculate_training_source_quality = server_module.calculate_training_source_quality.fn
    calculate_xp_to_buy_score = server_module.calculate_xp_to_buy_score.fn


class AdvancementCliIntegrationTests(unittest.TestCase):
    def invoke_cli(self, *arguments: str) -> dict[str, object]:
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(list(arguments)), 0)
        return json.loads(output.getvalue())

    def test_score_progress_json_includes_citations(self) -> None:
        result = self.invoke_cli("advancement", "score-progress", "ability", "17")
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["xp_into_score"], 2)
        self.assertTrue(result["citations"])

    def test_apply_xp_json_preserves_gain_limit_warning(self) -> None:
        result = self.invoke_cli(
            "advancement",
            "apply-xp",
            "ability",
            "0",
            "30",
            "--gain-limit",
            "2",
        )
        self.assertEqual(result["total_xp"], 15)
        self.assertTrue(result["warnings"])

    def test_source_quality_commands_return_auditable_results(self) -> None:
        result = self.invoke_cli(
            "advancement",
            "total",
            "8",
            "--virtue-bonus",
            "3",
            "--flaw-penalty",
            "1",
        )
        self.assertEqual(result["value"], 10)
        components = result["components"]
        assert isinstance(components, list)
        self.assertEqual(len(components), 4)
        self.assertTrue(result["citations"])


@unittest.skipUnless(FAST_MCP_AVAILABLE, "requires the optional fastmcp dependency")
class AdvancementMcpIntegrationTests(unittest.TestCase):
    def test_xp_tools_preserve_score_state(self) -> None:
        self.assertEqual(calculate_xp_to_buy_score("art", 4)["value"], 10)
        progress = calculate_score_progress("ability", 17)
        self.assertEqual(progress["score"], 2)
        self.assertTrue(progress["citations"])

    def test_apply_experience_exposes_source_cap(self) -> None:
        result = apply_advancement_experience("ability", 0, 30, gain_limit=2)
        self.assertEqual(result["total_xp"], 15)
        self.assertTrue(result["warnings"])

    def test_source_quality_tools_return_components_and_metadata(self) -> None:
        total = calculate_advancement_total(8, virtue_bonus=3, flaw_penalty=1)
        self.assertEqual(total["value"], 10)
        self.assertEqual(len(total["components"]), 4)
        self.assertEqual(calculate_exposure_source_quality(2)["value"], 1)
        self.assertEqual(calculate_practice_source_quality(4)["value"], 4)
        training = calculate_training_source_quality(5)
        self.assertEqual(training["metadata"]["gain_limit"], 5)
        self.assertEqual(calculate_teaching_source_quality(2, 4, 3)["value"], 12)
        adventure = calculate_adventure_source_quality(11)
        self.assertTrue(adventure["warnings"])


if __name__ == "__main__":
    unittest.main()
