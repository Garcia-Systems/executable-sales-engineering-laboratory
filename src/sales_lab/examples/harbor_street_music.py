"""Reusable Chapter 0 customer-supplied facts."""

from sales_lab.domain.business_process import (
    BusinessProcess,
    DecisionPoint,
    InformationArtifact,
    ProcessActor,
    ProcessBoundary,
    ProcessStep,
    WorkflowTransition,
)
from sales_lab.domain.customer_situation import CustomerSituation
from sales_lab.domain.discovery import (
    Assumption,
    CustomerStatement,
    UnknownInformation,
    VerifiedFact,
)
from sales_lab.domain.discovery_meeting import (
    DiscoveryMeeting,
    DiscoveryResponse,
    EvidenceRecord,
    MeetingParticipant,
)
from sales_lab.question_catalog import DISCOVERY_QUESTION_CATALOG
from sales_lab.services.discovery_meeting import capture_evidence, record_question, record_response
from sales_lab.services.investigation import DiscoveryEvidence


def harbor_street_music_situation() -> CustomerSituation:
    """Return the fixed Harbor Street Music introductory situation."""
    return CustomerSituation(
        organization_name="Harbor Street Music",
        industry="community music retail and education",
        stated_concern="Lesson inquiries sometimes require repeated follow-up.",
        current_process=(
            "Inquiries are entered into a shared spreadsheet.",
            "Confirmed appointments are copied manually into a separate calendar.",
        ),
        known_constraints=("The organization has not yet approved a software budget.",),
        source_notes=("Information supplied during an introductory conversation.",),
    )


def harbor_street_music_discovery() -> DiscoveryEvidence:
    """Return Chapter 1 evidence without interpreting the customer's statement."""
    return DiscoveryEvidence(
        customer_statements=(CustomerStatement("Students keep slipping through the cracks."),),
        verified_facts=(
            VerifiedFact("Inquiries are entered into a shared spreadsheet."),
            VerifiedFact("Confirmed appointments are copied manually into a separate calendar."),
        ),
        assumptions=(
            Assumption("Scheduling is broken."),
            Assumption("Automation is needed."),
        ),
        unknown_information=(UnknownInformation("The frequency and meaning of missed inquiries."),),
    )


def harbor_street_music_discovery_meeting() -> DiscoveryMeeting:
    """Conduct the fixed Chapter 2 scenario using only customer-provided facts."""
    meeting = DiscoveryMeeting(
        title="Harbor Street Music discovery meeting",
        participants=(
            MeetingParticipant("Morgan Lee", "Harbor Street Music manager"),
            MeetingParticipant("Sam Rivera", "Sales Engineer"),
        ),
    )
    for question in DISCOVERY_QUESTION_CATALOG:
        meeting = record_question(meeting, question)

    responses = (
        DiscoveryResponse(
            "process-1",
            "Morgan Lee",
            "Inquiries are recorded in one shared spreadsheet. After confirmation, appointments "
            "are copied into a separate calendar.",
        ),
        DiscoveryResponse("people-1", "Morgan Lee", "Two staff members respond to inquiries."),
        DiscoveryResponse(
            "technology-1",
            "Morgan Lee",
            "One shared spreadsheet and a separate calendar hold the information.",
        ),
        DiscoveryResponse(
            "data-1", "Morgan Lee", "Approximately 30 lesson inquiries arrive per week."
        ),
        DiscoveryResponse("constraints-1", "Morgan Lee", "No documented follow-up process exists."),
        DiscoveryResponse(
            "data-2",
            "Morgan Lee",
            "No. Management is unsure how many inquiries are ultimately lost.",
        ),
    )
    for response in responses:
        meeting = record_response(meeting, response)

    facts = (
        "Approximately 30 lesson inquiries arrive per week.",
        "Two staff members respond to inquiries.",
        "One shared spreadsheet is used for inquiries.",
        "Appointments are copied into a separate calendar after confirmation.",
        "No documented follow-up process exists.",
        "Management is unsure how many inquiries are ultimately lost.",
    )
    for fact in facts:
        meeting = capture_evidence(meeting, EvidenceRecord(fact, "Morgan Lee, discovery meeting"))
    return meeting


def harbor_street_music_business_process() -> BusinessProcess:
    """Return the documented Chapter 3 process, preserving its explicit unknown ending."""
    return BusinessProcess(
        name="Harbor Street Music lesson inquiry process",
        purpose="Record and respond to lesson inquiries through acceptance or decline.",
        actors=(
            ProcessActor("student", "Prospective student"),
            ProcessActor("staff", "Harbor Street Music staff"),
        ),
        steps=(
            ProcessStep("inquiry", "Student submits a lesson inquiry", "student"),
            ProcessStep("spreadsheet", "Inquiry is entered into the shared spreadsheet", "staff"),
            ProcessStep("review", "Staff reviews the shared spreadsheet", "staff"),
            ProcessStep("contact", "Staff contacts the prospective student", "staff"),
            ProcessStep("decision", "Student accepts or declines", "student"),
            ProcessStep("calendar", "Confirmed lesson is copied into a separate calendar", "staff"),
            ProcessStep(
                "declined-unknown",
                "What happens after the student declines is not documented",
                is_unknown=True,
            ),
        ),
        decisions=(DecisionPoint("decision", "Does the student accept the lesson?"),),
        artifacts=(
            InformationArtifact("inquiry-record", "Lesson inquiry", ("inquiry", "spreadsheet")),
            InformationArtifact(
                "shared-spreadsheet", "Shared spreadsheet", ("spreadsheet", "review")
            ),
            InformationArtifact("lesson-calendar", "Separate calendar", ("calendar",)),
        ),
        boundary=ProcessBoundary("inquiry", ("calendar", "declined-unknown")),
        transitions=(
            WorkflowTransition("inquiry", "spreadsheet"),
            WorkflowTransition("spreadsheet", "review"),
            WorkflowTransition("review", "contact"),
            WorkflowTransition("contact", "decision"),
            WorkflowTransition("decision", "calendar", "Accepts"),
            WorkflowTransition("decision", "declined-unknown", "Declines", is_unknown=True),
        ),
    )
