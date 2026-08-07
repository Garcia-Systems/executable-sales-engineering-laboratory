"""Chapter 18 customer-success planning tests."""

# ruff: noqa: PLR2004 - explicit educational example values improve test readability.

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.success import render_success_lifecycle, render_success_loop
from sales_lab.domain.success import (
    Baseline,
    BaselineStatus,
    IndicatorTiming,
    MeasurementOwner,
    MeasurementReadiness,
    MeasureType,
    ObservationPeriodType,
    SuccessState,
    ValidationStatus,
)
from sales_lab.reports.success import (
    render_benefit_matrix,
    render_measurement_matrix,
    render_success_plan,
    render_success_review,
)
from sales_lab.services.success import (
    build_harbor_street_success_plan,
    experimental_reviews,
    validate_measurements,
)


def test_measurement_objects_and_states_are_explicit_and_immutable() -> None:
    """Implementation, adoption, outcomes, value, and acceptance remain distinct."""
    plan = build_harbor_street_success_plan()
    with pytest.raises(FrozenInstanceError):
        plan.engagement = "changed"  # type: ignore[misc]
    distinctions = {
        SuccessState.IMPLEMENTED,
        SuccessState.ADOPTED,
        SuccessState.OPERATIONALLY_EFFECTIVE,
        SuccessState.OUTCOME_OBSERVED,
        SuccessState.VALUE_VALIDATED,
    }
    assert len(distinctions) == 5
    assert plan.measures[0].success_criterion_ids[0] != plan.measures[0].identifier
    assert set(MeasureType) == {
        MeasureType.DELIVERY,
        MeasureType.ADOPTION,
        MeasureType.PROCESS,
        MeasureType.QUALITY,
        MeasureType.OUTCOME,
        MeasureType.VALUE,
        MeasureType.RISK,
        MeasureType.UNINTENDED_EFFECT,
    }
    assert set(ObservationPeriodType)
    assert {IndicatorTiming.LEADING, IndicatorTiming.LAGGING}


def test_baselines_preserve_unknown_and_validate_established_values() -> None:
    """A missing baseline is never silently converted to zero."""
    with pytest.raises(ValueError, match="requires a value"):
        Baseline(BaselineStatus.ESTABLISHED, "missing")
    with pytest.raises(ValueError, match="unknown, not zero"):
        Baseline(BaselineStatus.NOT_ESTABLISHED, "missing", Decimal(0))
    baseline = Baseline(BaselineStatus.ESTABLISHED, "fictional sample", Decimal(6))
    assert baseline.value == 6


def test_canonical_plan_is_planned_traceable_and_honest() -> None:
    """The canonical scenario reuses evidence without inventing implementation."""
    plan = build_harbor_street_success_plan()
    assert plan.lifecycle_status == "PROPOSED"
    assert all(row.observed_evidence == "NOT_OBSERVED" for row in plan.traceability)
    assert {m.readiness for m in plan.measures} >= {
        MeasurementReadiness.READY,
        MeasurementReadiness.PARTIALLY_READY,
        MeasurementReadiness.NOT_READY,
    }
    assert all(not consequence.observed for consequence in plan.unintended_consequences)
    assert all(not action.executed for action in plan.corrective_actions)
    assert all(
        item.validation_status is ValidationStatus.NOT_READY for item in plan.benefit_validations
    )
    assert any(item.follow_up_measure_id == "SM-006" for item in plan.benefit_validations)
    assert all(row.evidence_id.startswith("E") for row in plan.traceability)


def test_guardrails_find_missing_inputs_activity_and_unintended_effects() -> None:
    """Transparent findings reject vanity metrics and unsupported definitions."""
    measure = build_harbor_street_success_plan().measures[6]
    broken = replace(
        measure,
        definition="",
        unit="",
        evidence_source=replace(measure.evidence_source, name=""),
        observation_period=replace(measure.observation_period, identifier=""),
        target_condition=replace(measure.target_condition, population=""),
        measure_type=MeasureType.OUTCOME,
        activity_only=True,
    )
    kinds = {finding.kind for finding in validate_measurements((broken,))}
    assert kinds == {
        "Vague measure",
        "Missing baseline",
        "Missing evidence source",
        "Missing ownership",
        "Missing review period",
        "Unsupported target condition",
        "Potential vanity metric",
        "Unsupported outcome claim",
    }
    unintended_kinds = {finding.kind for finding in validate_measurements((measure,))}
    assert "Unintended effect measure" in unintended_kinds
    assert MeasurementOwner("staff role").established
    assert not MeasurementOwner("OWNER_NOT_ESTABLISHED").established


def test_reports_matrices_and_diagrams_are_stable_and_score_free() -> None:
    """Reports show readiness and evidence, never opaque scoring."""
    plan = build_harbor_street_success_plan()
    report = render_success_plan(plan)
    assert report == render_success_plan(plan)
    for section in range(1, 24):
        assert f"## {section}." in report
    assert "DELIVERED != IMPLEMENTED" in report
    assert "Missing baseline != zero" in report
    assert "health score" in report
    assert "readiness percentage" not in report
    assert "hidden ranking" in report
    assert "| SM-004 Duplicate Scheduling Effects | OUTCOME |" in render_measurement_matrix(plan)
    assert "BEN-001" in render_benefit_matrix(plan)
    assert "Correct --> Process" in render_success_loop()
    assert "MeasurementInProgress --> Inconclusive" in render_success_lifecycle()


def test_experiments_distinguish_adoption_outcome_causality_and_value() -> None:
    """Fictional observations do not mutate or overclaim the canonical plan."""
    plan = build_harbor_street_success_plan()
    before = plan
    positive, adoption, causality, unintended = experimental_reviews(plan)
    assert positive.observations[0].numerator / positive.observations[0].denominator == Decimal(
        "0.3"
    )
    assert positive.observations[1].numerator / positive.observations[1].denominator == Decimal(
        "0.9"
    )
    assert "does not prove" not in positive.outcome_findings[0].statement
    assert adoption.outcome_findings[0].state is SuccessState.ADOPTED
    assert adoption.benefit_validation[0].validation_status is ValidationStatus.NOT_SUPPORTED
    assert causality.outcome_findings[0].state is SuccessState.OUTCOME_OBSERVED
    assert causality.outcome_findings[0].causality is ValidationStatus.INCONCLUSIVE
    assert unintended.unintended_effects[0].observed
    assert not unintended.corrective_actions[0].executed
    assert plan == before
    for review in (positive, adoption, causality, unintended):
        rendered = render_success_review(review)
        assert "EXPERIMENTAL_MEASUREMENT_SCENARIO" in rendered
        assert "# Customer Success Review Report" in rendered


def test_cli_success_plan_experiments_and_invalid_scenario() -> None:
    """The CLI exposes canonical and explicitly fictional paths."""
    runner = CliRunner()
    canonical = runner.invoke(app, ["success"])
    assert canonical.exit_code == 0
    assert "Customer Success and Outcome Measurement Plan" in canonical.stdout
    assert "no approval, implementation, adoption" in canonical.stdout
    experimental = runner.invoke(app, ["success", "--scenario", "experimental"])
    assert experimental.exit_code == 0
    assert experimental.stdout.count("Customer Success Review Report") == 4
    invalid = runner.invoke(app, ["success", "--scenario", "invented"])
    assert invalid.exit_code == 2
    chapters = runner.invoke(app, ["chapters"])
    assert "18. Customer Success" in chapters.stdout
