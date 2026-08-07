"""Chapter 13 transparent risk-analysis tests."""

# ruff: noqa: PLR2004

from dataclasses import FrozenInstanceError, replace

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.risks import render_risk_lifecycle_mermaid, render_risk_relationship_mermaid
from sales_lab.domain.integrations import FeasibilityState
from sales_lab.domain.risks import (
    Applicability,
    AssumptionValidationStatus,
    DependencyStatus,
    QualitativeLevel,
    ResponseType,
    RiskCategory,
    RiskStatus,
)
from sales_lab.reports.risks import render_risk_report
from sales_lab.services.risks import (
    analyze_harbor_street_risks,
    analyze_risks,
    assumption_disproved_experiment,
    classify_statement,
    harbor_street_risk_register,
    mitigation_added_experiment,
)


def test_domain_is_immutable_and_structured() -> None:
    """Risks require cause, event, consequence, and categories and remain frozen."""
    risk = harbor_street_risk_register().risks[0]
    with pytest.raises(FrozenInstanceError):
        risk.event = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError, match="cause, event"):
        replace(risk, cause="")
    with pytest.raises(ValueError, match="category"):
        replace(risk, categories=())
    assert risk.categories == (RiskCategory.TECHNICAL, RiskCategory.INTEGRATION)
    assert set(RiskStatus) == {
        RiskStatus.IDENTIFIED,
        RiskStatus.UNDER_REVIEW,
        RiskStatus.RESPONSE_PLANNED,
        RiskStatus.ACCEPTED,
        RiskStatus.MITIGATED,
        RiskStatus.CLOSED,
    }
    assert len({QualitativeLevel.UNKNOWN, QualitativeLevel.NOT_EVALUATED}) == 2


def test_register_preserves_classifications_and_provenance() -> None:
    """Unknowns, established boundaries, issues, and premises stay separate."""
    register = harbor_street_risk_register()
    assert register.assumptions[0].validation_status is AssumptionValidationStatus.UNVALIDATED
    assert register.dependencies[0].status is DependencyStatus.UNRESOLVED
    assert register.constraints[0].identifier == "CON-001"
    assert register.constraints[0].identifier not in {risk.identifier for risk in register.risks}
    assert register.issues[0].identifier == "ISS-001"
    assert register.issues[0].identifier not in {risk.identifier for risk in register.risks}
    assert register.risks[0].evidence_ids == ("E2", "INT-UNKNOWN")
    semantic_states = {
        QualitativeLevel.UNKNOWN.value,
        FeasibilityState.NOT_FEASIBLE.value,
        "Absent",
    }
    assert len(semantic_states) == 3
    assert not hasattr(register, "risk_score")
    assert tuple(risk.identifier for risk in register.risks) == (
        "RISK-001",
        "RISK-002",
        "RISK-003",
        "RISK-004",
    )


def test_analysis_finds_omissions_without_inventing_risks() -> None:
    """The service derives omissions and validates references in stable order."""
    analysis = analyze_harbor_street_risks()
    assert analysis.unvalidated_assumptions == ()
    assert tuple(item.identifier for item in analysis.unresolved_dependencies) == (
        "DEP-001",
        "DEP-003",
    )
    assert tuple(item.identifier for item in analysis.risks_without_responses) == (
        "RISK-003",
        "RISK-004",
    )
    assert analysis.orphan_responses == ()
    bad = replace(
        analysis.register,
        risks=(replace(analysis.register.risks[0], evidence_ids=("MISSING",)),),
    )
    with pytest.raises(ValueError, match="unknown evidence"):
        analyze_risks(bad)
    extra = replace(analysis.register.responses[0], identifier="ORPHAN", risk_id="MISSING")
    orphan_analysis = analyze_risks(replace(analysis.register, responses=(extra,)))
    assert orphan_analysis.orphan_responses == (extra,)


def test_classification_guardrails_are_narrow_and_explicit() -> None:
    """Existing facts, constraints, and unsupported absence claims get distinct findings."""
    assert classify_statement("A neutral future possibility.") == ()
    assert classify_statement("The current process currently uses two tools.")[0].finding == (
        "Possible issue classification"
    )
    budget = classify_statement("No budget has been approved.")
    assert budget[0].finding == "Possible constraint or dependency"
    unsupported = classify_statement("The calendar has no API.", "Availability unknown")
    assert unsupported[0].finding == "Unsupported conclusion"
    assert classify_statement("The calendar is not feasible.", "unknown")[0].finding == (
        "Unsupported conclusion"
    )
    assert classify_statement("The interface is absent.", "unknown")[0].finding == (
        "Unsupported conclusion"
    )


def test_responses_distinguish_mitigation_contingency_and_residual_risk() -> None:
    """A response does not close a risk and consequences do not disappear."""
    analysis = analyze_harbor_street_risks()
    investigate, contingency, mitigation = analysis.register.responses
    assert investigate.response_type is ResponseType.INVESTIGATE
    assert contingency.response_type is ResponseType.CONTINGENCY
    assert mitigation.response_type is ResponseType.REDUCE
    assert analysis.register.residual_risks
    assert analysis.register.risks[0].status is RiskStatus.UNDER_REVIEW
    assert all(risk.status is not RiskStatus.CLOSED for risk in analysis.register.risks)


def test_profiles_and_matrix_are_applicability_not_ranking() -> None:
    """Profiles state explicit applicability and never total qualitative labels."""
    analysis = analyze_harbor_street_risks()
    configure, buy, build, status_quo = analysis.register.profiles
    assert configure.approach_name == "Configure Existing Tools"
    assert dict(build.entries)["RISK-003"] is Applicability.APPLICABLE
    assert dict(buy.entries)["RISK-003"] is Applicability.NOT_APPLICABLE
    assert all(value is Applicability.NOT_APPLICABLE for _, value in status_quo.entries)
    report = render_risk_report(analysis)
    assert "| Risk | Configure Existing Tools | Buy Commercial Software" in report
    assert "aggregate risk score" in report
    assert "hidden ranking" in report
    assert "Risk Score" not in report


def test_diagrams_and_report_cover_relationships_and_sections() -> None:
    """Generated artifacts are complete, deterministic, and educationally bounded."""
    analysis = analyze_harbor_street_risks()
    relationship = render_risk_relationship_mermaid(analysis)
    assert relationship.startswith("flowchart LR")
    assert "Mitigation --> Residual" in relationship
    assert "Risk --> Contingency" in relationship
    lifecycle = render_risk_lifecycle_mermaid()
    assert "ResponsePlanned --> Mitigated" in lifecycle
    assert "Mitigated --> UnderReview" in lifecycle
    report = render_risk_report(analysis)
    assert report.startswith("# Risk, Assumption, Dependency, and Constraint Analysis")
    assert all(f"## {number}." in report for number in range(1, 23))
    assert "UNKNOWN != NOT FEASIBLE" in report
    assert "Constraint != Risk" in report
    assert "E2 → REQ-004 → CAP-004" in report
    assert "BEN-001 → RISK-001" in report
    no_responses = replace(analysis.register, responses=())
    relationship_without = render_risk_relationship_mermaid(analyze_risks(no_responses))
    assert "Mitigation" not in relationship_without
    assert "Contingency" not in relationship_without
    empty_report = render_risk_report(
        analyze_risks(
            replace(
                analysis.register,
                responses=(),
                residual_risks=(),
                assumptions=(),
                dependencies=(),
                open_questions=(),
            )
        )
    )
    assert "## 12. Mitigations\n- None" in empty_report
    assert "## 13. Contingencies\n- None" in empty_report


def test_assumption_disproved_experiment_preserves_history() -> None:
    """New evidence disproves only the new premise and activates contingency relevance."""
    original = analyze_harbor_street_risks()
    experiment = assumption_disproved_experiment(original)
    assert experiment.original is original
    assert (
        original.register.assumptions[0].validation_status is AssumptionValidationStatus.UNVALIDATED
    )
    assert (
        experiment.updated.register.assumptions[0].validation_status
        is AssumptionValidationStatus.DISPROVED
    )
    assert experiment.integration_feasibility.startswith("Not feasible")
    assert experiment.relevant_contingency_id == "RESP-002"
    assert experiment.evidence.evidence_id == "EXP-API-ABSENT"
    assert experiment.updated.register.risks[0].status is RiskStatus.RESPONSE_PLANNED
    default_result = assumption_disproved_experiment()
    assert (
        default_result.updated.register.assumptions[0].validation_status
        is AssumptionValidationStatus.DISPROVED
    )


def test_mitigation_experiment_adds_plan_but_not_closure_or_score() -> None:
    """A new response and residual risk coexist with the unchanged original register."""
    original = analyze_harbor_street_risks()
    experiment = mitigation_added_experiment(original)
    assert experiment.original is original
    assert len(original.register.responses) == 3
    assert len(experiment.updated.register.responses) == 4
    assert experiment.updated.register.risks[2].status is RiskStatus.RESPONSE_PLANNED
    assert experiment.updated.register.residual_risks[-1].risk_id == "RISK-003"
    assert not hasattr(experiment.updated, "score")
    assert mitigation_added_experiment().validation_action.action.startswith("Conduct")


def test_cli_exposes_complete_chapter_13_analysis() -> None:
    """The command and chapter catalog expose deterministic Chapter 13 output."""
    result = CliRunner().invoke(app, ["risks"])
    assert result.exit_code == 0
    assert "RISK-001: Calendar integration feasibility" in result.stdout
    assert "Assumptions Register" in result.stdout
    assert "Residual Risks" in result.stdout
    assert "Classification Findings" in result.stdout
    assert "Traceability" in result.stdout
    chapters = CliRunner().invoke(app, ["chapters"])
    assert "13. Risks, Assumptions, Dependencies, and Constraints" in chapters.stdout
