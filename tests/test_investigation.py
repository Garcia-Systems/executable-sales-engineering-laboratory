"""Tests for Chapter 1 evidence classification and investigation."""
# ruff: noqa: D103

from dataclasses import FrozenInstanceError

import pytest

from sales_lab.diagrams.investigation import investigation_flowchart
from sales_lab.domain import (
    Assumption,
    CustomerStatement,
    InvestigationQuestion,
    Observation,
    ProblemHypothesis,
    UnknownInformation,
    VerifiedFact,
)
from sales_lab.examples.harbor_street_music import harbor_street_music_discovery
from sales_lab.reports.markdown import render_initial_discovery_assessment
from sales_lab.services.investigation import (
    DiscoveryEvidence,
    build_initial_discovery_assessment,
    classify_information,
    investigation_questions,
)

INFORMATION_TYPES = (
    CustomerStatement,
    Observation,
    VerifiedFact,
    Assumption,
    InvestigationQuestion,
    ProblemHypothesis,
    UnknownInformation,
)


@pytest.mark.parametrize("information_type", INFORMATION_TYPES)
def test_information_objects_are_immutable(information_type: type[object]) -> None:
    item = information_type("Evidence")  # type: ignore[call-arg]
    with pytest.raises(FrozenInstanceError):
        item.text = "Changed"  # type: ignore[attr-defined]


@pytest.mark.parametrize("information_type", INFORMATION_TYPES)
def test_information_objects_reject_blank_text(information_type: type[object]) -> None:
    with pytest.raises(ValueError, match="text must not be blank"):
        information_type(" ")  # type: ignore[call-arg]


def test_classification_preserves_category_and_insertion_order() -> None:
    evidence = DiscoveryEvidence(
        customer_statements=(CustomerStatement("First"), CustomerStatement("Second")),
        observations=(Observation("Observed"),),
        verified_facts=(VerifiedFact("Verified"),),
        questions=(InvestigationQuestion("Question?"),),
        hypotheses=(ProblemHypothesis("Possible problem"),),
        unknown_information=(UnknownInformation("Unknown"),),
    )
    classified = classify_information(evidence)
    assert classified.customer_statements == ("First", "Second")
    assert classified.observations == ("Observed",)
    assert classified.verified_facts == ("Verified",)
    assert classified.open_questions == ("Question?",)
    assert classified.hypotheses == ("Possible problem",)
    assert classified.unknown_information == ("Unknown",)


def test_assumption_cannot_be_stored_as_verified_fact() -> None:
    with pytest.raises(TypeError, match="verified_facts accepts only VerifiedFact objects"):
        DiscoveryEvidence(verified_facts=(Assumption("Unverified"),))  # type: ignore[arg-type]


def test_every_discovery_category_rejects_a_wrong_type() -> None:
    fields = (
        "customer_statements",
        "observations",
        "assumptions",
        "questions",
        "hypotheses",
        "unknown_information",
    )
    for field in fields:
        with pytest.raises(TypeError, match=f"{field} accepts only"):
            DiscoveryEvidence(**{field: (VerifiedFact("Wrong category"),)})  # type: ignore[arg-type]


def test_investigation_questions_are_fixed_and_keep_recorded_questions_first() -> None:
    recorded = InvestigationQuestion("What evidence is available?")
    evidence = DiscoveryEvidence(questions=(recorded,))
    first = investigation_questions(evidence)
    assert first == investigation_questions(evidence)
    assert first[0] is recorded
    assert tuple(item.text for item in first[1:]) == (
        "How many inquiries arrive each week?",
        "Who contacts prospective students?",
        "How is follow-up tracked?",
        "When does information become unavailable?",
        "Which systems currently contain student information?",
        "What counts as a missed inquiry?",
    )


def test_report_is_deterministic_and_has_required_section_order() -> None:
    evidence = harbor_street_music_discovery()
    assessment = build_initial_discovery_assessment(evidence)
    report = render_initial_discovery_assessment(assessment)
    assert report == render_initial_discovery_assessment(
        build_initial_discovery_assessment(evidence)
    )
    headings = (
        "Customer Statement",
        "Known Facts",
        "Observations",
        "Assumptions to Avoid",
        "Questions Requiring Investigation",
        "Possible Problem Hypotheses",
        "Educational Limitations",
    )
    assert tuple(section.heading for section in assessment.sections) == headings
    positions = [report.index(f"## {heading}") for heading in headings]
    assert positions == sorted(positions)
    assert "Students keep slipping through the cracks." in report
    assert "## Observations\n- None recorded." in report
    assert "## Possible Problem Hypotheses\n- None recorded." in report
    assert report.endswith("\n")


def test_mermaid_flow_is_deterministic_and_defers_recommendations() -> None:
    diagram = investigation_flowchart()
    assert diagram == investigation_flowchart()
    assert diagram.startswith("flowchart TD")
    assert "Customer Statement" in diagram
    assert "No recommendations in Chapter 1" in diagram
