"""Chapter 12 transparent value-analysis tests."""

# ruff: noqa: PLR2004

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.value import render_value_mermaid
from sales_lab.domain.value import (
    BenefitCategory,
    BenefitEstimate,
    CalculationReadiness,
    CostCategory,
    CostEstimate,
    CostTiming,
    EstimateRange,
    EstimateUnit,
    EvidenceStatus,
    FinancialPeriod,
    ValueKind,
)
from sales_lab.examples.harbor_street_music import harbor_street_music_solution_options
from sales_lab.reports.value import render_value_report
from sales_lab.services.value import (
    analyze_harbor_street_value,
    calculate_payback,
    calculate_scenario,
    calculate_simple_roi,
    detect_omitted_costs,
    detect_unsupported_benefits,
    illustrative_scenarios,
    sensitivity_analysis,
    total_cost,
)

DEFAULT_RANGE = EstimateRange(Decimal(1), Decimal(3), Decimal(2))


def money_cost(
    *,
    amount: EstimateRange | None = DEFAULT_RANGE,
    timing: CostTiming = CostTiming.ONE_TIME,
    status: EvidenceStatus = EvidenceStatus.CUSTOMER_ESTIMATE,
) -> CostEstimate:
    """Build a small valid test cost."""
    return CostEstimate(
        "C",
        "APP-001",
        CostCategory.INTERNAL_LABOR,
        "cost",
        amount,
        EstimateUnit.USD,
        "USD",
        timing,
        FinancialPeriod.MONTH if timing is CostTiming.RECURRING else None,
        status,
    )


def hypothesis(**changes: object) -> BenefitEstimate:
    """Build a hypothesis and apply typed test changes."""
    item = BenefitEstimate(
        "B",
        "APP-001",
        BenefitCategory.TIME_SAVINGS,
        "Work may take less time.",
        "Compare before and after.",
        "REQ-001",
        "Not measured",
        None,
        EstimateUnit.HOURS_PER_WEEK,
        EvidenceStatus.NOT_ESTABLISHED,
        ValueKind.TANGIBLE,
    )
    return replace(item, **changes)  # type: ignore[arg-type]


def test_range_decimal_validation_and_immutability() -> None:
    """Ranges use Decimal, validate order and expectation, and remain frozen."""
    value = EstimateRange(Decimal(1), Decimal(3), Decimal(2))
    with pytest.raises(FrozenInstanceError):
        value.minimum = Decimal(0)  # type: ignore[misc]
    with pytest.raises(TypeError, match="Decimal"):
        EstimateRange(1, Decimal(2))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="expected"):
        EstimateRange(Decimal(1), Decimal(2), 1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="negative"):
        EstimateRange(Decimal(-1), Decimal(2))
    with pytest.raises(ValueError, match="less than"):
        EstimateRange(Decimal(2), Decimal(1))
    with pytest.raises(ValueError, match="between"):
        EstimateRange(Decimal(1), Decimal(2), Decimal(3))


def test_money_currency_timing_and_missing_validation() -> None:
    """Currency, units, timing, periods, and unknown values cannot be ambiguous."""
    assert money_cost().currency == "USD"
    assert money_cost(timing=CostTiming.RECURRING).period is FinancialPeriod.MONTH
    with pytest.raises(ValueError, match="currency='USD'"):
        replace(money_cost(), currency="EUR")
    with pytest.raises(ValueError, match="only valid"):
        replace(money_cost(), unit=EstimateUnit.HOURS, currency="USD")
    with pytest.raises(ValueError, match="explicit period"):
        replace(money_cost(timing=CostTiming.RECURRING), period=None)
    with pytest.raises(ValueError, match="must not specify"):
        replace(money_cost(), period=FinancialPeriod.MONTH)
    with pytest.raises(ValueError, match="missing cost"):
        replace(money_cost(), amount=None)
    assert money_cost(amount=None, status=EvidenceStatus.NOT_ESTABLISHED).amount is None


def test_benefit_validation_preserves_unknown_and_intangible_value() -> None:
    """Missing is not zero and intangible value cannot receive arbitrary amounts."""
    assert hypothesis().amount is None
    with pytest.raises(ValueError, match="missing benefit"):
        hypothesis(evidence_status=EvidenceStatus.CUSTOMER_ESTIMATE)
    with pytest.raises(ValueError, match="intangible"):
        hypothesis(
            amount=EstimateRange(Decimal(1), Decimal(1)),
            value_kind=ValueKind.INTANGIBLE,
            evidence_status=EvidenceStatus.CUSTOMER_ESTIMATE,
        )


def test_scenario_inputs_are_decimal_explicit_and_immutable() -> None:
    """Experiments require Decimal, positive horizons, a basis, and experimental labels."""
    scenario = illustrative_scenarios()[1]
    with pytest.raises(FrozenInstanceError):
        scenario.horizon_months = 1  # type: ignore[misc]
    with pytest.raises(TypeError, match="Decimal"):
        replace(scenario, implementation_hours=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Experimental"):
        replace(scenario, classification=EvidenceStatus.ANALYST_ASSUMPTION)
    with pytest.raises(ValueError, match="positive"):
        replace(scenario, horizon_months=0)
    with pytest.raises(ValueError, match="positive"):
        replace(scenario, minutes_saved_per_inquiry=Decimal(-1))
    with pytest.raises(ValueError, match="hourly value"):
        replace(scenario, hourly_value_basis="")


def test_transparent_calculations_round_and_apply_safeguards() -> None:
    """Scenario arithmetic is deterministic and guarded ROI/payback preserve unknowns."""
    conservative, expected, optimistic = illustrative_scenarios()
    metrics = calculate_scenario(expected)
    assert metrics.one_time_cost == Decimal("360.00")
    assert metrics.recurring_cost == Decimal("720.00")
    assert metrics.annual_hours == Decimal("104.00")
    assert metrics.estimated_value == Decimal("3120.00")
    assert metrics.net_value == Decimal("2040.00")
    assert metrics.simple_roi == Decimal("1.8889")
    assert metrics.payback_months == Decimal("1.80")
    assert (
        calculate_scenario(conservative).net_value
        < metrics.net_value
        < calculate_scenario(optimistic).net_value
    )
    assert calculate_simple_roi(Decimal(10), Decimal(4)) == Decimal("1.5000")
    assert calculate_simple_roi(None, Decimal(4)) is None
    assert calculate_simple_roi(Decimal(1), None) is None
    assert calculate_simple_roi(Decimal(1), Decimal(0)) is None
    assert calculate_payback(Decimal(10), Decimal(2)) == Decimal("5.00")
    assert calculate_payback(None, Decimal(2)) is None
    assert calculate_payback(Decimal(2), None) is None
    assert calculate_payback(Decimal(2), Decimal(0)) is None
    assert (
        calculate_scenario(
            replace(
                expected,
                implementation_hours=Decimal(0),
                recurring_admin_hours_per_month=Decimal(0),
                hourly_value=Decimal(0),
            )
        ).simple_roi
        is None
    )
    assert (
        calculate_scenario(
            replace(expected, recurring_admin_hours_per_month=Decimal(20))
        ).payback_months
        is None
    )


def test_total_cost_never_converts_missing_or_incompatible_to_zero() -> None:
    """Only supported expected monetary amounts can be summed."""
    assert total_cost((money_cost(), money_cost()), CostTiming.ONE_TIME) == Decimal("4.00")
    without_expected = replace(money_cost(), amount=EstimateRange(Decimal(4), Decimal(6)))
    assert total_cost((without_expected,), CostTiming.ONE_TIME) == Decimal("4.00")
    assert total_cost((), CostTiming.ONE_TIME) is None
    assert (
        total_cost(
            (money_cost(amount=None, status=EvidenceStatus.NOT_ESTABLISHED),), CostTiming.ONE_TIME
        )
        is None
    )
    nonmoney = replace(money_cost(), unit=EstimateUnit.HOURS, currency=None)
    assert total_cost((nonmoney,), CostTiming.ONE_TIME) is None


def test_sensitivity_changes_one_input_without_mutation_or_randomness() -> None:
    """Supplied values retain order, use stable rounding, and leave source unchanged."""
    scenario = illustrative_scenarios()[1]
    result = sensitivity_analysis(scenario, (Decimal(1), Decimal(3), Decimal(5)))
    assert tuple(r.minutes_saved for r in result) == (Decimal(1), Decimal(3), Decimal(5))
    assert tuple(r.annual_hours for r in result) == (
        Decimal("26.00"),
        Decimal("78.00"),
        Decimal("130.00"),
    )
    assert scenario.minutes_saved_per_inquiry == Decimal(4)
    with pytest.raises(ValueError, match="negative"):
        sensitivity_analysis(scenario, (Decimal(-1),))


def test_guardrails_find_omissions_and_unsupported_promises() -> None:
    """Checks add no money, reject causal rhetoric, and keep supported hypotheses."""
    findings = detect_omitted_costs(harbor_street_music_solution_options(), ())
    assert tuple((f.subject_id, f.kind) for f in findings) == (
        ("APP-003", "Potential omitted cost"),
        ("APP-003", "Potential omitted cost"),
        ("APP-004", "Potential omitted cost"),
        ("APP-004", "Potential omitted cost"),
        ("APP-005", "Potential omitted cost"),
        ("APP-005", "Potential omitted cost"),
    )
    maintenance = replace(money_cost(), approach_id="APP-005", category=CostCategory.MAINTENANCE)
    assert len(detect_omitted_costs(harbor_street_music_solution_options(), (maintenance,))) == 5
    unsupported = hypothesis(
        category=BenefitCategory.REVENUE_OPPORTUNITY, hypothesis="Revenue may improve."
    )
    assert detect_unsupported_benefits((unsupported,))[0].kind == "Unsupported benefit claim"
    assert detect_unsupported_benefits((hypothesis(),)) == ()
    assert detect_unsupported_benefits((hypothesis(hypothesis="This will save time."),))
    assert detect_unsupported_benefits((hypothesis(hypothesis="It improves conversion by 30%."),))


def test_canonical_analysis_report_diagram_and_cli_are_neutral() -> None:
    """End-to-end output separates canonical unknowns and fictional scenarios."""
    analysis = analyze_harbor_street_value()
    assert analysis.readiness is CalculationReadiness.NOT_READY
    assert analysis.baseline.approach_id == "APP-007"
    assert len(analysis.approach_names) == 7
    assert analysis.scenarios[0][0].name.startswith("Conservative")
    assert analysis.scenarios[2][0].name.startswith("Optimistic")
    assert not hasattr(analysis, "recommendation")
    report = render_value_report(analysis)
    assert report.startswith("# Cost, Benefit, and Value Analysis")
    assert all(f"## {number}." in report for number in range(1, 22))
    assert "NOT READY" in report
    assert "Not Established" in report
    assert "fictional experiments" in report
    assert "does not select a winning approach" in report
    assert "E2 → REQ-001 → CAP-001 → APP-002 → BEN-001" in report
    assert "Future Decision Process" in render_value_mermaid()
    result = CliRunner().invoke(app, ["value"])
    assert result.exit_code == 0
    assert "Sensitivity Analysis" in result.stdout
    chapters = CliRunner().invoke(app, ["chapters"])
    assert "12. Cost, Benefit, and Value Analysis" in chapters.stdout
