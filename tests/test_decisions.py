"""Chapter 14 transparent decision analysis tests."""

# ruff: noqa: PLR2004

from dataclasses import FrozenInstanceError, fields, replace

import pytest

from sales_lab.diagrams.decisions import render_decision_mermaid
from sales_lab.domain.decisions import (
    ConditionKind,
    ConditionStatus,
    ConfidenceLevel,
    CriterionType,
    DecisionCriterion,
    EvidenceStrength,
    FindingState,
    RecommendationConfidence,
    RecommendationType,
    StakeholderPerspective,
    numeric_decision_fields,
)
from sales_lab.reports.decisions import _bullets, render_comparison_matrix, render_decision_report
from sales_lab.services.decisions import (
    harbor_street_decision_package,
    integration_evidence_experiment,
    scale_evidence_experiment,
    validate_decision,
)


def test_decision_package_is_immutable_and_qualitative() -> None:
    """All authored decision records are frozen and contain no scoring machinery."""
    package = harbor_street_decision_package()
    with pytest.raises(FrozenInstanceError):
        package.context = "changed"  # type: ignore[misc]
    assert {item.criterion_type for item in package.criteria} <= set(CriterionType)
    assert {item.kind for item in package.mandatory_conditions} == {
        ConditionKind.MANDATORY,
        ConditionKind.PREFERENCE,
    }
    assert {item.status for item in package.mandatory_conditions} <= set(ConditionStatus)
    assert {
        finding.evidence_strength for item in package.evaluations for finding in item.findings
    } <= set(EvidenceStrength)
    distinct_states: set[FindingState] = {FindingState.UNKNOWN, FindingState.DISQUALIFIED}
    assert len(distinct_states) == 2
    assert numeric_decision_fields() == ()
    assert not any(
        field.name in {"score", "weight", "total", "rank"} for field in fields(type(package))
    )


def test_canonical_recommendation_is_authored_conditional_and_not_approval() -> None:
    """The service validates an explicit judgment rather than choosing from values."""
    package = harbor_street_decision_package()
    recommendation = package.recommendation
    assert recommendation.recommendation_type is RecommendationType.PROCEED_CONDITIONALLY
    assert recommendation.approach_ids == ("APP-001", "APP-002")
    assert len(recommendation.conditions) == 5
    assert recommendation.confidence.level is ConfidenceLevel.MODERATE
    assert recommendation.confidence.basis
    assert recommendation.alternatives
    assert recommendation.change_triggers
    assert not recommendation.approved
    assert package.professional_judgment.rationale
    assert package.traceability[0][0] == "E2"
    assert package.traceability[0][-1] == "REC-001"


def test_validation_rejects_incoherent_or_authoritative_package() -> None:
    """Every required decision guardrail contributes a deterministic finding."""
    package = harbor_street_decision_package()
    recommendation = replace(
        package.recommendation,
        recommendation_type=RecommendationType.PROCEED,
        approach_ids=("MISSING",),
        evidence_ids=(),
        conditions=(),
        confidence=RecommendationConfidence(ConfidenceLevel.HIGH, ""),
        change_triggers=(),
        approved=True,
    )
    invalid = replace(
        package,
        professional_judgment=replace(package.professional_judgment, rationale=""),
        perspectives=(
            StakeholderPerspective("staff", "Staff", "All agree.", claims_agreement=True),
        ),
        recommendation=recommendation,
    )
    with pytest.raises(ValueError, match="supporting approach") as error:
        validate_decision(invalid)
    message = str(error.value)
    assert "supporting approach" in message
    assert "traceable evidence" in message
    assert "written basis" in message
    assert "requires a rationale" in message
    assert "agreement requires evidence" in message
    assert "change triggers" in message
    assert "cannot approve" in message


def test_validation_rejects_unmet_condition_conditional_omission_and_disqualification() -> None:
    """Proceed states cannot conceal mandatory conditions or disqualification."""
    package = harbor_street_decision_package()
    selected = tuple(
        replace(item, disqualified=True) if item.approach_id == "APP-002" else item
        for item in package.evaluations
    )
    recommendation = replace(
        package.recommendation,
        recommendation_type=RecommendationType.PROCEED,
        conditions=(),
    )
    with pytest.raises(ValueError, match=r"ignores.*disqualified"):
        validate_decision(replace(package, evaluations=selected, recommendation=recommendation))
    conditional = replace(
        recommendation, recommendation_type=RecommendationType.PROCEED_CONDITIONALLY
    )
    with pytest.raises(ValueError, match="conditional recommendation requires conditions"):
        validate_decision(replace(package, recommendation=conditional))


def test_validation_rejects_hidden_numeric_decision_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A future numeric score field cannot silently enter recommendation logic."""
    package = harbor_street_decision_package()
    monkeypatch.setattr(
        "sales_lab.services.decisions.numeric_decision_fields",
        lambda: ("score",),
    )
    with pytest.raises(ValueError, match="hidden numeric decision field detected"):
        validate_decision(package)


def test_matrix_report_and_mermaid_are_deterministic_and_non_numeric() -> None:
    """Presentation exposes findings and authority boundaries without arithmetic selection."""
    package = harbor_street_decision_package()
    matrix = render_comparison_matrix(package)
    report = render_decision_report(package)
    mermaid = render_decision_mermaid(package)
    assert matrix == render_comparison_matrix(package)
    assert "Requirement coverage" in matrix
    assert "Total" not in matrix
    assert "winner" not in matrix.casefold()
    assert report.startswith("# Decision Analysis and Recommendation")
    assert "## 20. Educational Limitations" in report
    assert "does not approve" in report
    assert "no total, weight, arithmetic winner" in report.casefold()
    assert "Recommendation --> Triggers" in mermaid
    assert _bullets(()) == "- None recorded."
    with pytest.raises(ValueError, match="requires criteria"):
        render_decision_mermaid(replace(package, criteria=()))


def test_integration_experiment_changes_viability_not_original_recommendation() -> None:
    """New technical evidence updates one finding without forcing a recommendation."""
    original = harbor_street_decision_package()
    experiment = integration_evidence_experiment(original)
    finding = next(
        finding
        for evaluation in experiment.updated.evaluations
        for finding in evaluation.findings
        if finding.approach_id == "APP-003"
    )
    assert experiment.original is original
    assert experiment.updated.recommendation is original.recommendation
    assert finding.state is FindingState.ESTABLISHED
    assert finding.evidence_strength is EvidenceStrength.EXPERIMENTAL
    assert experiment.changed_findings
    assert (
        integration_evidence_experiment().original.recommendation.statement
        == original.recommendation.statement
    )


def test_scale_experiment_exposes_reassessment_without_a_new_conclusion() -> None:
    """Scale evidence changes concerns while preserving unresolved dependencies."""
    original = harbor_street_decision_package()
    experiment = scale_evidence_experiment(original)
    assert experiment.original is original
    assert experiment.updated.recommendation is original.recommendation
    assert len(experiment.updated.risks_and_unknowns) == len(original.risks_and_unknowns) + 1
    assert "does not by itself" in experiment.interpretation
    assert scale_evidence_experiment().new_evidence


def test_decision_criterion_can_represent_engagement_specific_traceability() -> None:
    """A criterion remains an immutable description, not a universal weighting."""
    criterion = DecisionCriterion(
        "C", CriterionType.TIME_TO_LEARN, "Learn before commitment.", ("E",)
    )
    assert criterion.trace_ids == ("E",)
