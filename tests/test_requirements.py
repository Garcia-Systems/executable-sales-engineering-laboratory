"""Tests for Chapter 5 evidence-traceable requirements."""
# ruff: noqa: D103

from dataclasses import FrozenInstanceError, replace

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.requirements import render_requirements_mermaid
from sales_lab.domain.requirements import (
    AcceptanceCriterion,
    Requirement,
    RequirementSet,
    RequirementStatus,
    RequirementType,
    UnresolvedRequirement,
)
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_requirements,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.requirements import render_requirements_report, render_traceability_matrix
from sales_lab.services.requirements import (
    RequirementsAnalysis,
    analyze_requirements,
    contains_solution_language,
)


def _analysis() -> RequirementsAnalysis:
    return analyze_requirements(
        harbor_street_music_requirements(), harbor_street_music_stakeholder_map()
    )


@pytest.mark.parametrize(
    "item",
    [
        AcceptanceCriterion("AC", "state", "event", "outcome"),
        Requirement("R", "Statement", RequirementType.FUNCTIONAL, "staff", ("E2",)),
        UnresolvedRequirement("Authentication"),
        harbor_street_music_requirements(),
    ],
)
def test_requirement_domain_is_immutable(item: object) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(item, next(iter(item.__dataclass_fields__)), "changed")  # type: ignore[attr-defined]


def test_categories_and_traceability_reuse_stakeholder_evidence() -> None:
    requirement_set = harbor_street_music_requirements()
    assert tuple(RequirementType) == (
        RequirementType.FUNCTIONAL,
        RequirementType.NON_FUNCTIONAL,
        RequirementType.BUSINESS_RULE,
        RequirementType.CONSTRAINT,
        RequirementType.SUCCESS_CRITERION,
    )
    assert [item.identifier for item in requirement_set.requirements] == [
        "REQ-001",
        "REQ-002",
        "REQ-003",
    ]
    evidence = {item.identifier for item in harbor_street_music_stakeholder_map().evidence}
    assert all(set(item.source_evidence_ids) <= evidence for item in requirement_set.requirements)
    assert requirement_set.requirements[1].stakeholder_id == "instructor"
    assert requirement_set.requirements[0].acceptance_criteria[0].then == (
        "the recorded status is available"
    )


def test_unknown_is_not_not_required() -> None:
    assert {RequirementStatus.UNKNOWN} != {RequirementStatus.NOT_REQUIRED}
    assert all(
        item.status is RequirementStatus.UNKNOWN
        for item in harbor_street_music_requirements().unresolved
    )


@pytest.mark.parametrize(
    "statement",
    [
        "Buy a CRM",
        "Install software",
        "Replace the spreadsheet with a CRM",
        "Use Salesforce",
        "Build an app",
        "Move to AWS",
        "Implement a CRM",
    ],
)
def test_solution_language_is_detected(statement: str) -> None:
    assert contains_solution_language(statement)


def test_invalid_candidates_produce_transparent_findings() -> None:
    criterion = AcceptanceCriterion("AC", "x", "y", "z")
    candidates = (
        Requirement(
            "DUP",
            "A clear statement",
            RequirementType.FUNCTIONAL,
            "staff",
            ("E2",),
            (criterion,),
            conflicts_with=("OTHER",),
        ),
        Requirement(
            "DUP", "Buy a CRM that is fast", RequirementType.FUNCTIONAL, "missing", ("missing",)
        ),
        Requirement("", "", RequirementType.FUNCTIONAL, "staff", ()),
        Requirement(
            "OTHER",
            "Observable statement",
            RequirementType.BUSINESS_RULE,
            "staff",
            ("E2",),
            (criterion,),
            conflicts_with=("DUP",),
        ),
    )
    result = analyze_requirements(
        RequirementSet("Engagement", candidates, ()), harbor_street_music_stakeholder_map()
    )
    codes = {item.code for item in result.findings}
    assert codes == {
        "DUPLICATE_ID",
        "SOLUTION_LANGUAGE",
        "AMBIGUOUS_LANGUAGE",
        "UNKNOWN_STAKEHOLDER",
        "UNKNOWN_EVIDENCE",
        "MISSING_ACCEPTANCE_CRITERIA",
        "BLANK_ID",
        "BLANK_STATEMENT",
        "MISSING_EVIDENCE",
        "EXPLICIT_CONFLICT",
    }
    assert result.accepted_requirements == ()


def test_unknown_conflict_reference_is_not_promoted_to_an_explicit_conflict() -> None:
    criterion = AcceptanceCriterion("AC-X", "state", "event", "outcome")
    requirement = Requirement(
        "REQ-X",
        "Staff must record a status.",
        RequirementType.FUNCTIONAL,
        "staff",
        ("E2",),
        (criterion,),
        conflicts_with=("REQ-NOT-AUTHORED",),
    )
    analysis = analyze_requirements(
        RequirementSet("Engagement", (requirement,), ()),
        harbor_street_music_stakeholder_map(),
    )
    assert all(item.code != "EXPLICIT_CONFLICT" for item in analysis.findings)


def test_matrix_report_and_diagram_are_deterministic() -> None:
    analysis = _analysis()
    matrix = render_traceability_matrix(analysis)
    assert matrix == render_traceability_matrix(analysis)
    assert "| REQ-001 | Functional | Front Desk Staff | E2 | Established |" in matrix
    report = render_requirements_report(analysis)
    assert report == render_requirements_report(analysis)
    headings = (
        "Engagement",
        "Requirements Overview",
        "Functional Requirements",
        "Non-Functional Requirements",
        "Business Rules",
        "Constraints",
        "Success Criteria",
        "Acceptance Criteria",
        "Evidence Traceability",
        "Requirements Not Yet Established",
        "Validation Findings",
        "Educational Limitations",
    )
    assert [report.index(f"## {item}") for item in headings] == sorted(
        report.index(f"## {item}") for item in headings
    )
    assert "UNKNOWN does not mean NOT REQUIRED" in report
    assert "No validation findings." in report
    assert render_requirements_mermaid().startswith("flowchart LR")
    assert "Evidence[Discovery Evidence] --> Requirements" in report


def test_matrix_handles_unresolved_display_references() -> None:
    source = harbor_street_music_requirements()
    candidate = Requirement("", "Statement", RequirementType.NON_FUNCTIONAL, "", ())
    analysis = analyze_requirements(
        replace(source, requirements=(candidate,)), harbor_street_music_stakeholder_map()
    )
    assert (
        "| (blank) | Non-Functional | (blank) | None | Established |"
        in render_traceability_matrix(analysis)
    )


def test_cli_prints_requirements_analysis() -> None:
    result = CliRunner().invoke(app, ["requirements"])
    assert result.exit_code == 0
    assert result.stdout.startswith("# Requirements Analysis")
    assert "REQ-001" in result.stdout
    assert "Authentication: Not Established" in result.stdout
    assert "Future Capability Mapping" in result.stdout
