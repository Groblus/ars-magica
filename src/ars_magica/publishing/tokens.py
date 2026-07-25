"""Read DTCG-style token files and compile their scalar values to CSS."""

from __future__ import annotations

import json
import re
from typing import Any

from .paths import THEME_ROOT, TOKEN_ROOT

REFERENCE = re.compile(r"^\{([^}]+)\}$")


def read_json(path: Any) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        if "$value" in value:
            result[prefix] = value["$value"]
        else:
            for key, child in value.items():
                if not key.startswith("$"):
                    child_name = f"{prefix}.{key}" if prefix else key
                    result.update(_flatten(child, child_name))
    return result


def token_values(theme: str) -> dict[str, Any]:
    """Return primitive, semantic, component, then theme token values."""
    values: dict[str, Any] = {}
    for filename in ("primitives.json", "semantic.json", "components.json"):
        values.update(_flatten(read_json(TOKEN_ROOT / filename)))
    theme_path = THEME_ROOT / theme / "tokens.json"
    if not theme_path.is_file():
        available = ", ".join(sorted(path.name for path in THEME_ROOT.iterdir() if path.is_dir()))
        raise ValueError(f"unknown theme '{theme}'; available themes: {available}")
    values.update(_flatten(read_json(theme_path)))
    return values


def _resolve(value: Any, values: dict[str, Any], seen: set[str] | None = None) -> Any:
    if not isinstance(value, str):
        return value
    match = REFERENCE.match(value)
    if not match:
        return value
    token_name = match.group(1)
    seen = seen or set()
    if token_name in seen:
        raise ValueError(f"circular token reference: {token_name}")
    if token_name not in values:
        raise ValueError(f"unknown token reference: {token_name}")
    return _resolve(values[token_name], values, seen | {token_name})


def compile_css_variables(theme: str) -> str:
    """Compile scalar DTCG token values to predictable custom properties."""
    values = token_values(theme)
    lines = [":root {"]
    for name in sorted(values):
        resolved = _resolve(values[name], values)
        if isinstance(resolved, (str, int, float)):
            lines.append(f"  --am-{name.replace('.', '-')}: {resolved};")
    lines.append("}")
    return "\n".join(lines)
