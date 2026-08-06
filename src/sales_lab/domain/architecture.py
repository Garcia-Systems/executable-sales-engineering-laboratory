"""Immutable, technology-neutral solution architecture concepts for Chapter 9."""

from dataclasses import dataclass
from enum import StrEnum


class BoundaryPosition(StrEnum):
    """Whether an element is governed by the candidate solution."""

    INSIDE = "Inside Solution Boundary"
    EXTERNAL = "External"


class ComponentType(StrEnum):
    """Small educational classification rather than a universal standard."""

    USER_INTERFACE = "User Interface"
    WORKFLOW = "Workflow"
    DATA = "Data"
    INTEGRATION = "Integration"
    EXTERNAL_SYSTEM = "External System"
    REPORTING = "Reporting"
    IDENTITY = "Identity"


class DependencyState(StrEnum):
    """Evidence state for an architectural dependency."""

    ESTABLISHED = "Established"
    UNKNOWN = "Unknown"


class ArchitectureDimension(StrEnum):
    """Qualitative comparison dimensions that must not be totaled."""

    CHANGE_SCOPE = "Change Scope"
    INTEGRATION_DEPENDENCY = "Integration Dependency"
    CUSTOM_DEVELOPMENT = "Custom Development"
    PROCESS_CHANGE = "Process Change"
    OPERATIONAL_DEPENDENCY = "Operational Dependency"
    MAINTENANCE_RESPONSIBILITY = "Maintenance Responsibility"
    UNKNOWN_TECHNICAL_FACTORS = "Unknown Technical Factors"


class ArchitectureState(StrEnum):
    """Non-numeric comparison states."""

    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    UNKNOWN = "Unknown"
    NOT_EVALUATED = "Not Evaluated"


@dataclass(frozen=True, slots=True)
class ArchitectureActor:
    """A person or role interacting across the solution boundary."""

    identifier: str
    name: str
    stakeholder_id: str


@dataclass(frozen=True, slots=True)
class ArchitectureComponent:
    """A logical responsibility or established external resource."""

    identifier: str
    name: str
    component_type: ComponentType
    boundary: BoundaryPosition
    capability_ids: tuple[str, ...] = ()
    requirement_ids: tuple[str, ...] = ()
    constraint_ids: tuple[str, ...] = ()
    necessity: str | None = None


@dataclass(frozen=True, slots=True)
class ArchitectureConnection:
    """A directed relationship between actors or components."""

    identifier: str
    source_id: str
    destination_id: str


@dataclass(frozen=True, slots=True)
class InformationFlow:
    """Information crossing a connection without prescribing a schema or protocol."""

    identifier: str
    connection_id: str
    information: str
    purpose: str
    dependency_id: str | None = None


@dataclass(frozen=True, slots=True)
class ArchitectureDependency:
    """A dependency whose feasibility may remain explicitly unknown."""

    identifier: str
    description: str
    state: DependencyState


@dataclass(frozen=True, slots=True)
class ArchitectureAssumption:
    """A candidate proposition, never silently promoted to fact."""

    identifier: str
    statement: str


@dataclass(frozen=True, slots=True)
class ArchitectureDecision:
    """A lightweight candidate Architecture Decision Record."""

    identifier: str
    decision: str
    reason: str
    alternatives: tuple[str, ...]
    status: str = "Candidate architecture decision"


@dataclass(frozen=True, slots=True)
class ArchitectureQuestion:
    """An unresolved technical question retained for later investigation."""

    identifier: str
    question: str


@dataclass(frozen=True, slots=True)
class ArchitectureComparison:
    """One rationale-backed qualitative observation."""

    dimension: ArchitectureDimension
    state: ArchitectureState
    rationale: str


@dataclass(frozen=True, slots=True)
class SolutionArchitecture:
    """An ordered logical candidate linked to a Chapter 8 approach."""

    identifier: str
    name: str
    engagement: str
    approach_ids: tuple[str, ...]
    goals: tuple[str, ...]
    actors: tuple[ArchitectureActor, ...]
    components: tuple[ArchitectureComponent, ...]
    connections: tuple[ArchitectureConnection, ...]
    information_flows: tuple[InformationFlow, ...]
    dependencies: tuple[ArchitectureDependency, ...]
    assumptions: tuple[ArchitectureAssumption, ...]
    decisions: tuple[ArchitectureDecision, ...]
    questions: tuple[ArchitectureQuestion, ...]
    comparison: tuple[ArchitectureComparison, ...]
