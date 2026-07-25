"""Shared audit dataclasses for deterministic Ars Magica mechanics."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from fractions import Fraction

Number = int | Fraction
CORE_RULES = "reviewed/Ars Magica - Definitive Edition (Core Rules).md"


@dataclass(frozen=True)
class Component:
    """One named contribution to a calculated total."""

    label: str
    value: Number
    citation: str | None = None


@dataclass(frozen=True)
class AuditResult:
    """A calculated value with the trail needed to inspect it."""

    value: Number
    components: tuple[Component, ...]
    warnings: tuple[str, ...]
    citations: tuple[str, ...]
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    """Validation messages with citations to the rules being checked."""

    valid: bool
    warnings: tuple[str, ...]
    citations: tuple[str, ...]


def cite(line_start: int, line_end: int) -> str:
    """Return a repository-local Core Rules citation."""

    return f"{CORE_RULES}:{line_start}-{line_end}"


def audit_sum(
    components: tuple[Component, ...],
    *,
    warnings: tuple[str, ...] = (),
    citations: tuple[str, ...] = (),
    metadata: Mapping[str, object] | None = None,
) -> AuditResult:
    """Sum components into an auditable total."""

    total: Number = 0
    for component in components:
        total += component.value
    component_citations = tuple(
        component.citation for component in components if component.citation is not None
    )
    return AuditResult(
        value=total,
        components=components,
        warnings=warnings,
        citations=tuple(dict.fromkeys(component_citations + citations)),
        metadata={} if metadata is None else metadata,
    )
