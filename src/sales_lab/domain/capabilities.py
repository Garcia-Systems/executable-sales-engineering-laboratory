"""Immutable, vendor-neutral capability mapping concepts for Chapter 6."""

from dataclasses import dataclass
from enum import StrEnum


class CapabilityCategory(StrEnum):
    """Educational organization categories, not a universal industry taxonomy."""

    PROCESS = "Process"
    INFORMATION = "Information"
    COLLABORATION = "Collaboration"
    INTEGRATION = "Integration"
    CONTROL = "Control"
    REPORTING = "Reporting"


class CoverageStatus(StrEnum):
    """Qualitative mapping states; deliberately not numeric fit scores."""

    COVERED = "Covered"
    PARTIALLY_COVERED = "Partially Covered"
    NOT_COVERED = "Not Covered"
    NOT_EVALUATED = "Not Evaluated"


@dataclass(frozen=True, slots=True)
class Capability:
    """What the organization must be able to accomplish, without implementation."""

    identifier: str
    name: str
    description: str
    category: CapabilityCategory


@dataclass(frozen=True, slots=True)
class CapabilityRequirementLink:
    """An explicit many-to-many link with a qualitative coverage judgment."""

    capability_id: str
    requirement_id: str
    coverage: CoverageStatus = CoverageStatus.COVERED


@dataclass(frozen=True, slots=True)
class CapabilityMap:
    """Ordered author-supplied capabilities and mappings for one engagement."""

    engagement: str
    capabilities: tuple[Capability, ...]
    links: tuple[CapabilityRequirementLink, ...]
    open_questions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CapabilityGap:
    """A requirement gap or unsupported-capability guardrail finding."""

    subject_id: str
    kind: str
    message: str
