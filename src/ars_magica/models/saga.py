"""Saga entities and mutable narrative state."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import Field

from .base import Authority, StateRecord, Visibility


class SagaEntityKind(StrEnum):
    PERSON = "person"
    FACTION = "faction"
    PLACE = "place"
    OBJECT = "object"
    CONCEPT = "concept"


class SagaEntity(StateRecord):
    name: str
    kind: SagaEntityKind
    authority: Authority = Authority.SAGA
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class Person(SagaEntity):
    kind: SagaEntityKind = SagaEntityKind.PERSON
    character_id: str | None = None
    roles: list[str] = Field(default_factory=list)
    faction_ids: list[str] = Field(default_factory=list)
    portrait_asset_id: str | None = None
    status: str | None = None


class Faction(SagaEntity):
    kind: SagaEntityKind = SagaEntityKind.FACTION
    member_ids: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)


class Place(SagaEntity):
    kind: SagaEntityKind = SagaEntityKind.PLACE
    parent_place_id: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    map_feature_id: str | None = None
    alternate_names: list[str] = Field(default_factory=list)


class Relationship(StateRecord):
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    strength: int = Field(default=0, ge=-5, le=5)
    reciprocity: str = "directed"
    public_summary: str | None = None
    storyguide_notes: str | None = None


class SagaEvent(StateRecord):
    name: str
    occurred_on: date | None = None
    participant_ids: list[str] = Field(default_factory=list)
    location_id: str | None = None
    summary: str | None = None
    consequences: list[str] = Field(default_factory=list)


class Scene(StateRecord):
    name: str
    saga_id: str | None = None
    location_id: str | None = None
    participant_ids: list[str] = Field(default_factory=list)
    event_ids: list[str] = Field(default_factory=list)
    objective: str | None = None
    player_brief: str | None = None
    storyguide_notes: str | None = None


class Rumor(StateRecord):
    text: str
    subject_entity_ids: list[str] = Field(default_factory=list)
    truth_status: str = "unknown"
    origin_entity_id: str | None = None
    reliability: int | None = Field(default=None, ge=0, le=5)


class Secret(StateRecord):
    name: str
    details: str
    holder_entity_ids: list[str] = Field(default_factory=list)
    related_entity_ids: list[str] = Field(default_factory=list)
    reveal_conditions: list[str] = Field(default_factory=list)
    visibility: Visibility = Visibility.STORYGUIDE


class SagaState(StateRecord):
    name: str
    premise: str | None = None
    entity_ids: list[str] = Field(default_factory=list)
    event_ids: list[str] = Field(default_factory=list)
    current_season_id: str | None = None
    notes: str | None = None
