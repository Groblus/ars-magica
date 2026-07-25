"""Template discovery and public requirement inspection."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from .errors import TemplateNotFoundError
from .paths import TEMPLATE_ROOT


def _descriptor(template_name: str) -> dict[str, Any]:
    path = TEMPLATE_ROOT / template_name / "template.json"
    if not path.is_file():
        raise TemplateNotFoundError(f"unknown publishing template: {template_name}")
    return json.loads(path.read_text(encoding="ascii"))


def list_templates() -> list[dict[str, Any]]:
    """List stable metadata for all checked-in material templates."""
    templates = []
    for directory in sorted(TEMPLATE_ROOT.iterdir(), key=lambda item: item.name):
        descriptor = directory / "template.json"
        if not descriptor.is_file():
            continue
        data = json.loads(descriptor.read_text(encoding="ascii"))
        templates.append(
            {
                "id": data["id"],
                "version": data["version"],
                "title": data["title"],
                "description": data["description"],
                "outputs": data["outputs"],
            }
        )
    return templates


def inspect_template_requirements(template_name: str) -> dict[str, Any]:
    """Return the versioned structured-input contract for a template."""
    return deepcopy(_descriptor(template_name))
