"""Installed-wheel smoke test for bundled press resources."""

from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_wheel_contains_press_resources_in_an_isolated_environment(tmp_path):
    uv = shutil.which("uv")
    if uv is None:
        raise unittest.SkipTest("uv is required for the isolated wheel resource test")

    wheelhouse = tmp_path / "wheelhouse"
    subprocess.run(
        [uv, "build", "--wheel", "--out-dir", str(wheelhouse), str(ROOT)],
        check=True,
        capture_output=True,
        text=True,
    )
    wheel = next(wheelhouse.glob("ars_magica_reference_lab-*.whl"))
    environment = tmp_path / "venv"
    venv.EnvBuilder(with_pip=False).create(environment)
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    subprocess.run(
        [uv, "pip", "install", "--python", str(python), "--no-deps", str(wheel)],
        check=True,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        [
            str(python),
            "-c",
            "from ars_magica.publishing import list_templates; "
            "print(','.join(item['id'] for item in list_templates()))",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "magus-character-sheet" in result.stdout
