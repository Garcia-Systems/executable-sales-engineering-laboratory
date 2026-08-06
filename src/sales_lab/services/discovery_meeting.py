"""Pure, deterministic workflow operations for discovery meetings."""

from dataclasses import dataclass, replace

from sales_lab.domain.discovery_meeting import (
    DiscoveryMeeting,
    DiscoveryQuestion,
    DiscoveryResponse,
    EvidenceRecord,
    FollowUpItem,
    QuestionCategory,
)
from sales_lab.services.situation_summary import SummarySection

EDUCATIONAL_LIMITATIONS = (
    "This summary contains only information recorded during the fictional meeting.",
    "Responses and evidence are records, not predictions, diagnoses, or interpretations.",
    "No product, vendor, architecture, prioritization, ROI, or implementation plan is suggested.",
    "Open questions require further evidence and professional judgment.",
)


@dataclass(frozen=True, slots=True)
class DiscoveryMeetingSummary:
    """Stable structured output for the discovery meeting report."""

    title: str
    sections: tuple[SummarySection, ...]


def record_question(meeting: DiscoveryMeeting, question: DiscoveryQuestion) -> DiscoveryMeeting:
    """Append a question without mutating or reordering the meeting."""
    return replace(meeting, questions=(*meeting.questions, question))


def record_response(meeting: DiscoveryMeeting, response: DiscoveryResponse) -> DiscoveryMeeting:
    """Append a customer response after validating its question reference."""
    return replace(meeting, responses=(*meeting.responses, response))


def capture_evidence(meeting: DiscoveryMeeting, evidence: EvidenceRecord) -> DiscoveryMeeting:
    """Append a sourced fact without interpreting it."""
    return replace(meeting, evidence=(*meeting.evidence, evidence))


def unanswered_questions(meeting: DiscoveryMeeting) -> tuple[DiscoveryQuestion, ...]:
    """Return recorded questions having no response, in question order."""
    answered = {response.question_id for response in meeting.responses}
    return tuple(question for question in meeting.questions if question.identifier not in answered)


def generate_follow_up_items(meeting: DiscoveryMeeting) -> tuple[FollowUpItem, ...]:
    """Create one transparent evidence-gathering action per open question."""
    return tuple(
        FollowUpItem(question.identifier, f"Ask the customer: {question.text}")
        for question in unanswered_questions(meeting)
    )


def _items(values: tuple[str, ...]) -> tuple[str, ...]:
    return values or ("None recorded.",)


def build_discovery_meeting_summary(meeting: DiscoveryMeeting) -> DiscoveryMeetingSummary:
    """Build an evidence-bounded summary while retaining all recorded ordering."""
    question_by_id = {question.identifier: question for question in meeting.questions}
    business_goals = tuple(
        response.text
        for response in meeting.responses
        if question_by_id[response.question_id].category is QuestionCategory.BUSINESS_GOALS
    )
    responses = tuple(
        f"{question_by_id[item.question_id].text} — {item.respondent}: {item.text}"
        for item in meeting.responses
    )
    evidence = tuple(f"{item.fact} (Source: {item.source})" for item in meeting.evidence)
    open_questions = tuple(item.text for item in unanswered_questions(meeting))
    follow_ups = tuple(item.action for item in generate_follow_up_items(meeting))
    return DiscoveryMeetingSummary(
        title="Discovery Meeting Summary",
        sections=(
            SummarySection(
                "Meeting Participants",
                tuple(f"{item.name} — {item.role}" for item in meeting.participants),
            ),
            SummarySection("Business Goals", _items(business_goals)),
            SummarySection("Customer Responses", _items(responses)),
            SummarySection("Evidence Collected", _items(evidence)),
            SummarySection("Questions Still Open", _items(open_questions)),
            SummarySection("Follow-Up Actions", _items(follow_ups)),
            SummarySection("Educational Limitations", EDUCATIONAL_LIMITATIONS),
        ),
    )
