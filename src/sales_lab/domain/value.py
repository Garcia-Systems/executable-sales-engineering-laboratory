"""Immutable Chapter 12 cost, benefit, and value concepts."""

# ruff: noqa: D105, EM101, TRY003 - validation messages are part of the lesson.

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CostCategory(StrEnum):
    """Educational cost taxonomy; it is deliberately not universal."""

    ONE_TIME_IMPLEMENTATION = "One-time implementation"
    RECURRING_SUBSCRIPTION = "Recurring subscription"
    INTERNAL_LABOR = "Internal labor"
    TRAINING = "Training"
    DATA_MIGRATION = "Data migration"
    INTEGRATION = "Integration"
    CUSTOMIZATION = "Customization"
    MAINTENANCE = "Maintenance"
    SUPPORT = "Support"
    CHANGE_MANAGEMENT = "Change management"
    OPERATING = "Operating"
    OPPORTUNITY_COST = "Opportunity cost"
    RISK_CONTINGENCY = "Risk contingency"


class BenefitCategory(StrEnum):
    """Potential value categories; membership does not prove a benefit."""

    TIME_SAVINGS = "Time savings"
    REDUCED_REWORK = "Reduced rework"
    IMPROVED_VISIBILITY = "Improved visibility"
    IMPROVED_CONSISTENCY = "Improved consistency"
    REDUCED_DELAY = "Reduced delay"
    BETTER_CUSTOMER_EXPERIENCE = "Better customer experience"
    RISK_REDUCTION = "Risk reduction"
    CAPACITY_INCREASE = "Capacity increase"
    REVENUE_OPPORTUNITY = "Revenue opportunity"
    STRATEGIC_FLEXIBILITY = "Strategic flexibility"


class EstimateUnit(StrEnum):
    """Units accepted by the educational model."""

    USD = "USD"
    HOURS = "hours"
    HOURS_PER_WEEK = "hours/week"
    INQUIRIES_PER_WEEK = "inquiries/week"
    MINUTES_PER_INQUIRY = "minutes/inquiry"
    PERCENT = "percent"
    COUNT = "count"


class EvidenceStatus(StrEnum):
    """How strongly an input is grounded."""

    ESTABLISHED = "Established"
    CUSTOMER_ESTIMATE = "Customer estimate"
    ANALYST_ASSUMPTION = "Analyst assumption"
    EXPERIMENTAL_SCENARIO = "Experimental scenario"
    NOT_ESTABLISHED = "Not established"


class CostTiming(StrEnum):
    """Whether a cost occurs once or repeats."""

    ONE_TIME = "One-time"
    RECURRING = "Recurring"


class FinancialPeriod(StrEnum):
    """Explicit analysis or recurrence periods."""

    MONTH = "Month"
    YEAR = "Year"
    THREE_YEARS = "Three years"
    CUSTOM_PERIOD = "Custom period"


class CalculationReadiness(StrEnum):
    """Whether a calculation has its required supported inputs."""

    READY = "Ready"
    PARTIALLY_READY = "Partially ready"
    NOT_READY = "Not ready"
    NOT_APPLICABLE = "Not applicable"


class ValueKind(StrEnum):
    """Whether value can currently be measured in a defined unit."""

    TANGIBLE = "Tangible"
    INTANGIBLE = "Intangible"


@dataclass(frozen=True, slots=True)
class EstimateRange:
    """A Decimal range that never silently rearranges invalid bounds."""

    minimum: Decimal
    maximum: Decimal
    expected: Decimal | None = None

    def __post_init__(self) -> None:
        if not all(isinstance(value, Decimal) for value in (self.minimum, self.maximum)):
            raise TypeError("range bounds must use Decimal")
        if self.minimum < 0:
            raise ValueError("range minimum cannot be negative")
        if self.minimum > self.maximum:
            raise ValueError("range minimum must be less than or equal to maximum")
        if self.expected is not None:
            if not isinstance(self.expected, Decimal):
                raise TypeError("range expected value must use Decimal")
            if not self.minimum <= self.expected <= self.maximum:
                raise ValueError("range expected value must be between minimum and maximum")


@dataclass(frozen=True, slots=True)
class ValueAssumption:
    """An inspectable premise with source and evidence classification."""

    identifier: str
    statement: str
    evidence_status: EvidenceStatus
    source: str


@dataclass(frozen=True, slots=True)
class CostEstimate:
    """A cost whose amount may legitimately remain unknown."""

    identifier: str
    approach_id: str
    category: CostCategory
    description: str
    amount: EstimateRange | None
    unit: EstimateUnit
    currency: str | None
    timing: CostTiming
    period: FinancialPeriod | None
    evidence_status: EvidenceStatus
    assumption_ids: tuple[str, ...] = ()
    trace_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.unit is EstimateUnit.USD:
            if self.currency != "USD":
                raise ValueError("USD monetary estimates require currency='USD'")
        elif self.currency is not None:
            raise ValueError("currency is only valid for monetary estimates")
        if self.timing is CostTiming.RECURRING and self.period is None:
            raise ValueError("recurring costs require an explicit period")
        if self.timing is CostTiming.ONE_TIME and self.period is not None:
            raise ValueError("one-time costs must not specify a recurring period")
        if self.amount is None and self.evidence_status is not EvidenceStatus.NOT_ESTABLISHED:
            raise ValueError("a missing cost amount must be Not established")


@dataclass(frozen=True, slots=True)
class BenefitEstimate:
    """A measured benefit or an explicitly unresolved hypothesis."""

    identifier: str
    approach_id: str
    category: BenefitCategory
    hypothesis: str
    measurement_definition: str
    supporting_requirement_or_gap: str
    baseline_status: str
    amount: EstimateRange | None
    unit: EstimateUnit
    evidence_status: EvidenceStatus
    value_kind: ValueKind
    assumption_ids: tuple[str, ...] = ()
    uncertainty: str = ""
    trace_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.amount is None and self.evidence_status is not EvidenceStatus.NOT_ESTABLISHED:
            raise ValueError("a missing benefit amount must be Not established")
        if self.value_kind is ValueKind.INTANGIBLE and self.amount is not None:
            raise ValueError("intangible value must not be assigned an arbitrary amount")


@dataclass(frozen=True, slots=True)
class Baseline:
    """The explicit comparison state, including unknown rather than zero costs."""

    approach_id: str
    current_process: str
    known_costs: tuple[str, ...]
    unknown_costs: tuple[str, ...]
    consequences: tuple[str, ...]
    unresolved_measurements: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Scenario:
    """An immutable, explicitly classified set of numerical experiment inputs."""

    name: str
    classification: EvidenceStatus
    approach_id: str
    horizon: FinancialPeriod
    horizon_months: int
    implementation_hours: Decimal
    hourly_value: Decimal
    hourly_value_basis: str
    recurring_admin_hours_per_month: Decimal
    inquiries_per_week: Decimal
    minutes_saved_per_inquiry: Decimal

    def __post_init__(self) -> None:
        values = (
            self.implementation_hours,
            self.hourly_value,
            self.recurring_admin_hours_per_month,
            self.inquiries_per_week,
            self.minutes_saved_per_inquiry,
        )
        if not all(isinstance(value, Decimal) for value in values):
            raise TypeError("scenario numerical inputs must use Decimal")
        if self.classification is not EvidenceStatus.EXPERIMENTAL_SCENARIO:
            raise ValueError("numerical learning scenarios must be Experimental scenario")
        if self.horizon_months <= 0 or any(value < 0 for value in values):
            raise ValueError("scenario horizon must be positive and inputs cannot be negative")
        if not self.hourly_value_basis:
            raise ValueError(
                "hourly value must identify wage, loaded cost, billing rate, or opportunity value"
            )


@dataclass(frozen=True, slots=True)
class FinancialMetrics:
    """Simple outputs; None means not calculable, never zero."""

    one_time_cost: Decimal
    recurring_cost: Decimal
    annual_hours: Decimal
    estimated_value: Decimal
    total_cost: Decimal
    net_value: Decimal
    simple_roi: Decimal | None
    payback_months: Decimal | None


@dataclass(frozen=True, slots=True)
class SensitivityResult:
    """One deterministic change to a supplied assumption."""

    minutes_saved: Decimal
    annual_hours: Decimal
    estimated_value: Decimal
    net_value: Decimal


@dataclass(frozen=True, slots=True)
class ValueFinding:
    """An omitted-cost or unsupported-benefit guardrail finding."""

    subject_id: str
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class ValueAnalysis:
    """The complete neutral analysis; it intentionally has no recommendation field."""

    engagement: str
    baseline: Baseline
    approach_names: tuple[tuple[str, str], ...]
    costs: tuple[CostEstimate, ...]
    benefits: tuple[BenefitEstimate, ...]
    assumptions: tuple[ValueAssumption, ...]
    readiness: CalculationReadiness
    readiness_reason: str
    scenarios: tuple[tuple[Scenario, FinancialMetrics], ...]
    sensitivity_results: tuple[SensitivityResult, ...]
    findings: tuple[ValueFinding, ...]
    open_questions: tuple[str, ...]
