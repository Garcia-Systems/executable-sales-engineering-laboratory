"""Immutable Chapter 13 risk, assumption, dependency, and constraint concepts."""

# ruff: noqa: D101, D105, EM101, TRY003

from dataclasses import dataclass
from enum import StrEnum


class RiskCategory(StrEnum):
    """Educational organizing aids, not a universal taxonomy."""

    TECHNICAL = "Technical"
    OPERATIONAL = "Operational"
    DATA = "Data"
    SECURITY = "Security"
    PRIVACY = "Privacy"
    ORGANIZATIONAL = "Organizational"
    ADOPTION = "Adoption"
    COMMERCIAL = "Commercial"
    SCHEDULE = "Schedule"
    MAINTENANCE = "Maintenance"
    INTEGRATION = "Integration"
    PROCESS = "Process"
    VALUE_REALIZATION = "Value realization"


class RiskStatus(StrEnum):
    IDENTIFIED = "Identified"
    UNDER_REVIEW = "Under review"
    RESPONSE_PLANNED = "Response planned"
    ACCEPTED = "Accepted"
    MITIGATED = "Mitigated"
    CLOSED = "Closed"


class QualitativeLevel(StrEnum):
    """Independent likelihood or impact—not inputs to an aggregate score."""

    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    UNKNOWN = "Unknown"
    NOT_EVALUATED = "Not evaluated"


class AssumptionValidationStatus(StrEnum):
    UNVALIDATED = "Unvalidated"
    VALIDATION_PLANNED = "Validation planned"
    VALIDATED = "Validated"
    DISPROVED = "Disproved"
    NOT_VALIDATABLE_YET = "Not validatable yet"


class DependencyCategory(StrEnum):
    TECHNICAL = "Technical"
    ORGANIZATIONAL = "Organizational"
    COMMERCIAL = "Commercial"
    DATA = "Data"
    VENDOR = "Vendor"
    STAFFING = "Staffing"
    DECISION = "Decision"
    EXTERNAL = "External"


class DependencyStatus(StrEnum):
    UNRESOLVED = "Unresolved"
    RESOLUTION_PLANNED = "Resolution planned"
    SATISFIED = "Satisfied"
    UNAVAILABLE = "Unavailable"
    UNKNOWN = "Unknown"


class ConstraintScope(StrEnum):
    CUSTOMER = "Customer"
    LABORATORY = "Laboratory"


class ResponseType(StrEnum):
    AVOID = "Avoid"
    REDUCE = "Reduce"
    TRANSFER = "Transfer"
    ACCEPT = "Accept"
    INVESTIGATE = "Investigate"
    CONTINGENCY = "Contingency"
    NOT_PLANNED = "Not planned"


class Applicability(StrEnum):
    APPLICABLE = "Applicable"
    NOT_APPLICABLE = "Not Applicable"
    UNKNOWN = "Unknown"
    REQUIRES_VALIDATION = "Requires Validation"


@dataclass(frozen=True, slots=True)
class ValidationAction:
    action: str
    responsible_role: str | None = None


@dataclass(frozen=True, slots=True)
class RiskEvidence:
    evidence_id: str
    statement: str
    source: str


@dataclass(frozen=True, slots=True)
class RiskResponse:
    identifier: str
    risk_id: str
    response_type: ResponseType
    action: str
    responsible_role: str | None
    triggering_condition: str
    expected_effect: str
    remaining_uncertainty: str


@dataclass(frozen=True, slots=True)
class ResidualRisk:
    identifier: str
    risk_id: str
    statement: str
    likelihood: QualitativeLevel
    impact: QualitativeLevel


@dataclass(frozen=True, slots=True)
class Risk:
    """An explicit uncertain cause-event-consequence statement."""

    identifier: str
    title: str
    cause: str
    event: str
    consequence: str
    categories: tuple[RiskCategory, ...]
    status: RiskStatus
    likelihood: QualitativeLevel
    impact: QualitativeLevel
    evaluation_reason: str
    affected_approach_ids: tuple[str, ...]
    trace_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    owner_role: str | None = None

    def __post_init__(self) -> None:
        if not self.cause.strip() or not self.event.strip() or not self.consequence.strip():
            raise ValueError("risk requires non-empty cause, event, and consequence")
        if not self.categories:
            raise ValueError("risk requires at least one category")


@dataclass(frozen=True, slots=True)
class AssumptionRecord:
    identifier: str
    statement: str
    source: str
    affected_approach_ids: tuple[str, ...]
    validation_status: AssumptionValidationStatus
    validation_action: ValidationAction | None
    consequence_if_false: str
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DependencyRecord:
    identifier: str
    statement: str
    category: DependencyCategory
    depended_on_by: tuple[str, ...]
    status: DependencyStatus
    evidence_ids: tuple[str, ...]
    consequence_if_unmet: str
    resolution_action: ValidationAction | None
    owner_role: str | None = None


@dataclass(frozen=True, slots=True)
class ConstraintRecord:
    identifier: str
    statement: str
    scope: ConstraintScope
    source: str
    affected_approach_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class IssueRecord:
    identifier: str
    statement: str
    evidence_ids: tuple[str, ...]
    affected_objective: str


@dataclass(frozen=True, slots=True)
class ClassificationFinding:
    subject: str
    finding: str
    explanation: str


@dataclass(frozen=True, slots=True)
class ApproachRiskProfile:
    approach_id: str
    approach_name: str
    entries: tuple[tuple[str, Applicability], ...]


@dataclass(frozen=True, slots=True)
class RiskValueLink:
    value_id: str
    risk_id: str
    value_effect: str


@dataclass(frozen=True, slots=True)
class RiskRegister:
    """Complete authored register; tuple order is explicit and never a ranking."""

    engagement: str
    scope: str
    risks: tuple[Risk, ...]
    evidence: tuple[RiskEvidence, ...]
    assumptions: tuple[AssumptionRecord, ...]
    dependencies: tuple[DependencyRecord, ...]
    constraints: tuple[ConstraintRecord, ...]
    issues: tuple[IssueRecord, ...]
    responses: tuple[RiskResponse, ...]
    residual_risks: tuple[ResidualRisk, ...]
    profiles: tuple[ApproachRiskProfile, ...]
    value_links: tuple[RiskValueLink, ...]
    traceability: tuple[tuple[str, ...], ...]
    open_questions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RiskAnalysis:
    register: RiskRegister
    unvalidated_assumptions: tuple[AssumptionRecord, ...]
    unresolved_dependencies: tuple[DependencyRecord, ...]
    risks_without_responses: tuple[Risk, ...]
    orphan_responses: tuple[RiskResponse, ...]
    classification_findings: tuple[ClassificationFinding, ...]


@dataclass(frozen=True, slots=True)
class AssumptionExperiment:
    original: RiskAnalysis
    updated: RiskAnalysis
    evidence: RiskEvidence
    integration_feasibility: str
    relevant_contingency_id: str


@dataclass(frozen=True, slots=True)
class MitigationExperiment:
    original: RiskAnalysis
    updated: RiskAnalysis
    validation_action: ValidationAction
