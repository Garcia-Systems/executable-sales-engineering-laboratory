"""Learner-owned breakpoint path for Chapter 2."""

from sales_lab.domain import (
    DiscoveryMeeting,
    DiscoveryQuestion,
    DiscoveryResponse,
    EvidenceRecord,
    MeetingParticipant,
    QuestionCategory,
    QuestionKind,
)
from sales_lab.reports.markdown import render_discovery_meeting_summary
from sales_lab.services.discovery_meeting import (
    build_discovery_meeting_summary,
    capture_evidence,
    record_question,
    record_response,
)

meeting = DiscoveryMeeting(
    "Practice discovery meeting", (MeetingParticipant("Customer", "Manager"),)
)  # Breakpoint 1: inspect the initial immutable meeting.
question = DiscoveryQuestion(
    "process",
    QuestionCategory.CURRENT_PROCESS,
    "How does the process work today?",
    QuestionKind.OPEN,
)
meeting = record_question(meeting, question)  # Breakpoint 2: compare old and new tuple values.
meeting = record_response(
    meeting, DiscoveryResponse("process", "Customer", "We record each inquiry in a spreadsheet.")
)  # Breakpoint 3: inspect the ordered response tuple.
meeting = capture_evidence(
    meeting, EvidenceRecord("Each inquiry is recorded in a spreadsheet.", "Customer response")
)  # Breakpoint 4: inspect evidence separately from the response.
summary = build_discovery_meeting_summary(meeting)
report = render_discovery_meeting_summary(summary)  # Breakpoint 5: inspect deterministic output.

if __name__ == "__main__":
    print(report, end="")  # noqa: T201
