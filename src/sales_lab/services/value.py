"""Deterministic, auditable Chapter 12 value analysis."""

# ruff: noqa: E501, EM101, TRY003 - readable authored fixtures and learner-facing errors.

from dataclasses import replace
from decimal import ROUND_HALF_UP, Decimal

from sales_lab.domain.approaches import SolutionApproachType, SolutionOptionSet
from sales_lab.domain.value import (
    Baseline,
    BenefitCategory,
    BenefitEstimate,
    CalculationReadiness,
    CostCategory,
    CostEstimate,
    CostTiming,
    EstimateUnit,
    EvidenceStatus,
    FinancialMetrics,
    FinancialPeriod,
    Scenario,
    SensitivityResult,
    ValueAnalysis,
    ValueAssumption,
    ValueFinding,
    ValueKind,
)
from sales_lab.examples.harbor_street_music import harbor_street_music_solution_options

MONEY = Decimal("0.01")
HOURS = Decimal("0.01")
MONTHS_PER_YEAR = Decimal(12)
WEEKS_PER_YEAR = Decimal(52)
MINUTES_PER_HOUR = Decimal(60)


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def _round_hours(value: Decimal) -> Decimal:
    return value.quantize(HOURS, rounding=ROUND_HALF_UP)


def calculate_scenario(scenario: Scenario) -> FinancialMetrics:
    """Calculate simple metrics from a fully supplied fictional scenario.

    Money and hours round to two decimals using ROUND_HALF_UP. Intermediate arithmetic is
    retained at Decimal precision. The hourly input is an opportunity-value assumption, so the
    result is estimated value rather than promised cash savings.
    """
    one_time = _round_money(scenario.implementation_hours * scenario.hourly_value)
    recurring = _round_money(
        scenario.recurring_admin_hours_per_month
        * Decimal(scenario.horizon_months)
        * scenario.hourly_value
    )
    horizon_years = Decimal(scenario.horizon_months) / MONTHS_PER_YEAR
    annual_hours = _round_hours(
        scenario.inquiries_per_week
        * scenario.minutes_saved_per_inquiry
        / MINUTES_PER_HOUR
        * WEEKS_PER_YEAR
    )
    estimated_value = _round_money(annual_hours * horizon_years * scenario.hourly_value)
    total_cost = one_time + recurring
    net = estimated_value - total_cost
    roi = (
        None
        if total_cost == 0
        else (net / total_cost).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    )
    monthly_gross_value = annual_hours * scenario.hourly_value / MONTHS_PER_YEAR
    monthly_net = monthly_gross_value - (
        scenario.recurring_admin_hours_per_month * scenario.hourly_value
    )
    payback = None
    if one_time > 0 and monthly_net > 0:
        payback = (one_time / monthly_net).quantize(MONEY, rounding=ROUND_HALF_UP)
    return FinancialMetrics(
        one_time, recurring, annual_hours, estimated_value, total_cost, net, roi, payback
    )


def calculate_simple_roi(benefit: Decimal | None, cost: Decimal | None) -> Decimal | None:
    """Return simple ROI only when both explicit values and a non-zero denominator exist."""
    if benefit is None or cost is None or cost == 0:
        return None
    return ((benefit - cost) / cost).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def calculate_payback(
    one_time_cost: Decimal | None, monthly_net_benefit: Decimal | None
) -> Decimal | None:
    """Return simple payback only for defined timing and positive recurring net benefit."""
    if one_time_cost is None or monthly_net_benefit is None or monthly_net_benefit <= 0:
        return None
    return (one_time_cost / monthly_net_benefit).quantize(MONEY, rounding=ROUND_HALF_UP)


def total_cost(costs: tuple[CostEstimate, ...], timing: CostTiming) -> Decimal | None:
    """Sum expected USD amounts of one timing, preserving missing as unknown."""
    selected = tuple(cost for cost in costs if cost.timing is timing)
    if not selected or any(
        cost.amount is None or cost.unit is not EstimateUnit.USD for cost in selected
    ):
        return None
    return _round_money(
        sum(
            (cost.amount.expected or cost.amount.minimum for cost in selected if cost.amount),
            start=Decimal(0),
        )
    )


def sensitivity_analysis(
    scenario: Scenario, minutes: tuple[Decimal, ...]
) -> tuple[SensitivityResult, ...]:
    """Vary only supplied minutes saved; never optimize, randomize, or attach probabilities."""
    results = []
    for value in minutes:
        if value < 0:
            raise ValueError("sensitivity values cannot be negative")
        metrics = calculate_scenario(replace(scenario, minutes_saved_per_inquiry=value))
        results.append(
            SensitivityResult(
                value, metrics.annual_hours, metrics.estimated_value, metrics.net_value
            )
        )
    return tuple(results)


def detect_omitted_costs(
    options: SolutionOptionSet, costs: tuple[CostEstimate, ...]
) -> tuple[ValueFinding, ...]:
    """Flag commonly omitted assessments without adding invented amounts."""
    findings = []
    assessed = {(cost.approach_id, cost.category) for cost in costs}
    checks = {
        SolutionApproachType.BUILD: (
            (CostCategory.MAINTENANCE, "Ongoing maintenance has not been evaluated."),
            (CostCategory.SUPPORT, "Ongoing support has not been evaluated."),
        ),
        SolutionApproachType.BUY: (
            (CostCategory.TRAINING, "Training has not been evaluated."),
            (CostCategory.DATA_MIGRATION, "Data migration has not been evaluated."),
        ),
        SolutionApproachType.INTEGRATE_EXISTING: (
            (CostCategory.INTEGRATION, "Integration effort has not been evaluated."),
            (CostCategory.SUPPORT, "Integration support has not been evaluated."),
        ),
    }
    for approach in options.approaches:
        for category, message in checks.get(approach.approach_type, ()):
            if (approach.identifier, category) not in assessed:
                findings.append(
                    ValueFinding(approach.identifier, "Potential omitted cost", message)
                )
    return tuple(findings)


def detect_unsupported_benefits(benefits: tuple[BenefitEstimate, ...]) -> tuple[ValueFinding, ...]:
    """Flag assertive, ungrounded benefit claims, especially unknown revenue impacts."""
    findings = []
    for benefit in benefits:
        unsupported = benefit.evidence_status is EvidenceStatus.NOT_ESTABLISHED and (
            benefit.category is BenefitCategory.REVENUE_OPPORTUNITY
            or " will " in f" {benefit.hypothesis.lower()} "
            or "%" in benefit.hypothesis
        )
        if unsupported:
            findings.append(
                ValueFinding(
                    benefit.identifier,
                    "Unsupported benefit claim",
                    "No established baseline, causal evidence, or measurement assumption supports this claim.",
                )
            )
    return tuple(findings)


def illustrative_scenarios() -> tuple[Scenario, ...]:
    """Return three immutable fictional variants; none is a forecast or assigned probability."""
    common = {
        "classification": EvidenceStatus.EXPERIMENTAL_SCENARIO,
        "approach_id": "APP-002",
        "horizon": FinancialPeriod.YEAR,
        "horizon_months": 12,
        "hourly_value": Decimal(30),
        "hourly_value_basis": "Opportunity-value assumption; not wage or cash savings",
        "inquiries_per_week": Decimal(30),
    }
    return (
        Scenario(
            "Conservative Illustrative Spreadsheet Configuration",
            implementation_hours=Decimal(20),
            recurring_admin_hours_per_month=Decimal(3),
            minutes_saved_per_inquiry=Decimal(2),
            **common,  # type: ignore[arg-type]
        ),
        Scenario(
            "Expected Illustrative Spreadsheet Configuration",
            implementation_hours=Decimal(12),
            recurring_admin_hours_per_month=Decimal(2),
            minutes_saved_per_inquiry=Decimal(4),
            **common,  # type: ignore[arg-type]
        ),
        Scenario(
            "Optimistic Illustrative Spreadsheet Configuration",
            implementation_hours=Decimal(8),
            recurring_admin_hours_per_month=Decimal(1),
            minutes_saved_per_inquiry=Decimal(6),
            **common,  # type: ignore[arg-type]
        ),
    )


def analyze_harbor_street_value() -> ValueAnalysis:
    """Build incomplete canonical analysis and separate executable experiments."""
    options = harbor_street_music_solution_options()
    assumptions = (
        ValueAssumption(
            "VA-001",
            "The illustrative hourly value represents opportunity value, not payroll savings.",
            EvidenceStatus.EXPERIMENTAL_SCENARIO,
            "Chapter 12 learning experiment",
        ),
    )
    costs = (
        CostEstimate(
            "COST-001",
            "APP-004",
            CostCategory.RECURRING_SUBSCRIPTION,
            "Commercial software price",
            None,
            EstimateUnit.USD,
            "USD",
            CostTiming.RECURRING,
            FinancialPeriod.MONTH,
            EvidenceStatus.NOT_ESTABLISHED,
            trace_ids=("E7", "REQ-003", "APP-004"),
        ),
        CostEstimate(
            "COST-002",
            "APP-005",
            CostCategory.ONE_TIME_IMPLEMENTATION,
            "Custom development effort",
            None,
            EstimateUnit.USD,
            "USD",
            CostTiming.ONE_TIME,
            None,
            EvidenceStatus.NOT_ESTABLISHED,
            trace_ids=("CAP-001", "APP-005", "AUT-001"),
        ),
    )
    benefits = (
        BenefitEstimate(
            "BEN-001",
            "APP-002",
            BenefitCategory.TIME_SAVINGS,
            "Consistent inquiry status may reduce time spent reconstructing follow-up history.",
            "Compare current and future staff time locating inquiry history.",
            "REQ-001 / CAP-001",
            "Current time has not been measured",
            None,
            EstimateUnit.HOURS_PER_WEEK,
            EvidenceStatus.NOT_ESTABLISHED,
            ValueKind.TANGIBLE,
            uncertainty="Frequency and minutes are not established",
            trace_ids=("E2", "REQ-001", "CAP-001", "APP-002"),
        ),
        BenefitEstimate(
            "BEN-002",
            "APP-001",
            BenefitCategory.IMPROVED_CONSISTENCY,
            "A documented process may make follow-up more consistent.",
            "Observe whether agreed statuses and follow-up steps are used.",
            "REQ-001 / process gap",
            "No documented follow-up process exists",
            None,
            EstimateUnit.COUNT,
            EvidenceStatus.NOT_ESTABLISHED,
            ValueKind.INTANGIBLE,
            uncertainty="Future adherence has not been tested",
            trace_ids=("E2", "REQ-001", "CAP-001", "APP-001"),
        ),
        BenefitEstimate(
            "BEN-003",
            "APP-004",
            BenefitCategory.REVENUE_OPPORTUNITY,
            "Commercial software will increase lesson revenue by 25%.",
            "Incremental lesson revenue compared with an established baseline.",
            "No supporting requirement or gap",
            "Revenue and conversion baseline not established",
            None,
            EstimateUnit.PERCENT,
            EvidenceStatus.NOT_ESTABLISHED,
            ValueKind.TANGIBLE,
            uncertainty="Baseline, causality, and conversion are unknown",
            trace_ids=("APP-004",),
        ),
    )
    scenarios = illustrative_scenarios()
    scenario_results = tuple((scenario, calculate_scenario(scenario)) for scenario in scenarios)
    findings = (*detect_omitted_costs(options, costs), *detect_unsupported_benefits(benefits))
    return ValueAnalysis(
        options.engagement,
        Baseline(
            "APP-007",
            "Shared spreadsheet with confirmed lessons copied manually to a separate calendar.",
            ("No new implementation or change-management cost is established.",),
            ("Manual effort cost", "Consequences of unresolved inquiries"),
            ("Continued manual effort", "Continued limited inquiry-status visibility"),
            ("Time spent per inquiry", "Follow-up outcomes", "Loaded labor cost", "Revenue impact"),
        ),
        tuple((approach.identifier, approach.name) for approach in options.approaches),
        costs,
        benefits,
        assumptions,
        CalculationReadiness.NOT_READY,
        "Baseline staff time, loaded labor cost, implementation effort, and recurring costs are not established.",
        scenario_results,
        sensitivity_analysis(scenarios[1], (Decimal(1), Decimal(3), Decimal(5), Decimal(7))),
        findings,
        (
            "How much staff time does the current process require?",
            "Which costs are cash expenditures versus internal capacity?",
            "What implementation, training, support, and maintenance effort would each approach require?",
        ),
    )
