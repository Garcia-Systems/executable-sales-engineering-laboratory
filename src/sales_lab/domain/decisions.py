"""Immutable concepts for transparent Chapter 14 decision analysis."""

# ruff: noqa: D101

from dataclasses import dataclass, fields
from enum import StrEnum


class CriterionType(StrEnum):
    REQUIREMENT_COVERAGE = "Requirement coverage"
    CAPABILITY_COVERAGE = "Capability coverage"
    EVIDENCE_STRENGTH = "Evidence strength"
    IMPLEMENTATION_FEASIBILITY = "Implementation feasibility"
    DEPENDENCY_READINESS = "Dependency readiness"
    RISK_ACCEPTABILITY = "Risk acceptability"
    COST_READINESS = "Cost readiness"
    REVERSIBILITY = "Reversibility"
    MAINTENANCE_OWNERSHIP = "Maintenance ownership"
    STAKEHOLDER_READINESS = "Stakeholder readiness"
    TIME_TO_LEARN = "Time to learn"


class ConditionKind(StrEnum):
    MANDATORY = "Mandatory"
    PREFERENCE = "Preference"


class ConditionStatus(StrEnum):
    SATISFIED = "Satisfied"
    UNMET = "Unmet"
    REQUIRES_VALIDATION = "Requires Validation"


class EvidenceStrength(StrEnum):
    ESTABLISHED = "Established"
    PARTIALLY_ESTABLISHED = "Partially Established"
    ASSUMPTION_DEPENDENT = "Assumption Dependent"
    EXPERIMENTAL = "Experimental"
    UNKNOWN = "Unknown"


class FindingState(StrEnum):
    ESTABLISHED = "Established"
    PARTIAL = "Partial"
    UNKNOWN = "Unknown"
    REQUIRES_VALIDATION = "Requires Validation"
    CONSTRAINT_CONFLICT = "Constraint Conflict"
    NOT_EVALUATED = "Not Evaluated"
    DISQUALIFIED = "Disqualified"


class RecommendationType(StrEnum):
    PROCEED = "Proceed"
    PROCEED_CONDITIONALLY = "Proceed Conditionally"
    VALIDATE_BEFORE_DECISION = "Validate Before Decision"
    DEFER = "Defer"
    DO_NOT_PROCEED = "Do Not Proceed"


class ConfidenceLevel(StrEnum):
    HIGH = "High"
    MODERATE = "Moderate"
    LOW = "Low"
    NOT_ASSESSED = "Not Assessed"


@dataclass(frozen=True, slots=True)
class DecisionCriterion:
    identifier: str
    criterion_type: CriterionType
    description: str
    trace_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DecisionCondition:
    identifier: str
    description: str
    kind: ConditionKind
    status: ConditionStatus
    approach_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CriterionFinding:
    approach_id: str
    criterion_id: str
    state: FindingState
    evidence_strength: EvidenceStrength
    reason: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ApproachEvaluation:
    approach_id: str
    findings: tuple[CriterionFinding, ...]
    condition_ids: tuple[str, ...]
    disqualified: bool = False


@dataclass(frozen=True, slots=True)
class TradeoffStatement:
    approach_id: str
    accepts: str
    in_exchange_for: str


@dataclass(frozen=True, slots=True)
class StakeholderPerspective:
    role_id: str
    role_name: str
    perspective: str
    evidence_ids: tuple[str, ...] = ()
    claims_agreement: bool = False


@dataclass(frozen=True, slots=True)
class ProfessionalJudgment:
    rationale: str
    accepted_tradeoffs: tuple[str, ...]
    unresolved_concerns: tuple[str, ...]
    evidence_limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RecommendationConfidence:
    level: ConfidenceLevel
    basis: str


@dataclass(frozen=True, slots=True)
class RecommendationCondition:
    identifier: str
    description: str
    trace_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RecommendationAlternative:
    approach_id: str
    role: str
    description: str


@dataclass(frozen=True, slots=True)
class ChangeTrigger:
    identifier: str
    condition: str
    response: str


@dataclass(frozen=True, slots=True)
class Recommendation:
    recommendation_type: RecommendationType
    approach_ids: tuple[str, ...]
    statement: str
    need_addressed: str
    evidence_ids: tuple[str, ...]
    conditions: tuple[RecommendationCondition, ...]
    confidence: RecommendationConfidence
    alternatives: tuple[RecommendationAlternative, ...]
    change_triggers: tuple[ChangeTrigger, ...]
    approved: bool = False


@dataclass(frozen=True, slots=True)
class DecisionPackage:
    engagement: str
    context: str
    approaches: tuple[tuple[str, str], ...]
    criteria: tuple[DecisionCriterion, ...]
    mandatory_conditions: tuple[DecisionCondition, ...]
    evaluations: tuple[ApproachEvaluation, ...]
    tradeoffs: tuple[TradeoffStatement, ...]
    perspectives: tuple[StakeholderPerspective, ...]
    professional_judgment: ProfessionalJudgment
    recommendation: Recommendation
    risks_and_unknowns: tuple[str, ...]
    traceability: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class DecisionExperiment:
    name: str
    original: DecisionPackage
    updated: DecisionPackage
    new_evidence: tuple[str, ...]
    changed_findings: tuple[str, ...]
    unchanged_findings: tuple[str, ...]
    interpretation: str


def numeric_decision_fields() -> tuple[str, ...]:
    """Expose accidental numeric-score fields for deterministic validation."""
    forbidden = {"score", "weight", "total", "rank", "ranking"}
    classes = (DecisionCriterion, CriterionFinding, ApproachEvaluation, Recommendation)
    return tuple(
        field.name
        for model in classes
        for field in fields(model)
        if field.name.casefold() in forbidden
    )
