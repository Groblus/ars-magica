"""Versioned publishing helpers for Ars Magica materials.

The public API deliberately accepts plain mappings as well as Pydantic-like
objects exposing ``model_dump``. Optional renderers are imported lazily.
"""

from .errors import (
    OptionalDependencyError,
    PublishingError,
    SourceReferenceError,
    TemplateNotFoundError,
)
from .render import (
    build_attribution,
    build_manifest,
    package_material,
    render_html,
    render_pdf,
    render_preview,
)
from .templates import inspect_template_requirements, list_templates

__all__ = [
    "OptionalDependencyError",
    "PublishingError",
    "SourceReferenceError",
    "TemplateNotFoundError",
    "build_attribution",
    "build_manifest",
    "inspect_template_requirements",
    "list_templates",
    "package_material",
    "render_html",
    "render_pdf",
    "render_preview",
]
