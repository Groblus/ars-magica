"""Covenant, laboratory, season, and advancement state."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .base import ReferenceDefinition, StateRecord


class SeasonName(StrEnum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class LaboratoryFeatureDefinition(ReferenceDefinition):
    category: str | None = None
    description: str | None = None


class CovenantOptionDefinition(ReferenceDefinition):
    kind: str
    magnitude: str | None = None
    category: str | None = None
    description: str | None = None


class LaboratoryState(StateRecord):
    name: str
    owner_id: str | None = None
    covenant_id: str | None = None
    size: int = 0
    refinement: int = 0
    general_quality: int = 0
    safety: int = 0
    health: int = 0
    aesthetics: int = 0
    warping: int = 0
    feature_ids: list[str] = Field(default_factory=list)
    specialization_modifiers: dict[str, int] = Field(default_factory=dict)
    notes: str | None = None


class CovenantResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9._:-]*$")
    name: str
    kind: str
    quantity: float | None = None
    unit: str | None = None
    description: str | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class CovenantState(StateRecord):
    name: str
    tribunal: str | None = None
    location_id: str | None = None
    aura: int | None = None
    members: list[str] = Field(default_factory=list)
    laboratories: list[LaboratoryState] = Field(default_factory=list)
    option_ids: list[str] = Field(default_factory=list)
    resources: list[CovenantResource] = Field(default_factory=list)
    treasury: float | None = None
    notes: str | None = None


class Season(StateRecord):
    name: SeasonName
    year: int
    starts_on: date | None = None
    saga_id: str | None = None
    summary: str | None = None


class AdvancementEvent(StateRecord):
    character_id: str
    season_id: str
    activity: str
    ability_id: str | None = None
    art_id: str | None = None
    experience_awarded: int = Field(default=0, ge=0)
    source_kind: str | None = None
    laboratory_id: str | None = None
    result: str | None = None
    notes: str | None = None
