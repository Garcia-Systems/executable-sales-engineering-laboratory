"""Tests for evidence-bounded Chapter 4 stakeholder analysis."""
# ruff: noqa: D103, PT007

from dataclasses import FrozenInstanceError, fields, replace
from typing import Any, cast

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.stakeholders import render_stakeholder_mermaid
from sales_lab.domain import (
    AuthorityState,
    DecisionAuthority,
    PerspectiveGap,
    ProcessParticipation,
    ResponsibilityCategory,
    StakeholderEvidence,
    StakeholderRelationship,
    StakeholderResponsibility,
    StakeholderRole,
)
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_business_process,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.stakeholders import (
    render_responsibility_matrix,
    render_stakeholder_report,
)
from sales_lab.services.stakeholders import StakeholderAnalysis, analyze_stakeholders, authority_for


def analysis_fixture() -> StakeholderAnalysis:
    """Build the deterministic scenario for focused assertions."""
    return analyze_stakeholders(
        harbor_street_music_business_process(), harbor_street_music_stakeholder_map()
    )


@pytest.mark.parametrize(
    "item",
    (
        StakeholderRole("role", "Role"),
        StakeholderEvidence("e", "Fact", "Source"),
        StakeholderResponsibility("role", ResponsibilityCategory.PERFORMS_WORK, "e"),
        ProcessParticipation("role", "step", "e"),
        DecisionAuthority("role", "Decision", AuthorityState.UNKNOWN, "e"),
        StakeholderRelationship("role", "other", "Works with", "e"),
        PerspectiveGap("gap", "Unknown.", "Who knows?"),
        harbor_street_music_stakeholder_map(),
    ),
)
def test_domain_objects_are_immutable(item: object) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(item, fields(cast("Any", item))[0].name, "changed")


def test_responsibilities_are_multiple_classified_and_evidenced() -> None:
    stakeholder_map = harbor_street_music_stakeholder_map()
    staff = tuple(item for item in stakeholder_map.responsibilities if item.role_id == "staff")
    assert {item.category for item in staff} == {
        ResponsibilityCategory.PERFORMS_WORK,
        ResponsibilityCategory.USES_SYSTEM,
        ResponsibilityCategory.AFFECTED_BY_CHANGE,
    }
    evidence_ids = {item.identifier for item in stakeholder_map.evidence}
    assert all(item.evidence_id in evidence_ids for item in stakeholder_map.responsibilities)


def test_participation_reuses_chapter_three_step_identifiers() -> None:
    analysis = analysis_fixture()
    step_ids = {step.identifier for step in analysis.process.steps}
    assert {item.step_id for item in analysis.stakeholder_map.participations} <= step_ids
    assert (
        ProcessParticipation("staff", "calendar", "E2") in analysis.stakeholder_map.participations
    )


def test_unknown_authority_is_not_no_and_missing_roles_remain_unknown() -> None:
    analysis = analysis_fixture()
    manager = next(role for role in analysis.stakeholder_map.roles if role.identifier == "manager")
    student = next(role for role in analysis.stakeholder_map.roles if role.identifier == "student")
    assert {AuthorityState.UNKNOWN} != {AuthorityState.NO}
    assert authority_for(analysis, manager) is AuthorityState.UNKNOWN
    assert authority_for(analysis, student) is AuthorityState.UNKNOWN


def test_gaps_generate_only_ordered_follow_up_questions() -> None:
    analysis = analysis_fixture()
    assert analysis.follow_up_questions == tuple(
        gap.follow_up_question for gap in analysis.missing_perspectives
    )
    assert analysis.follow_up_questions[0] == "Who maintains the spreadsheet and calendar accounts?"


def test_mermaid_matrix_and_report_are_deterministic() -> None:
    analysis = analysis_fixture()
    diagram = render_stakeholder_mermaid(analysis)
    matrix = render_responsibility_matrix(analysis)
    report = render_stakeholder_report(analysis)
    assert diagram == render_stakeholder_mermaid(analysis)
    assert "R1[Prospective Student or Parent]" in diagram
    assert "R3 -.->|Technology responsibility not established| R5" in diagram
    assert matrix.startswith("| Stakeholder | Performs Work")
    assert "| Store Manager | Not Established | Established | Unknown" in matrix
    assert report == render_stakeholder_report(analysis)
    headings = (
        "Engagement",
        "Stakeholder Roles",
        "Responsibilities",
        "Process Participation",
        "Decision Authority",
        "Stakeholder Relationships",
        "Evidence",
        "Missing Perspectives",
        "Follow-Up Questions",
        "Educational Limitations",
    )
    assert report.startswith("# Stakeholder Analysis\n")
    assert [report.index(f"## {heading}") for heading in headings] == sorted(
        report.index(f"## {heading}") for heading in headings
    )


def test_analysis_rejects_broken_references() -> None:
    process = harbor_street_music_business_process()
    stakeholder_map = harbor_street_music_stakeholder_map()
    with pytest.raises(ValueError, match="unknown process step"):
        analyze_stakeholders(
            process,
            replace(
                stakeholder_map, participations=(ProcessParticipation("staff", "missing", "E2"),)
            ),
        )
    with pytest.raises(ValueError, match="unknown role"):
        analyze_stakeholders(
            process,
            replace(
                stakeholder_map,
                responsibilities=(
                    StakeholderResponsibility(
                        "missing", ResponsibilityCategory.PERFORMS_WORK, "E2"
                    ),
                ),
            ),
        )
    with pytest.raises(ValueError, match="unknown evidence"):
        analyze_stakeholders(
            process,
            replace(
                stakeholder_map,
                responsibilities=(
                    StakeholderResponsibility(
                        "staff", ResponsibilityCategory.PERFORMS_WORK, "missing"
                    ),
                ),
            ),
        )
    with pytest.raises(ValueError, match="role identifiers must be unique"):
        analyze_stakeholders(
            process,
            replace(stakeholder_map, roles=(*stakeholder_map.roles, stakeholder_map.roles[0])),
        )
    with pytest.raises(ValueError, match="evidence identifiers must be unique"):
        analyze_stakeholders(
            process,
            replace(
                stakeholder_map, evidence=(*stakeholder_map.evidence, stakeholder_map.evidence[0])
            ),
        )


def test_no_numeric_scores_exist_in_domain_or_output() -> None:
    stakeholder_map = harbor_street_music_stakeholder_map()
    assert all("score" not in field.name for field in fields(stakeholder_map))
    report = render_stakeholder_report(analysis_fixture()).lower()
    assert "importance score" not in report
    assert "influence score" not in report


@pytest.mark.parametrize(
    "factory",
    (
        lambda: StakeholderRole("", "Role"),
        lambda: StakeholderEvidence("e", " ", "Source"),
        lambda: DecisionAuthority("role", "", AuthorityState.UNKNOWN, "e"),
        lambda: StakeholderRelationship("role", "other", "", "e"),
        lambda: PerspectiveGap("gap", "Unknown", " "),
    ),
)
def test_domain_text_rejects_blanks(factory: object) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        factory()  # type: ignore[operator]


def test_cli_prints_stakeholder_roles_gaps_and_report() -> None:
    result = CliRunner().invoke(app, ["stakeholders"])
    assert result.exit_code == 0
    assert result.stdout.startswith("# Stakeholder Analysis")
    assert "Front Desk Staff" in result.stdout
    assert "Final spending authority has not been established." in result.stdout
