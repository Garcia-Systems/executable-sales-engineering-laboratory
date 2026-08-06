"""Tests for the Chapter 2 discovery meeting workflow."""
# ruff: noqa: D103

from collections.abc import Callable
from dataclasses import FrozenInstanceError, fields
from typing import Any, cast

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.discovery_meeting import discovery_meeting_flowchart
from sales_lab.domain import (
    DiscoveryMeeting,
    DiscoveryQuestion,
    DiscoveryResponse,
    EvidenceRecord,
    FollowUpItem,
    MeetingParticipant,
    QuestionCategory,
    QuestionKind,
)
from sales_lab.examples.harbor_street_music import harbor_street_music_discovery_meeting
from sales_lab.question_catalog import DISCOVERY_QUESTION_CATALOG, questions_by_category
from sales_lab.reports.markdown import render_discovery_meeting_summary
from sales_lab.services.discovery_meeting import (
    build_discovery_meeting_summary,
    capture_evidence,
    generate_follow_up_items,
    record_question,
    record_response,
    unanswered_questions,
)

DOMAIN_OBJECTS = (
    MeetingParticipant("Name", "Role"),
    DiscoveryQuestion("id", QuestionCategory.DATA, "What is known?", QuestionKind.OPEN),
    DiscoveryResponse("id", "Name", "Response"),
    EvidenceRecord("Fact", "Source"),
    FollowUpItem("id", "Ask again"),
)


@pytest.mark.parametrize("item", DOMAIN_OBJECTS)
def test_meeting_objects_are_immutable(item: object) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(item, fields(cast("Any", item))[0].name, "changed")


def test_workflow_preserves_chronological_order_without_mutation() -> None:
    original = DiscoveryMeeting("Meeting", (MeetingParticipant("Name", "Role"),))
    first = DiscoveryQuestion("first", QuestionCategory.DATA, "First?", QuestionKind.OPEN)
    second = DiscoveryQuestion("second", QuestionCategory.PEOPLE, "Second?", QuestionKind.CLOSED)
    meeting = record_question(record_question(original, first), second)
    meeting = record_response(meeting, DiscoveryResponse("second", "Name", "Second answer"))
    meeting = record_response(meeting, DiscoveryResponse("first", "Name", "First answer"))
    meeting = capture_evidence(meeting, EvidenceRecord("First fact", "Name"))
    meeting = capture_evidence(meeting, EvidenceRecord("Second fact", "Name"))
    assert original.questions == ()
    assert meeting.questions == (first, second)
    assert tuple(item.question_id for item in meeting.responses) == ("second", "first")
    assert tuple(item.fact for item in meeting.evidence) == ("First fact", "Second fact")


def test_response_must_reference_a_recorded_unique_question() -> None:
    participant = (MeetingParticipant("Name", "Role"),)
    with pytest.raises(ValueError, match="reference a recorded question"):
        DiscoveryMeeting(
            "Meeting", participant, responses=(DiscoveryResponse("missing", "Name", "Answer"),)
        )
    duplicate = DiscoveryQuestion("same", QuestionCategory.DATA, "Question?", QuestionKind.OPEN)
    with pytest.raises(ValueError, match="identifiers must be unique"):
        DiscoveryMeeting("Meeting", participant, questions=(duplicate, duplicate))


@pytest.mark.parametrize(
    "constructor",
    [
        lambda: MeetingParticipant(" ", "Role"),
        lambda: MeetingParticipant("Name", " "),
        lambda: DiscoveryQuestion(" ", QuestionCategory.DATA, "Question?", QuestionKind.OPEN),
        lambda: DiscoveryQuestion("id", QuestionCategory.DATA, " ", QuestionKind.OPEN),
        lambda: DiscoveryResponse(" ", "Name", "Answer"),
        lambda: DiscoveryResponse("id", " ", "Answer"),
        lambda: DiscoveryResponse("id", "Name", " "),
        lambda: EvidenceRecord(" ", "Source"),
        lambda: EvidenceRecord("Fact", " "),
        lambda: FollowUpItem(" ", "Action"),
        lambda: FollowUpItem("id", " "),
        lambda: DiscoveryMeeting(" ", (MeetingParticipant("Name", "Role"),)),
    ],
)
def test_meeting_objects_reject_blank_text(constructor: Callable[[], object]) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        constructor()


def test_meeting_requires_a_participant() -> None:
    with pytest.raises(ValueError, match="participants must not be empty"):
        DiscoveryMeeting("Meeting", ())


def test_catalog_contains_each_category_and_distinguishes_question_kinds() -> None:
    assert {item.category for item in DISCOVERY_QUESTION_CATALOG} == set(QuestionCategory)
    assert {item.kind for item in DISCOVERY_QUESTION_CATALOG} == set(QuestionKind)
    for category in QuestionCategory:
        assert all(item.category is category for item in questions_by_category(category))


def test_unanswered_questions_and_follow_ups_retain_question_order() -> None:
    meeting = harbor_street_music_discovery_meeting()
    assert tuple(item.identifier for item in unanswered_questions(meeting)) == (
        "goals-1",
        "success-1",
    )
    assert generate_follow_up_items(meeting) == (
        FollowUpItem("goals-1", "Ask the customer: What prompted this conversation?"),
        FollowUpItem(
            "success-1", "Ask the customer: How would management measure a successful outcome?"
        ),
    )


def test_report_is_deterministic_evidence_bounded_and_formatted() -> None:
    meeting = harbor_street_music_discovery_meeting()
    summary = build_discovery_meeting_summary(meeting)
    report = render_discovery_meeting_summary(summary)
    assert report == render_discovery_meeting_summary(build_discovery_meeting_summary(meeting))
    headings = (
        "Meeting Participants",
        "Business Goals",
        "Customer Responses",
        "Evidence Collected",
        "Questions Still Open",
        "Follow-Up Actions",
        "Educational Limitations",
    )
    assert tuple(section.heading for section in summary.sections) == headings
    assert [report.index(f"## {heading}") for heading in headings] == sorted(
        report.index(f"## {heading}") for heading in headings
    )
    assert report.startswith("# Discovery Meeting Summary\n")
    assert "## Business Goals\n- None recorded." in report
    assert "Approximately 30 lesson inquiries arrive per week." in report
    assert "Management is unsure how many inquiries are ultimately lost." in report
    assert report.endswith("\n")
    for forbidden in ("CRM", "recommend buying", "proposed architecture"):
        assert forbidden not in report


def test_answered_business_goal_and_empty_categories_are_rendered_faithfully() -> None:
    question = DiscoveryQuestion(
        "goal", QuestionCategory.BUSINESS_GOALS, "What is the goal?", QuestionKind.OPEN
    )
    meeting = DiscoveryMeeting(
        "Meeting",
        (MeetingParticipant("Customer", "Manager"),),
        (question,),
        (DiscoveryResponse("goal", "Customer", "Understand the current process."),),
    )
    report = render_discovery_meeting_summary(build_discovery_meeting_summary(meeting))
    assert "## Business Goals\n- Understand the current process." in report
    assert "## Evidence Collected\n- None recorded." in report
    assert "## Questions Still Open\n- None recorded." in report
    assert "## Follow-Up Actions\n- None recorded." in report


def test_cli_discovery_prints_summary() -> None:
    result = CliRunner().invoke(app, ["discovery"])
    assert result.exit_code == 0
    assert result.stdout.startswith("# Discovery Meeting Summary")
    assert "## Questions Still Open" in result.stdout


def test_discovery_diagram_defers_design() -> None:
    diagram = discovery_meeting_flowchart()
    assert diagram == discovery_meeting_flowchart()
    assert diagram.startswith("flowchart LR")
    assert diagram.index("Discovery Meeting") < diagram.index("Future Requirements Gathering")
