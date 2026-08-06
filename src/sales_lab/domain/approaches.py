"""Immutable, product-neutral solution-approach concepts for Chapter 8."""

from dataclasses import dataclass
from enum import StrEnum


class SolutionApproachType(StrEnum):
    """Educational categories, not a universal industry taxonomy."""

    PROCESS_CHANGE = "Process Change"
    CONFIGURE_EXISTING = "Configure Existing"
    INTEGRATE_EXISTING = "Integrate Existing"
    BUY = "Buy"
    BUILD = "Build"
    HYBRID = "Hybrid"
    STATUS_QUO = "Status Quo"


class FeasibilityState(StrEnum):
    """Evidence-bounded feasibility state; unknown is never impossibility."""

    PLAUSIBLE = "Plausible"
    REQUIRES_VALIDATION = "Requires Validation"
    NOT_FEASIBLE = "Not Feasible"
    NOT_EVALUATED = "Not Evaluated"


class TradeoffDimension(StrEnum):
    """Qualitative dimensions which must never be totaled into a score."""

    CHANGE_TO_PROCESS = "Change to Process"
    IMPLEMENTATION_EFFORT = "Implementation Effort"
    CUSTOMIZATION = "Customization"
    DEPENDENCY = "Dependency"
    MAINTENANCE = "Maintenance"
    TECHNICAL_COMPLEXITY = "Technical Complexity"
    TIME_TO_IMPLEMENT = "Time to Implement"
    FUTURE_FLEXIBILITY = "Future Flexibility"


class QualitativeState(StrEnum):
    """Non-numeric characterization supported by an authored rationale."""

    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    UNKNOWN = "Unknown"
    NOT_EVALUATED = "Not Evaluated"


@dataclass(frozen=True, slots=True)
class ApproachAssumption:
    """A proposition that must remain visible until evidence validates it."""

    statement: str
    evidence: str
    status: FeasibilityState


@dataclass(frozen=True, slots=True)
class ApproachTradeoff:
    """One qualitative observation and its explicit educational basis."""

    dimension: TradeoffDimension
    state: QualitativeState
    rationale: str


@dataclass(frozen=True, slots=True)
class SolutionApproach:
    """One candidate path linked by identifier to established capability gaps."""

    identifier: str
    name: str
    approach_type: SolutionApproachType
    description: str
    gap_capability_ids: tuple[str, ...]
    assumptions: tuple[ApproachAssumption, ...]
    constraint_requirement_ids: tuple[str, ...]
    evidence_needs: tuple[str, ...]
    feasibility: FeasibilityState
    tradeoffs: tuple[ApproachTradeoff, ...]
    uses_existing_tools: str
    needs_new_software: str
    needs_custom_development: str


@dataclass(frozen=True, slots=True)
class SolutionOptionSet:
    """Ordered authored candidates for an established gap analysis."""

    engagement: str
    approaches: tuple[SolutionApproach, ...]
    open_questions: tuple[str, ...]
