"""Immutable, evidence-bounded current-capability concepts for Chapter 7."""

from dataclasses import dataclass
from enum import StrEnum


class CapabilityState(StrEnum):
    """What evidence establishes about a required capability in the current environment."""

    AVAILABLE = "Available"
    PARTIALLY_AVAILABLE = "Partially Available"
    NOT_AVAILABLE = "Not Available"
    UNKNOWN = "Unknown"


class GapType(StrEnum):
    """Distinct reasons that current and required capability do not align."""

    CAPABILITY_GAP = "Capability Gap"
    PROCESS_GAP = "Process Gap"
    INFORMATION_GAP = "Information Gap"
    EVIDENCE_GAP = "Evidence Gap"


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    """A reference to established evidence, retaining its identifier and provenance."""

    identifier: str
    statement: str
    source: str


@dataclass(frozen=True, slots=True)
class CurrentResource:
    """A current tool, process, or organizational resource—not a capability claim."""

    identifier: str
    name: str
    description: str
    evidence_ids: tuple[str, ...]
    investigation_question: str | None = None


@dataclass(frozen=True, slots=True)
class CapabilityAssessment:
    """An explicit evidence-based comparison for one Chapter 6 capability."""

    capability_id: str
    current_resource_ids: tuple[str, ...]
    state: CapabilityState
    evidence_ids: tuple[str, ...]
    rationale: str
    missing_evidence: str | None = None
    gap_type: GapType | None = None
    follow_up_question: str | None = None


@dataclass(frozen=True, slots=True)
class CurrentCapabilityInventory:
    """Ordered current resources, evidence references, and authored assessments."""

    engagement: str
    resources: tuple[CurrentResource, ...]
    evidence: tuple[EvidenceReference, ...]
    assessments: tuple[CapabilityAssessment, ...]


@dataclass(frozen=True, slots=True)
class CapabilityGap:
    """A derived gap which remains separate from any future remedy decision."""

    capability_id: str
    gap_type: GapType
    description: str
