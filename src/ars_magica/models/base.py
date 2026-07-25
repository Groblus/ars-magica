"""Shared, versioned building blocks for Ars Magica records."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


SCHEMA_VERSION = "1.0"
RecordId = str


class Visibility(StrEnum):
    """Audience allowed to see a record or derivative."""

    PUBLIC = "public"
    PLAYER = "player"
    STORYGUIDE = "storyguide"


class Authority(StrEnum):
    """How a fact entered the corpus or saga."""

    DEFINITIVE = "definitive"
    FIFTH_EDITION = "fifth_edition"
    HISTORICAL = "historical"
    RECONSTRUCTION = "reconstruction"
    SAGA = "saga"


class SourceReference(BaseModel):
    """A precise, portable citation into a book, file, or external source."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    id: RecordId = Field(pattern=r"^[a-z][a-z0-9._:-]*$")
    title: str
    locator: str | None = None
    citation: str | None = None
    url: HttpUrl | None = None
    authority: Authority = Authority.DEFINITIVE
    notes: str | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class ProvenanceRecord(BaseModel):
    """Records a transformation or generation without prescribing a vendor."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    id: RecordId = Field(pattern=r"^[a-z][a-z0-9._:-]*$")
    actor: str
    action: str
    occurred_at: datetime | None = None
    input_ids: list[RecordId] = Field(default_factory=list)
    tool: str | None = None
    tool_version: str | None = None
    notes: str | None = None
    extensions: dict[str, Any] = Field(default_factory=dict)


class Record(BaseModel):
    """Common metadata for all durable model records."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    id: RecordId = Field(pattern=r"^[a-z][a-z0-9._:-]*$")
    source_refs: list[SourceReference] = Field(default_factory=list)
    visibility: Visibility = Visibility.STORYGUIDE
    valid_from: date | None = None
    valid_to: date | None = None
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    extensions: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_date_range(self) -> "Record":
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to must not be earlier than valid_from")
        return self


class ReferenceDefinition(Record):
    """An immutable catalog definition; mutable play belongs in state models."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    authority: Authority = Authority.DEFINITIVE


class StateRecord(Record):
    """A mutable record owned by a campaign, player, or Storyguide."""

    model_config = ConfigDict(extra="forbid")

    revision: int = Field(default=1, ge=1)
