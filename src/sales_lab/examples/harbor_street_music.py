"""Reusable Chapter 0 customer-supplied facts."""

from sales_lab.domain.approaches import (
    ApproachAssumption,
    ApproachTradeoff,
    FeasibilityState,
    QualitativeState,
    SolutionApproach,
    SolutionApproachType,
    SolutionOptionSet,
    TradeoffDimension,
)
from sales_lab.domain.business_process import (
    BusinessProcess,
    DecisionPoint,
    InformationArtifact,
    ProcessActor,
    ProcessBoundary,
    ProcessStep,
    WorkflowTransition,
)
from sales_lab.domain.capabilities import (
    Capability,
    CapabilityCategory,
    CapabilityMap,
    CapabilityRequirementLink,
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
from sales_lab.domain.gaps import (
    CapabilityAssessment,
    CapabilityState,
    CurrentCapabilityInventory,
    CurrentResource,
    EvidenceReference,
    GapType,
)
from sales_lab.domain.requirements import (
    AcceptanceCriterion,
    Requirement,
    RequirementSet,
    RequirementStatus,
    RequirementType,
    UnresolvedRequirement,
)
from sales_lab.domain.stakeholders import (
    AuthorityState,
    DecisionAuthority,
    PerspectiveGap,
    ProcessParticipation,
    ResponsibilityCategory,
    StakeholderEvidence,
    StakeholderMap,
    StakeholderRelationship,
    StakeholderResponsibility,
    StakeholderRole,
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


def harbor_street_music_stakeholder_map() -> StakeholderMap:
    """Return Chapter 4 assertions, each bounded by established evidence or a gap."""
    roles = (
        StakeholderRole("student", "Prospective Student or Parent"),
        StakeholderRole("staff", "Front Desk Staff"),
        StakeholderRole("manager", "Store Manager"),
        StakeholderRole("instructor", "Music Instructor"),
        StakeholderRole("technology-unknown", "Technology Ownership: Unknown"),
    )
    evidence = (
        StakeholderEvidence(
            "E1",
            "Prospective students or parents submit lesson inquiries and may accept or decline.",
            "Chapter 3 process steps inquiry and decision",
        ),
        StakeholderEvidence(
            "E2",
            "Front desk staff enter inquiries, contact prospective students, and copy confirmed "
            "lessons into the calendar.",
            "Harbor Street Music discovery meeting and Chapter 3 process",
        ),
        StakeholderEvidence(
            "E3",
            "The store manager oversees the lesson program and discusses process changes.",
            "Store manager discovery statement",
        ),
        StakeholderEvidence(
            "E4",
            "Music instructors teach scheduled lessons and depend on accurate schedule "
            "information.",
            "Lesson-operation discovery note",
        ),
        StakeholderEvidence(
            "E5",
            "Ownership of spreadsheet, calendar, devices, and accounts was not established.",
            "Discovery evidence gap",
        ),
        StakeholderEvidence(
            "E6", "Final spending authority was not established.", "Discovery evidence gap"
        ),
        StakeholderEvidence(
            "E7",
            "The organization has not yet approved a software budget.",
            "Chapter 0 customer situation known constraint",
        ),
    )
    return StakeholderMap(
        "Harbor Street Music lesson inquiry process",
        roles,
        (
            StakeholderResponsibility("student", ResponsibilityCategory.PROVIDES_INFORMATION, "E1"),
            StakeholderResponsibility("student", ResponsibilityCategory.RECEIVES_OUTPUT, "E1"),
            StakeholderResponsibility("student", ResponsibilityCategory.AFFECTED_BY_CHANGE, "E1"),
            StakeholderResponsibility("staff", ResponsibilityCategory.PERFORMS_WORK, "E2"),
            StakeholderResponsibility("staff", ResponsibilityCategory.USES_SYSTEM, "E2"),
            StakeholderResponsibility("staff", ResponsibilityCategory.AFFECTED_BY_CHANGE, "E2"),
            StakeholderResponsibility("manager", ResponsibilityCategory.OWNS_OUTCOME, "E3"),
            StakeholderResponsibility("manager", ResponsibilityCategory.AFFECTED_BY_CHANGE, "E3"),
            StakeholderResponsibility("instructor", ResponsibilityCategory.PERFORMS_WORK, "E4"),
            StakeholderResponsibility("instructor", ResponsibilityCategory.RECEIVES_OUTPUT, "E4"),
            StakeholderResponsibility(
                "instructor", ResponsibilityCategory.AFFECTED_BY_CHANGE, "E4"
            ),
        ),
        (
            ProcessParticipation("student", "inquiry", "E1"),
            ProcessParticipation("student", "decision", "E1"),
            ProcessParticipation("staff", "spreadsheet", "E2"),
            ProcessParticipation("staff", "review", "E2"),
            ProcessParticipation("staff", "contact", "E2"),
            ProcessParticipation("staff", "calendar", "E2"),
        ),
        (
            DecisionAuthority(
                "manager", "Approve technology spending", AuthorityState.UNKNOWN, "E6"
            ),
        ),
        (
            StakeholderRelationship(
                "student", "staff", "Submits inquiry and receives follow-up", "E1"
            ),
            StakeholderRelationship(
                "staff", "manager", "Maintains lesson-inquiry information", "E2"
            ),
            StakeholderRelationship(
                "staff", "instructor", "Creates confirmed calendar entry", "E4"
            ),
            StakeholderRelationship(
                "manager",
                "technology-unknown",
                "Technology responsibility not established",
                "E5",
                is_unknown=True,
            ),
        ),
        evidence,
        (
            PerspectiveGap(
                "technology-owner",
                "Technology ownership has not been established.",
                "Who maintains the spreadsheet and calendar accounts?",
            ),
            PerspectiveGap(
                "spending-authority",
                "Final spending authority has not been established.",
                "Who has final authority to approve technology spending?",
            ),
            PerspectiveGap(
                "instructor-follow-up",
                "Instructor involvement in inquiry follow-up has not been established.",
                "Do instructors participate in prospective-student follow-up?",
            ),
            PerspectiveGap(
                "success-owner",
                "Who defines lesson-inquiry process success has not been established.",
                "Who defines whether the lesson inquiry process is successful?",
            ),
            PerspectiveGap(
                "scheduling-participants",
                "Additional scheduling participants have not been investigated.",
                "Are any additional employees involved in scheduling?",
            ),
            PerspectiveGap(
                "calendar-errors",
                "Responsibility for incorrect calendar information has not been established.",
                "Who handles problems when calendar information is incorrect?",
            ),
        ),
    )


def harbor_street_music_requirements() -> RequirementSet:
    """Return only requirements deliberately authored from established earlier evidence."""
    return RequirementSet(
        engagement="Harbor Street Music lesson inquiry process",
        requirements=(
            Requirement(
                "REQ-001",
                (
                    "Authorized staff must be able to determine the current status of "
                    "an active lesson inquiry."
                ),
                RequirementType.FUNCTIONAL,
                "staff",
                ("E2",),
                (
                    AcceptanceCriterion(
                        "AC-001",
                        "an active inquiry has a recorded status",
                        "an authorized staff member views that inquiry",
                        "the recorded status is available",
                    ),
                ),
            ),
            Requirement(
                "REQ-002",
                "Music instructors must be able to access confirmed lesson schedule information.",
                RequirementType.FUNCTIONAL,
                "instructor",
                ("E4",),
                (
                    AcceptanceCriterion(
                        "AC-002",
                        "a lesson is confirmed and its schedule information is recorded",
                        "the music instructor accesses the confirmed lesson schedule",
                        "the recorded schedule information is available",
                    ),
                ),
            ),
            Requirement(
                "REQ-003",
                (
                    "The organization must operate within the constraint that no software "
                    "budget has yet been approved."
                ),
                RequirementType.CONSTRAINT,
                "manager",
                ("E7",),
                (
                    AcceptanceCriterion(
                        "AC-003",
                        "a solution option requires software spending",
                        "the option is evaluated",
                        (
                            "the absence of an approved budget is recorded as a constraint "
                            "rather than a zero-dollar budget"
                        ),
                    ),
                ),
            ),
        ),
        unresolved=tuple(
            UnresolvedRequirement(area, RequirementStatus.UNKNOWN)
            for area in ("Authentication", "Retention", "Availability", "Integration")
        ),
    )


def harbor_street_music_capability_map() -> CapabilityMap:
    """Map the exact Chapter 5 requirement identifiers to explicit neutral capabilities."""
    return CapabilityMap(
        engagement=harbor_street_music_requirements().engagement,
        capabilities=(
            Capability(
                "CAP-001",
                "Inquiry Status Tracking",
                "Maintain shared visibility of an active lesson inquiry's current status.",
                CapabilityCategory.INFORMATION,
            ),
            Capability(
                "CAP-002",
                "Confirmed Lesson Schedule Visibility",
                "Make recorded confirmed lesson schedule information visible to instructors.",
                CapabilityCategory.INFORMATION,
            ),
            Capability(
                "CAP-003",
                "Inquiry Information Sharing",
                "Share relevant inquiry and confirmed-lesson information across authorized roles.",
                CapabilityCategory.COLLABORATION,
            ),
            Capability(
                "CAP-004",
                "Constraint-Aware Option Evaluation",
                "Evaluate future options while preserving the unapproved-budget constraint.",
                CapabilityCategory.CONTROL,
            ),
        ),
        links=(
            CapabilityRequirementLink("CAP-001", "REQ-001"),
            CapabilityRequirementLink("CAP-003", "REQ-001"),
            CapabilityRequirementLink("CAP-002", "REQ-002"),
            CapabilityRequirementLink("CAP-003", "REQ-002"),
            CapabilityRequirementLink("CAP-004", "REQ-003"),
        ),
        open_questions=(
            "Do the explicitly unresolved authentication, retention, availability, or integration "
            "areas justify future capabilities?",
            "What existing organizational capabilities already satisfy any part of these "
            "requirements?",
        ),
    )


def harbor_street_music_current_capability_inventory() -> CurrentCapabilityInventory:
    """Return Chapter 7 resources and assessments bounded by established evidence."""
    stakeholder_evidence = {
        item.identifier: item for item in harbor_street_music_stakeholder_map().evidence
    }
    evidence = tuple(
        EvidenceReference(item.identifier, item.statement, item.source)
        for item in (
            stakeholder_evidence["E2"],
            stakeholder_evidence["E4"],
            stakeholder_evidence["E7"],
        )
    )

    return CurrentCapabilityInventory(
        harbor_street_music_capability_map().engagement,
        (
            CurrentResource(
                "RES-001",
                "Shared Lesson Inquiry Spreadsheet",
                "The shared spreadsheet currently holds lesson inquiries.",
                ("E2",),
                "Does the spreadsheet contain a defined inquiry-status field used consistently?",
            ),
            CurrentResource(
                "RES-002",
                "Separate Lesson Calendar",
                "Staff copy confirmed lessons into a separate calendar.",
                ("E2",),
                "Can music instructors view the confirmed lesson calendar, and who can edit it?",
            ),
            CurrentResource(
                "RES-003",
                "Manual Staff Follow-Up Process",
                "Front desk staff contact prospective students using the current process.",
                ("E2",),
                "Does the current process retain who followed up and the follow-up history?",
            ),
            CurrentResource(
                "RES-004",
                "Established Budget-Constraint Knowledge",
                "The unapproved software budget is an explicitly recorded constraint.",
                ("E7",),
            ),
        ),
        evidence,
        (
            CapabilityAssessment(
                "CAP-001",
                ("RES-001", "RES-003"),
                CapabilityState.PARTIALLY_AVAILABLE,
                ("E2",),
                (
                    "Inquiries and staff follow-up exist, but current-status tracking is not "
                    "established."
                ),
                "Evidence does not establish a consistently maintained inquiry-status field.",
                GapType.INFORMATION_GAP,
                "Does the spreadsheet contain a defined inquiry-status field used consistently?",
            ),
            CapabilityAssessment(
                "CAP-002",
                ("RES-002",),
                CapabilityState.UNKNOWN,
                ("E2", "E4"),
                "A calendar exists, but instructor access has not been established.",
                "Discovery does not establish whether instructors can access the calendar.",
                GapType.EVIDENCE_GAP,
                "Can music instructors view the confirmed lesson calendar?",
            ),
            CapabilityAssessment(
                "CAP-003",
                ("RES-001", "RES-002", "RES-003"),
                CapabilityState.PARTIALLY_AVAILABLE,
                ("E2", "E4"),
                "Staff share inquiry artifacts, but sharing across all required roles is unproven.",
                "The consistency and reach of information sharing have not been established.",
                GapType.PROCESS_GAP,
                "Can staff and instructors determine who last contacted a prospective student?",
            ),
            CapabilityAssessment(
                "CAP-004",
                ("RES-004",),
                CapabilityState.AVAILABLE,
                ("E7",),
                "The current record explicitly preserves the unapproved-budget constraint.",
            ),
        ),
    )


def harbor_street_music_solution_options() -> SolutionOptionSet:
    """Return vendor-neutral alternatives linked to the actual Chapter 7 gaps."""
    validation = FeasibilityState.REQUIRES_VALIDATION

    def approach(  # noqa: PLR0913
        identifier: str,
        name: str,
        approach_type: SolutionApproachType,
        description: str,
        assumption: str,
        evidence_need: str,
        feasibility: FeasibilityState,
        existing: str,
        new: str,
        custom: str,
        effort: QualitativeState,
    ) -> SolutionApproach:
        return SolutionApproach(
            identifier,
            name,
            approach_type,
            description,
            ("CAP-001",),
            (ApproachAssumption(assumption, "Not yet established", validation),),
            ("REQ-003",),
            (evidence_need,),
            feasibility,
            (
                ApproachTradeoff(
                    TradeoffDimension.IMPLEMENTATION_EFFORT,
                    effort,
                    "Qualitative teaching assumption; validate through future analysis.",
                ),
            ),
            existing,
            new,
            custom,
        )

    return SolutionOptionSet(
        harbor_street_music_capability_map().engagement,
        (
            approach(
                "APP-001",
                "Standardize Manual Follow-Up",
                SolutionApproachType.PROCESS_CHANGE,
                "Define a consistent status and follow-up process using current resources.",
                "Staff can consistently follow an agreed workflow.",
                "Workflow observation and staff validation",
                validation,
                "Yes",
                "No",
                "No",
                QualitativeState.MODERATE,
            ),
            approach(
                "APP-002",
                "Configure the Existing Spreadsheet",
                SolutionApproachType.CONFIGURE_EXISTING,
                "Represent inquiry status consistently in the current spreadsheet.",
                "The spreadsheet supports controlled shared editing and a usable status field.",
                "Spreadsheet capability and usage evidence",
                validation,
                "Yes",
                "No",
                "No",
                QualitativeState.UNKNOWN,
            ),
            approach(
                "APP-003",
                "Investigate Existing-Tool Integration",
                SolutionApproachType.INTEGRATE_EXISTING,
                (
                    "Explore exchange of inquiry and confirmed-appointment information; "
                    "technical feasibility is not yet established."
                ),
                "The current spreadsheet and calendar expose compatible integration mechanisms.",
                "Technical interface, access, authentication, and data-flow evidence",
                validation,
                "Yes",
                "No",
                "Maybe",
                QualitativeState.UNKNOWN,
            ),
            approach(
                "APP-004",
                "Evaluate Commercial Software",
                SolutionApproachType.BUY,
                "Evaluate a vendor-neutral commercial system that could provide the capability.",
                "A suitable product exists and procurement could become possible.",
                "Budget approval, product research, and user validation",
                FeasibilityState.NOT_EVALUATED,
                "Maybe",
                "Yes",
                "No",
                QualitativeState.NOT_EVALUATED,
            ),
            approach(
                "APP-005",
                "Develop a Custom Workflow",
                SolutionApproachType.BUILD,
                (
                    "Explore custom software implementing status tracking without assuming it "
                    "is desirable."
                ),
                "Custom development skills and maintenance capacity could be available.",
                "Technical, delivery, maintenance, and cost analysis",
                FeasibilityState.NOT_EVALUATED,
                "Maybe",
                "No",
                "Yes",
                QualitativeState.NOT_EVALUATED,
            ),
            approach(
                "APP-006",
                "Combine Process and Technology Changes",
                SolutionApproachType.HYBRID,
                (
                    "Combine validated process, configuration, integration, purchase, or "
                    "development elements."
                ),
                "Compatible elements can be combined without introducing unacceptable complexity.",
                "Evidence for each included element and their interactions",
                FeasibilityState.NOT_EVALUATED,
                "Yes",
                "Maybe",
                "Maybe",
                QualitativeState.NOT_EVALUATED,
            ),
            approach(
                "APP-007",
                "Continue the Current Process",
                SolutionApproachType.STATUS_QUO,
                (
                    "Retain the current process as a comparison baseline rather than assuming "
                    "intervention is justified."
                ),
                "The consequences of leaving the gap unchanged can be investigated.",
                "Baseline consequences and workflow evidence",
                validation,
                "Yes",
                "No",
                "No",
                QualitativeState.LOW,
            ),
        ),
        (
            "Which current-tool functions and access controls are available?",
            "What consequences follow if inquiry-status tracking remains unchanged?",
            "Who can approve spending if a future option requires it?",
        ),
    )
