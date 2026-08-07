"""Chapter 15 demonstration evidence and guardrail tests."""

# ruff: noqa: PLR2004

from dataclasses import FrozenInstanceError, replace

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.demonstrations import (
    render_demonstration_lifecycle,
    render_demonstration_sequence,
)
from sales_lab.domain.demonstrations import (
    DemonstrationAudience,
    DemonstrationFindingState,
    DemonstrationType,
    ProofOfConceptStatus,
)
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_requirements,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.demonstrations import render_demonstration_report
from sales_lab.services.decisions import harbor_street_decision_package
from sales_lab.services.demonstrations import (
    duplicate_confirmation_experiment,
    execute_harbor_street_demonstration,
    harbor_street_demonstration_plan,
    missing_information_experiment,
    unsupported_claim_experiment,
    validate_demonstration_plan,
)


def _validate(plan: object) -> tuple[str, ...]:
    return validate_demonstration_plan(
        plan,  # type: ignore[arg-type]
        harbor_street_music_requirements(),
        harbor_street_decision_package().recommendation.conditions,
        harbor_street_music_stakeholder_map(),
    )


def test_types_are_distinct_and_domain_is_immutable() -> None:
    """Demo, POC, pilot, and production remain separate lifecycle concepts."""
    plan = harbor_street_demonstration_plan()
    types = {
        DemonstrationType.SOLUTION_DEMONSTRATION,
        DemonstrationType.PROOF_OF_CONCEPT,
        DemonstrationType.PILOT,
        DemonstrationType.PRODUCTION_IMPLEMENTATION,
    }
    assert len(types) == 4
    with pytest.raises(FrozenInstanceError):
        plan.engagement = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        plan.scenario.initial_status = "changed"  # type: ignore[misc]


def test_canonical_plan_has_audience_order_conditions_and_traceability() -> None:
    """The plan reuses Chapter 4, 5, and 14 identifiers and needs no guardrail finding."""
    plan = harbor_street_demonstration_plan()
    assert [step.order for step in plan.steps] == list(range(1, 10))
    assert plan.success_conditions
    assert plan.failure_conditions
    assert plan.limitations
    assert {item.role_id for item in plan.audience} == {"staff", "manager", "instructor"}
    assert {"REQ-001", "AC-001", "RC-001", "RC-005"} <= set(plan.objective.trace_ids)
    assert _validate(plan) == ()


def test_validation_detects_vague_theatre_bad_audience_order_and_traceability() -> None:
    """A scripted success path cannot hide unsupported assumptions."""
    plan = harbor_street_demonstration_plan()
    invalid = replace(
        plan,
        objective=replace(
            plan.objective, statement="Show the customer the new system", trace_ids=()
        ),
        audience=(DemonstrationAudience("unknown", "Unknown", "Attend."),),
        steps=(replace(plan.steps[0], order=2, trace_ids=()),),
        success_conditions=(),
        failure_conditions=(),
        limitations=(),
        claims=("The solution is production ready.",),
    )
    findings = " ".join(_validate(invalid))
    for expected in (
        "Vague objective",
        "Invalid audience",
        "Invalid step order",
        "demo theatre",
        "Missing traceability",
        "Unsupported demonstration step",
        "production-readiness",
    ):
        assert expected.casefold() in findings.casefold()


def test_execution_preserves_observation_interpretation_and_failure_visibility() -> None:
    """Evidence passes narrowly, retains limitations, and never confers readiness."""
    report = execute_harbor_street_demonstration()
    assert report == execute_harbor_street_demonstration()
    assert report.evidence_artifacts
    assert all(item.observation != item.interpretation for item in report.observed_results)
    assert any(item.state is DemonstrationFindingState.PASSED for item in report.findings)
    assert any(item.state is DemonstrationFindingState.INCONCLUSIVE for item in report.findings)
    assert len({DemonstrationFindingState.INCONCLUSIVE, DemonstrationFindingState.FAILED}) == 2
    assert not report.production_ready
    assert report.plan.failure_conditions  # Failure conditions remain visible after passing.
    assert report.poc_questions[0].status is ProofOfConceptStatus.NOT_EXECUTED
    assert len(report.requirement_coverage) == 3
    assert len(report.condition_coverage) == 5


def test_experiments_are_isolated_and_have_no_external_effects() -> None:
    """Duplicate and incomplete inputs operate only on immutable scenario copies."""
    canonical = harbor_street_demonstration_plan().scenario
    duplicate = duplicate_confirmation_experiment()
    missing = missing_information_experiment()
    assert duplicate.original_scenario == canonical
    assert duplicate.scheduling_effects == 1
    assert "duplicate recognized" in duplicate.observations[1].casefold()
    assert missing.original_scenario == canonical
    assert missing.scheduling_effects == 0
    assert missing.finding is DemonstrationFindingState.FAILED
    assert harbor_street_demonstration_plan().scenario == canonical


def test_unsupported_revenue_claim_is_flagged() -> None:
    """A technical result cannot establish a financial outcome."""
    report = unsupported_claim_experiment()
    assert report.unsupported_claims == (
        "Unsupported demonstration claim: the demonstration does not measure or establish "
        "revenue impact.",
    )


def test_diagrams_and_report_are_deterministic_and_bounded() -> None:
    """Text evidence identifies simulation, coverage, POC, and readiness limits."""
    report = execute_harbor_street_demonstration()
    sequence = render_demonstration_sequence(report.plan)
    lifecycle = render_demonstration_lifecycle()
    markdown = render_demonstration_report(report)
    assert sequence == render_demonstration_sequence(report.plan)
    assert "Simulated Scheduling Handoff" in sequence
    assert "Finding --> Decision[Future Decision]" in lifecycle
    assert markdown.startswith("# Technical Demonstration and Proof-of-Concept Report")
    for section in range(1, 24):
        assert f"## {section}." in markdown
    assert "Production ready: **false**" in markdown
    assert "RC-005" in markdown
    assert "REQ-001" in markdown


def test_demo_cli_runs_canonical_demonstration() -> None:
    """The learner command prints useful deterministic evidence."""
    result = CliRunner().invoke(app, ["demo"])
    assert result.exit_code == 0
    for text in ("INQ-DEMO-001", "Observed Results", "Traceability", "Not Executed", "Limitations"):
        assert text in result.stdout
