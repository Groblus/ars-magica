"""Dependency-free normalization and deterministic serialization helpers."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from .errors import SourceReferenceError

_AUDIENCE_ORDER = {"public": 0, "player": 1, "storyguide": 2}
_PRECISE_CITATION = re.compile(r"^.+:\d+(?:-\d+)?$")
_SENSITIVE_KEY = re.compile(
    r"(?:^|[_\- .])(secret|secrets|storyguide|gm|gamemaster|private)(?:$|[_\- .])"
)


def as_mapping(value: Any, name: str = "value") -> dict[str, Any]:
    """Normalize dicts, dataclasses, and Pydantic-compatible objects."""
    if isinstance(value, Mapping):
        return {str(key): normalize(item) for key, item in value.items()}
    if hasattr(value, "model_dump"):
        return as_mapping(value.model_dump(mode="json"), name)
    if hasattr(value, "dict"):
        return as_mapping(value.dict(), name)
    if is_dataclass(value):
        return as_mapping(asdict(value), name)
    raise TypeError(f"{name} must be a mapping, dataclass, or Pydantic-compatible model")


def normalize(value: Any) -> Any:
    """Convert supported structured inputs to JSON-compatible primitives."""
    if isinstance(value, Mapping):
        return {str(key): normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(item) for item in value]
    if is_dataclass(value):
        return normalize(asdict(value))
    if hasattr(value, "model_dump"):
        return normalize(value.model_dump(mode="json"))
    if hasattr(value, "dict"):
        return normalize(value.dict())
    if isinstance(value, Path):
        return str(value)
    return value


def canonical_json(value: Any) -> str:
    """Produce stable JSON for hashes, manifests, and package files."""
    return json.dumps(normalize(value), ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def content_hash(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _resource_name(value: Any, prefix: str) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    name = value.removeprefix(prefix + ".")
    return name.replace("_", "-")


def _audience_name(value: Any) -> str:
    audience = str(value or "player").lower()
    if audience not in _AUDIENCE_ORDER:
        raise ValueError("material spec audience must be public, player, or storyguide")
    return audience


def _is_sensitive_key(key: str) -> bool:
    return bool(_SENSITIVE_KEY.search(key.lower()))


_OMIT = object()


def _filter_for_audience(value: Any, audience: str) -> Any:
    """Recursively omit values not safe for the requested material audience."""
    if isinstance(value, Mapping):
        visibility = value.get("visibility")
        if (
            visibility is not None
            and _AUDIENCE_ORDER[_audience_name(visibility)] > _AUDIENCE_ORDER[audience]
        ):
            return _OMIT
        result: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            if audience != "storyguide" and _is_sensitive_key(key):
                continue
            filtered = _filter_for_audience(raw_value, audience)
            if filtered is not _OMIT:
                result[key] = filtered
        return result
    if isinstance(value, (list, tuple)):
        return [
            item
            for item in (_filter_for_audience(item, audience) for item in value)
            if item is not _OMIT
        ]
    return value


def _citation_id(citation: str) -> str:
    return "source." + sha256(citation.encode("utf-8")).hexdigest()[:16]


def _source_reference(value: Any, index: int) -> dict[str, Any]:
    """Return the one template-safe source-reference shape used by press."""
    label = f"source_references[{index}]"
    if isinstance(value, str):
        citation = value.strip()
        if not _PRECISE_CITATION.fullmatch(citation):
            raise SourceReferenceError(
                f"{label} must be a precise citation such as 'reviewed/Core.md:500-510'"
            )
        path, locator = citation.rsplit(":", 1)
        return {
            "id": _citation_id(citation),
            "title": Path(path).stem or path,
            "locator": locator,
            "citation": citation,
            "url": None,
            "authority": "definitive",
            "notes": None,
        }
    if not isinstance(value, Mapping):
        raise SourceReferenceError(
            f"{label} must be a citation string or SourceReference-like mapping"
        )
    item = normalize(value)
    title = item.get("title") or item.get("book")
    citation = item.get("citation")
    locator = item.get("locator")
    if citation is not None:
        if not isinstance(citation, str) or not _PRECISE_CITATION.fullmatch(citation.strip()):
            raise SourceReferenceError(
                f"{label}.citation must be a precise citation such as 'reviewed/Core.md:500-510'"
            )
        citation = citation.strip()
        locator = locator or citation.rsplit(":", 1)[1]
        title = title or Path(citation.rsplit(":", 1)[0]).stem
    if not isinstance(title, str) or not title.strip():
        raise SourceReferenceError(
            f"{label} needs title/book, or a precise citation from which to derive one"
        )
    if locator is not None and not isinstance(locator, str):
        raise SourceReferenceError(f"{label}.locator must be a string")
    if not citation and not locator:
        raise SourceReferenceError(f"{label} needs citation or locator")
    identity = str(item.get("id") or _citation_id(citation or f"{title}:{locator}"))
    return {
        "id": identity,
        "title": title.strip(),
        "locator": locator,
        "citation": citation,
        "url": str(item["url"]) if item.get("url") else None,
        "authority": str(item.get("authority") or "definitive"),
        "notes": item.get("notes"),
    }


def normalize_source_references(values: Any) -> list[dict[str, Any]]:
    """Validate citations before rendering and expose a documented stable shape."""
    if values is None:
        return []
    if not isinstance(values, list):
        raise SourceReferenceError("source_references must be a list")
    return [_source_reference(value, index) for index, value in enumerate(values)]


def material_data(spec: Any) -> dict[str, Any]:
    """Produce the canonical, audience-safe publishing contract.

    This accepts compact mappings and Phase 1 ``ArtifactSpec`` instances. All
    content, assets, and source references are filtered before a template,
    manifest, attribution file, or ZIP receives them.
    """
    raw = as_mapping(spec, "material spec")
    data = dict(raw)
    data["template"] = _resource_name(raw.get("template") or raw.get("template_id"), "template")
    data["theme"] = _resource_name(raw.get("theme") or raw.get("style_profile_id"), "style")
    data["preset"] = _resource_name(raw.get("preset") or raw.get("print_preset_id"), "preset")
    data["content"] = raw.get("content", raw.get("data", {}))
    required = ("template", "theme", "preset", "content")
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise ValueError("material spec is missing: " + ", ".join(missing))
    if not isinstance(data["content"], dict):
        raise TypeError("material spec content must be a mapping")
    assets = raw.get("assets", [])
    if not isinstance(assets, list):
        raise TypeError("material spec assets must be a list")
    audience = _audience_name(raw.get("audience", "player"))
    content = _filter_for_audience(data["content"], audience)
    safe_assets = _filter_for_audience(assets, audience)
    source_values = raw.get("source_references", raw.get("source_refs", []))
    safe_sources = _filter_for_audience(source_values, audience)
    template = data["template"]
    if not isinstance(template, str):
        raise TypeError("material spec template must be a string")
    data["title"] = raw.get("title") or template.replace("-", " ").title()
    data["audience"] = audience
    data["content"] = content if content is not _OMIT else {}
    data["assets"] = safe_assets if safe_assets is not _OMIT else []
    data["source_references"] = normalize_source_references(safe_sources)
    return data
