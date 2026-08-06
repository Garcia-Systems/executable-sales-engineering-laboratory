"""Immutable, technology-neutral integration concepts for Chapter 10."""

from dataclasses import dataclass
from enum import StrEnum


class IntegrationPattern(StrEnum):
    """Candidate ways information can cross a boundary."""

    MANUAL_HANDOFF = "Manual handoff"
    FILE_BATCH = "File / batch exchange"
    REQUEST_RESPONSE_API = "Request / response API"
    WEBHOOK = "Webhook"
    EVENT_DRIVEN = "Event-driven"
    SHARED_DATA = "Shared-data access"
    HYBRID = "Hybrid"


class IntegrationDirection(StrEnum):
    """Explicit direction without implied synchronization."""

    ONE_WAY = "One way"
    BIDIRECTIONAL = "Bidirectional"
    UNKNOWN = "Unknown"


class IntegrationTiming(StrEnum):
    """Conceptual timing rather than an invented latency target."""

    MANUAL = "Manual"
    SCHEDULED = "Scheduled"
    ON_DEMAND = "On demand"
    NEAR_REAL_TIME = "Near real time"
    EVENT_DRIVEN = "Event driven"
    UNKNOWN = "Unknown"


class FeasibilityState(StrEnum):
    """Evidence-bounded technical feasibility."""

    ESTABLISHED = "Established"
    PLAUSIBLE = "Plausible"
    REQUIRES_VALIDATION = "Requires validation"
    NOT_FEASIBLE = "Not feasible"
    NOT_EVALUATED = "Not evaluated"


class AssumptionStatus(StrEnum):
    """Whether an integration proposition has been verified."""

    VERIFIED = "Verified"
    UNVERIFIED = "Unverified"


class DataOwnership(StrEnum):
    """Whether an authoritative owner has been established."""

    SYSTEM_OF_RECORD = "System of record"
    NOT_ESTABLISHED = "Not established"


class FailureMode(StrEnum):
    """Deterministic failure considerations used by candidate patterns."""

    SOURCE_UNAVAILABLE = "Source unavailable"
    DESTINATION_UNAVAILABLE = "Destination unavailable"
    INVALID_DATA = "Invalid data"
    TIMEOUT = "Timeout"
    DUPLICATE_DELIVERY = "Duplicate delivery"
    OUT_OF_ORDER_DELIVERY = "Out-of-order delivery"
    AUTHENTICATION_FAILURE = "Authentication failure"
    AUTHORIZATION_FAILURE = "Authorization failure"


@dataclass(frozen=True, slots=True)
class IntegrationDependency:
    """A known or unresolved prerequisite."""

    identifier: str
    description: str
    known: bool


@dataclass(frozen=True, slots=True)
class IntegrationAssumption:
    """A proposition kept distinct from an established architecture fact."""

    identifier: str
    statement: str
    status: AssumptionStatus


@dataclass(frozen=True, slots=True)
class IntegrationStrategy:
    """One candidate mechanism for one existing architecture information flow."""

    identifier: str
    architecture_id: str
    information_flow_id: str
    source_id: str
    destination_id: str
    information: str
    purpose: str
    pattern: IntegrationPattern
    direction: IntegrationDirection
    timing: IntegrationTiming
    dependencies: tuple[IntegrationDependency, ...]
    assumptions: tuple[IntegrationAssumption, ...]
    feasibility: FeasibilityState
    failure_modes: tuple[FailureMode, ...]
    traceability: tuple[str, ...]
    human_work: str
    interface_dependency: str
    data_ownership: DataOwnership = DataOwnership.NOT_ESTABLISHED


@dataclass(frozen=True, slots=True)
class IntegrationQuestion:
    """An authentication, authorization, recovery, or ownership question."""

    category: str
    question: str
