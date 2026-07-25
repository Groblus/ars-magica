"""Rules catalog definitions and character/magus state."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .base import ReferenceDefinition, StateRecord


class CharacteristicName(StrEnum):
    INTELLIGENCE = "intelligence"
    PERCEPTION = "perception"
    PRESENCE = "presence"
    COMMUNICATION = "communication"
    STRENGTH = "strength"
    STAMINA = "stamina"
    DEXTERITY = "dexterity"
    QUICKNESS = "quickness"


class ArtKind(StrEnum):
    TECHNIQUE = "technique"
    FORM = "form"


class AbilityDefinition(ReferenceDefinition):
    category: str | None = None
    specialties: list[str] = Field(default_factory=list)
    requires_specialty: bool = False


class ArtDefinition(ReferenceDefinition):
    kind: ArtKind


class SpellDefinition(ReferenceDefinition):
    technique_id: str
    form_id: str
    level: int = Field(ge=0)
    range: str | None = None
    duration: str | None = None
    target: str | None = None
    ritual: bool = False
    description: str | None = None


class Score(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0)
    experience: int = Field(default=0, ge=0)
    specialty: str | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class AbilityScore(Score):
    ability_id: str


class ArtScore(Score):
    art_id: str


class SpellKnowledge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    spell_id: str
    mastery_score: int = Field(default=0, ge=0)
    mastery_abilities: list[str] = Field(default_factory=list)
    casting_total_modifier: int = 0
    notes: str | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class Characteristics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intelligence: int = Field(default=0, ge=-5, le=5)
    perception: int = Field(default=0, ge=-5, le=5)
    presence: int = Field(default=0, ge=-5, le=5)
    communication: int = Field(default=0, ge=-5, le=5)
    strength: int = Field(default=0, ge=-5, le=5)
    stamina: int = Field(default=0, ge=-5, le=5)
    dexterity: int = Field(default=0, ge=-5, le=5)
    quickness: int = Field(default=0, ge=-5, le=5)
    extensions: dict[str, Any] = Field(default_factory=dict)


class WoundState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9._:-]*$")
    severity: str
    penalty: int = 0
    healed: bool = False
    source: str | None = None
    notes: str | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class FatigueState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_level: int = Field(default=0, ge=0)
    maximum_levels: int = Field(default=5, ge=0)
    unconscious: bool = False
    extensions: dict[str, Any] = Field(default_factory=dict)


class AgingState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    apparent_age: int | None = Field(default=None, ge=0)
    chronological_age: int | None = Field(default=None, ge=0)
    aging_points: int = Field(default=0, ge=0)
    decrepitude: int = Field(default=0, ge=0)
    longevity_ritual_level: int | None = Field(default=None, ge=0)
    last_aging_roll_year: int | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class WarpingState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    points: int = Field(default=0, ge=0)
    score: int = Field(default=0, ge=0)
    flaws: list[str] = Field(default_factory=list)
    twilight_scar: str | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class CharacterState(StateRecord):
    name: str
    character_type: str = "character"
    player_name: str | None = None
    characteristics: Characteristics = Field(default_factory=Characteristics)
    abilities: list[AbilityScore] = Field(default_factory=list)
    virtue_ids: list[str] = Field(default_factory=list)
    flaw_ids: list[str] = Field(default_factory=list)
    known_spells: list[SpellKnowledge] = Field(default_factory=list)
    wounds: list[WoundState] = Field(default_factory=list)
    fatigue: FatigueState = Field(default_factory=FatigueState)
    aging: AgingState = Field(default_factory=AgingState)
    warping: WarpingState = Field(default_factory=WarpingState)
    confidence_points: int = Field(default=0, ge=0)
    notes: str | None = None


class MagusState(CharacterState):
    character_type: str = "magus"
    house: str | None = None
    tradition: str = "Hermetic"
    arts: list[ArtScore] = Field(default_factory=list)
    parma_magica_score: int = Field(default=0, ge=0)
    sigil: str | None = None
    familiar_id: str | None = None
    talisman_id: str | None = None
    covenant_id: str | None = None
