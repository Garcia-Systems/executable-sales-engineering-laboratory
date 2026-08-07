"""Immutable customer-success and outcome-measurement concepts."""

# ruff: noqa: D101, D102, D105, EM101, TRY003 - compact educational value objects.

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class SuccessState(StrEnum):
    """Distinct lifecycle evidence states; no state implies the next."""

    DELIVERED = "DELIVERED"
    IMPLEMENTED = "IMPLEMENTED"
    AVAILABLE = "AVAILABLE"
    ADOPTED = "ADOPTED"
    USED_CORRECTLY = "USED_CORRECTLY"
    OPERATIONALLY_EFFECTIVE = "OPERATIONALLY_EFFECTIVE"
    OUTCOME_OBSERVED = "OUTCOME_OBSERVED"
    VALUE_VALIDATED = "VALUE_VALIDATED"


class MeasureType(StrEnum):
    DELIVERY = "DELIVERY"
    ADOPTION = "ADOPTION"
    PROCESS = "PROCESS"
    QUALITY = "QUALITY"
    OUTCOME = "OUTCOME"
    VALUE = "VALUE"
    RISK = "RISK"
    UNINTENDED_EFFECT = "UNINTENDED_EFFECT"


class IndicatorTiming(StrEnum):
    LEADING = "LEADING"
    LAGGING = "LAGGING"


class BaselineStatus(StrEnum):
    ESTABLISHED = "ESTABLISHED"
    PARTIALLY_ESTABLISHED = "PARTIALLY_ESTABLISHED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ObservationPeriodType(StrEnum):
    BASELINE_PERIOD = "BASELINE_PERIOD"
    INITIAL_VALIDATION_PERIOD = "INITIAL_VALIDATION_PERIOD"
    FIRST_REVIEW_PERIOD = "FIRST_REVIEW_PERIOD"
    FOLLOW_UP_REVIEW_PERIOD = "FOLLOW_UP_REVIEW_PERIOD"
    CUSTOM = "CUSTOM"


class MeasurementReadiness(StrEnum):
    READY = "READY"
    PARTIALLY_READY = "PARTIALLY_READY"
    NOT_READY = "NOT_READY"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ValidationStatus(StrEnum):
    NOT_READY = "NOT_READY"
    READY_TO_MEASURE = "READY_TO_MEASURE"
    MEASUREMENT_IN_PROGRESS = "MEASUREMENT_IN_PROGRESS"
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class MeasureStatus(StrEnum):
    PLANNED = "PLANNED"
    READY_TO_MEASURE = "READY_TO_MEASURE"
    MEASUREMENT_IN_PROGRESS = "MEASUREMENT_IN_PROGRESS"
    REVIEW = "REVIEW"


@dataclass(frozen=True, slots=True)
class Baseline:
    status: BaselineStatus
    description: str
    value: Decimal | None = None

    def __post_init__(self) -> None:
        if self.status is BaselineStatus.ESTABLISHED and self.value is None:
            raise ValueError("an established baseline requires a value")
        if self.status is BaselineStatus.NOT_ESTABLISHED and self.value is not None:
            raise ValueError("a missing baseline is unknown, not zero")


@dataclass(frozen=True, slots=True)
class TargetCondition:
    statement: str
    population: str
    exclusions: str
    sampling_method: str
    exception_treatment: str


@dataclass(frozen=True, slots=True)
class EvidenceSource:
    name: str
    limitation: str


@dataclass(frozen=True, slots=True)
class ObservationPeriod:
    period_type: ObservationPeriodType
    identifier: str


@dataclass(frozen=True, slots=True)
class MeasurementOwner:
    role: str

    @property
    def established(self) -> bool:
        return self.role != "OWNER_NOT_ESTABLISHED"


@dataclass(frozen=True, slots=True)
class SuccessMeasure:
    identifier: str
    name: str
    purpose: str
    measure_type: MeasureType
    definition: str
    unit: str
    baseline: Baseline
    target_condition: TargetCondition
    evidence_source: EvidenceSource
    observation_period: ObservationPeriod
    owner: MeasurementOwner
    status: MeasureStatus
    readiness: MeasurementReadiness
    indicator_timing: IndicatorTiming
    requirement_ids: tuple[str, ...]
    success_criterion_ids: tuple[str, ...]
    outcome_ids: tuple[str, ...]
    benefit_ids: tuple[str, ...]
    limitations: tuple[str, ...]
    activity_only: bool = False


@dataclass(frozen=True, slots=True)
class MeasurementFinding:
    measure_id: str
    kind: str
    statement: str


@dataclass(frozen=True, slots=True)
class BenefitValidation:
    benefit_id: str
    hypothesis: str
    required_baseline: str
    follow_up_measure_id: str
    evidence_status: str
    observed_result: str | None
    validation_status: ValidationStatus
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class UnintendedConsequence:
    identifier: str
    effect_to_monitor: str
    measure_id: str
    observed: bool = False


@dataclass(frozen=True, slots=True)
class CorrectiveAction:
    identifier: str
    finding: str
    action: str
    trigger: str
    decision_owner: MeasurementOwner
    executed: bool = False


@dataclass(frozen=True, slots=True)
class TraceabilityRow:
    evidence_id: str
    requirement_id: str
    success_criterion_id: str
    recommendation_id: str
    scope_id: str
    measure_id: str
    baseline_status: BaselineStatus
    observed_evidence: str
    outcome_finding: str
    value_validation: str
    corrective_action_id: str


@dataclass(frozen=True, slots=True)
class SuccessMeasurementPlan:
    engagement: str
    lifecycle_status: str
    purpose: str
    intended_outcomes: tuple[tuple[str, str], ...]
    measures: tuple[SuccessMeasure, ...]
    findings: tuple[MeasurementFinding, ...]
    benefit_validations: tuple[BenefitValidation, ...]
    unintended_consequences: tuple[UnintendedConsequence, ...]
    corrective_actions: tuple[CorrectiveAction, ...]
    traceability: tuple[TraceabilityRow, ...]
    next_review_actions: tuple[str, ...]
    open_questions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ObservedValue:
    measure_id: str
    period_id: str
    numerator: Decimal
    denominator: Decimal
    unit: str


@dataclass(frozen=True, slots=True)
class OutcomeFinding:
    measure_id: str
    statement: str
    state: SuccessState
    causality: ValidationStatus


@dataclass(frozen=True, slots=True)
class CustomerSuccessReview:
    classification: str
    scenario: str
    observations: tuple[ObservedValue, ...]
    outcome_findings: tuple[OutcomeFinding, ...]
    benefit_validation: tuple[BenefitValidation, ...]
    unintended_effects: tuple[UnintendedConsequence, ...]
    corrective_actions: tuple[CorrectiveAction, ...]
    limitations: tuple[str, ...]
    next_review_decision: str
