"""Publishing, map, visual, audio, and rights models."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, HttpUrl

from .base import StateRecord


class PrintPreset(StateRecord):
    name: str
    page_size: str
    trim_width_mm: float | None = Field(default=None, gt=0)
    trim_height_mm: float | None = Field(default=None, gt=0)
    bleed_mm: float = Field(default=0, ge=0)
    safe_margin_mm: float = Field(default=0, ge=0)
    color_space: str = "RGB"
    pdf_standard: str | None = None
    minimum_image_dpi: int = Field(default=300, ge=1)
    crop_marks: bool = False
    duplex: bool = False


class StyleProfile(StateRecord):
    name: str
    description: str | None = None
    token_overrides: dict[str, Any] = Field(default_factory=dict)
    palette: dict[str, str] = Field(default_factory=dict)
    typography: dict[str, str] = Field(default_factory=dict)
    negative_guidance: list[str] = Field(default_factory=list)


class ArtifactSpec(StateRecord):
    """A durable material request that can be rendered without translation glue.

    ``template``, ``theme``, ``preset``, and ``content`` are accepted as input
    aliases for the compact publishing JSON contract. The canonical stored
    fields remain explicit IDs and ``data`` so saga state is not coupled to a
    particular renderer.
    """

    template_id: str = Field(
        validation_alias=AliasChoices("template_id", "template"),
        serialization_alias="template",
    )
    title: str
    audience: str = "player"
    content_ids: list[str] = Field(default_factory=list)
    print_preset_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("print_preset_id", "preset"),
        serialization_alias="preset",
    )
    style_profile_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("style_profile_id", "theme"),
        serialization_alias="theme",
    )
    output_formats: list[str] = Field(default_factory=lambda: ["pdf"])
    data: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("data", "content"),
        serialization_alias="content",
    )
    assets: list[dict[str, Any]] = Field(default_factory=list)


class MapLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9._:-]*$")
    name: str
    source_id: str | None = None
    visible: bool = True
    min_scale: float | None = Field(default=None, gt=0)
    max_scale: float | None = Field(default=None, gt=0)
    extensions: dict[str, Any] = Field(default_factory=dict)


class MapSpec(StateRecord):
    title: str
    audience: str = "player"
    map_kind: str
    projection: str | None = None
    extent: list[float] = Field(default_factory=list)
    valid_date: str | None = None
    scale: float | None = Field(default=None, gt=0)
    layers: list[MapLayer] = Field(default_factory=list)
    style_profile_id: str | None = None
    print_preset_id: str | None = None


class AssetKind(StrEnum):
    IMAGE = "image"
    AUDIO = "audio"
    SVG = "svg"
    DOCUMENT = "document"


class LicenseRecord(StateRecord):
    name: str
    license_identifier: str | None = None
    holder: str | None = None
    source_url: HttpUrl | None = None
    commercial_use: bool | None = None
    redistribution: bool | None = None
    attribution_text: str | None = None
    terms: str | None = None


class ConsentRecord(StateRecord):
    subject_id: str
    scope: list[str] = Field(default_factory=list)
    granted_by: str
    granted_on: str | None = None
    expires_on: str | None = None
    revoked: bool = False
    evidence_uri: HttpUrl | None = None


class GenerationRun(StateRecord):
    provider: str
    model: str | None = None
    model_revision: str | None = None
    prompt: str | None = None
    prompt_hash: str | None = None
    seed: int | None = None
    input_asset_ids: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    output_hash: str | None = None


class MediaAsset(StateRecord):
    kind: AssetKind
    title: str
    uri: str
    entity_id: str | None = None
    mime_type: str | None = None
    sha256: str | None = Field(default=None, pattern=r"^[A-Fa-f0-9]{64}$")
    license_id: str | None = None
    consent_id: str | None = None
    generation_run_id: str | None = None
    alt_text: str | None = None


class VisualAsset(MediaAsset):
    kind: AssetKind = AssetKind.IMAGE
    width_px: int | None = Field(default=None, gt=0)
    height_px: int | None = Field(default=None, gt=0)
    style_profile_id: str | None = None
    reference_asset_ids: list[str] = Field(default_factory=list)


class AudioAsset(MediaAsset):
    kind: AssetKind = AssetKind.AUDIO
    duration_seconds: float | None = Field(default=None, gt=0)
    sample_rate_hz: int | None = Field(default=None, gt=0)
    transcript: str | None = None
    loop_start_seconds: float | None = Field(default=None, ge=0)
    loop_end_seconds: float | None = Field(default=None, ge=0)


class CharacterBible(StateRecord):
    character_id: str
    canonical_asset_ids: list[str] = Field(default_factory=list)
    visual_invariants: list[str] = Field(default_factory=list)
    costume_notes: str | None = None
    expression_asset_ids: list[str] = Field(default_factory=list)
    approved: bool = False


class LocaleBible(StateRecord):
    place_id: str
    establishing_asset_ids: list[str] = Field(default_factory=list)
    interior_asset_ids: list[str] = Field(default_factory=list)
    material_notes: list[str] = Field(default_factory=list)
    seasonal_notes: dict[str, str] = Field(default_factory=dict)
    map_spec_id: str | None = None
    approved: bool = False
