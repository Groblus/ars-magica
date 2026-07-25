"""HTML, optional PDF, and deterministic package rendering."""

from __future__ import annotations

import json
from pathlib import Path
import zipfile
from typing import Any

from .errors import OptionalDependencyError
from .models import canonical_json, content_hash, material_data
from .paths import PRESET_ROOT, STYLE_ROOT, TEMPLATE_ROOT, THEME_ROOT
from .templates import inspect_template_requirements
from .tokens import compile_css_variables


def _read_text(path: Any) -> str:
    return path.read_text(encoding="ascii")


def _preset(name: str) -> dict[str, Any]:
    path = PRESET_ROOT / f"{name}.json"
    if not path.is_file():
        available = ", ".join(sorted(item.name.removesuffix(".json") for item in PRESET_ROOT.iterdir() if item.name.endswith(".json")))
        raise ValueError(f"unknown print preset '{name}'; available presets: {available}")
    return json.loads(_read_text(path))


def _jinja_environment():
    try:
        from jinja2 import Environment, FunctionLoader, StrictUndefined, select_autoescape
    except ImportError as error:
        raise OptionalDependencyError(
            "render_html requires the optional dependency 'jinja2'. "
            "Install Jinja2 in the consuming environment."
        ) from error
    def load_template(name: str) -> str | None:
        resource = TEMPLATE_ROOT.joinpath(name)
        return _read_text(resource) if resource.is_file() else None

    return Environment(
        loader=FunctionLoader(load_template),
        autoescape=select_autoescape(default_for_string=True, default=True),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )


def _styles(theme: str, preset: dict[str, Any], preview: bool) -> str:
    styles = [
        compile_css_variables(theme),
        _read_text(STYLE_ROOT / "base.css"),
        _read_text(STYLE_ROOT / "components.css"),
        _read_text(THEME_ROOT / theme / "theme.css"),
        preset.get("css", ""),
    ]
    if preview:
        styles.append(_read_text(STYLE_ROOT / "preview.css"))
    return "\n\n".join(styles)


def render_html(spec: Any) -> str:
    """Render a self-contained HTML material using Jinja templates."""
    data = material_data(spec)
    descriptor = inspect_template_requirements(data["template"])
    preset = _preset(data["preset"])
    environment = _jinja_environment()
    template = environment.get_template(f"{data['template']}/document.html")
    return template.render(
        material=data,
        content=data["content"],
        artwork=data["assets"],
        template=descriptor,
        preset=preset,
        styles=_styles(data["theme"], preset, preview=False),
        preview=False,
    )


def render_preview(spec: Any) -> str:
    """Return a browser preview HTML document; raster previews are not bundled."""
    data = material_data(spec)
    descriptor = inspect_template_requirements(data["template"])
    preset = _preset(data["preset"])
    environment = _jinja_environment()
    template = environment.get_template(f"{data['template']}/document.html")
    return template.render(
        material=data,
        content=data["content"],
        artwork=data["assets"],
        template=descriptor,
        preset=preset,
        styles=_styles(data["theme"], preset, preview=True),
        preview=True,
    )


def render_pdf(spec: Any) -> bytes:
    """Render a PDF using optional WeasyPrint; no fallback PDF is fabricated."""
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as error:
        raise OptionalDependencyError(
            "render_pdf requires WeasyPrint and its native rendering libraries. "
            "Install the 'publishing' extra. On macOS install Pango and GObject "
            "first (for example: 'brew install pango gobject-introspection libffi'), "
            "then follow WeasyPrint's macOS library-path instructions."
        ) from error
    return HTML(string=render_html(spec), base_url=str(Path.cwd())).write_pdf()


def build_attribution(spec: Any) -> dict[str, Any]:
    """Build deterministic credits from separately registered visual assets."""
    data = material_data(spec)
    entries = []
    for asset in sorted(data["assets"], key=lambda item: str(item.get("id", ""))):
        entry = {
            "id": asset.get("id", "unidentified-asset"),
            "kind": asset.get("kind", "artwork"),
            "creator": asset.get("creator", "Unknown creator"),
            "license": asset.get("license", "License not recorded"),
            "source": asset.get("source", "Source not recorded"),
            "modified": bool(asset.get("modified", False)),
        }
        entries.append(entry)
    lines = ["# Asset attribution", ""]
    if not entries:
        lines.append("No external visual assets were registered for this material.")
    else:
        for entry in entries:
            changed = "; modified" if entry["modified"] else ""
            lines.append(
                f"- {entry['id']} ({entry['kind']}): {entry['creator']}; "
                f"{entry['license']}; {entry['source']}{changed}."
            )
    return {"version": "1.0.0", "entries": entries, "markdown": "\n".join(lines) + "\n"}


def build_manifest(spec: Any) -> dict[str, Any]:
    """Return a timestamp-free manifest that is stable for identical inputs."""
    data = material_data(spec)
    descriptor = inspect_template_requirements(data["template"])
    preset = _preset(data["preset"])
    return {
        "manifest_version": "1.0.0",
        "material": {
            "title": data["title"],
            "template": {"id": descriptor["id"], "version": descriptor["version"]},
            "theme": data["theme"],
            "preset": {"id": preset["id"], "version": preset["version"]},
            "audience": data["audience"],
        },
        "input_hash": content_hash(data),
        "content_hash": content_hash(data["content"]),
        "asset_hash": content_hash(data["assets"]),
        "source_references": data["source_references"],
        "outputs": descriptor["outputs"],
    }


def _zip_write(archive: zipfile.ZipFile, name: str, contents: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, contents)


def package_material(
    spec: Any,
    destination: str | Path,
    include_pdf: bool = False,
) -> Path:
    """Write a deterministic ZIP containing material, inputs, and provenance."""
    data = material_data(spec)
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    attribution = build_attribution(data)
    manifest = build_manifest(data)
    with zipfile.ZipFile(destination_path, "w") as archive:
        _zip_write(archive, "material.html", render_html(data).encode("utf-8"))
        _zip_write(archive, "input.json", canonical_json(data).encode("utf-8"))
        _zip_write(archive, "manifest.json", canonical_json(manifest).encode("utf-8"))
        _zip_write(archive, "ATTRIBUTION.md", attribution["markdown"].encode("utf-8"))
        if include_pdf:
            _zip_write(archive, "material.pdf", render_pdf(data))
    return destination_path
