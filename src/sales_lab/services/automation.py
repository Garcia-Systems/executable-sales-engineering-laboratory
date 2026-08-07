"""Deterministic Chapter 11 validation, experiments, and simulations."""

# ruff: noqa: EM101, TRY003

from dataclasses import dataclass, replace

from sales_lab.domain.automation import (
    ActivityCharacteristic,
    ApprovalBoundary,
    ApprovalState,
    AutomationAssessment,
    AutomationMode,
    AutomationPlan,
    AutomationReadiness,
    AutomationRiskCategory,
    ExceptionPath,
    HumanResponsibility,
    UnsupportedAutomationProposal,
    WorkflowActivity,
)
from sales_lab.domain.business_process import BusinessProcess
from sales_lab.domain.stakeholders import StakeholderMap
from sales_lab.services.architecture import ArchitectureAnalysis
from sales_lab.services.integrations import IntegrationAnalysis


@dataclass(frozen=True, slots=True)
class AutomationFinding:
    """One stable validation finding."""

    assessment_id: str
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class AutomationAnalysis:
    """Validated plan with the actual prior-chapter objects used as evidence."""

    plan: AutomationPlan
    process: BusinessProcess
    stakeholders: StakeholderMap
    architecture_analysis: ArchitectureAnalysis
    integration_analysis: IntegrationAnalysis
    findings: tuple[AutomationFinding, ...]


@dataclass(frozen=True, slots=True)
class ReminderState:
    """Explicit reminder inputs; no clock or random state is consulted."""

    inquiry_active: bool
    threshold_condition_satisfied: bool
    reminder_created: bool = False


@dataclass(frozen=True, slots=True)
class ApprovalResult:
    """A simulation outcome that cannot itself perform external action."""

    state: ApprovalState
    eligible_to_continue: bool
    external_action_performed: bool = False


@dataclass(frozen=True, slots=True)
class ExceptionRoutingResult:
    """A scheduling result exposing whether automatic completion stopped."""

    automatically_completed: bool
    human_review_created: bool
    review_owner_role_id: str | None


def harbor_street_automation_plan() -> AutomationPlan:
    """Return authored candidate modes without optimizing automation."""
    staff = HumanResponsibility(
        "staff", "Inquiry context and prepared work", "Customer communication", "Work remains open"
    )
    manager = HumanResponsibility(
        "manager", "Undefined closure conditions", "Closure authority", "Inquiry remains open"
    )
    return AutomationPlan(
        "Harbor Street Music lesson inquiry process",
        (
            AutomationAssessment(
                "AUT-001",
                WorkflowActivity(
                    "reminder", "Create follow-up reminder", ("review",), ("FLOW-003",)
                ),
                (
                    ActivityCharacteristic.REPETITIVE,
                    ActivityCharacteristic.RULE_BASED,
                    ActivityCharacteristic.DATA_DEPENDENT,
                    ActivityCharacteristic.REVERSIBLE,
                ),
                AutomationMode.RULE_BASED_AUTOMATION,
                AutomationReadiness.REQUIRES_RULE_DEFINITION,
                "Evaluate explicit inquiry state and create at most one internal reminder.",
                staff,
                ("E2",),
                ("REQ-001",),
                ("CAP-001", "CAP-003"),
                ("ARCH-001", "FLOW-003"),
                ("Active inquiry plus elapsed-time threshold creates one reminder.",),
                ("Elapsed-time threshold is not established.",),
                ("Recorded inquiry status", "Recorded last-contact state"),
                None,
                (),
                (AutomationRiskCategory.DUPLICATE_ACTION, AutomationRiskCategory.POOR_DATA_QUALITY),
                ("What elapsed time should trigger a reminder?",),
            ),
            AutomationAssessment(
                "AUT-002",
                WorkflowActivity("contact", "Initial customer contact", ("contact",)),
                (
                    ActivityCharacteristic.REQUIRES_EMPATHY,
                    ActivityCharacteristic.SENSITIVE,
                    ActivityCharacteristic.HIGH_VARIATION,
                ),
                AutomationMode.ASSISTED,
                AutomationReadiness.READY_FOR_DESIGN,
                "Present the recorded inquiry information; do not generate or send a message.",
                staff,
                ("E1", "E2"),
                ("REQ-001",),
                ("CAP-001",),
                ("ARCH-001", "FLOW-003"),
                (),
                (),
                ("Lesson inquiry record",),
                None,
                (),
                (AutomationRiskCategory.LOSS_OF_HUMAN_CONTEXT,),
                ("What information should staff see before contact?",),
            ),
            AutomationAssessment(
                "AUT-003",
                WorkflowActivity(
                    "confirmation",
                    "Prepare lesson confirmation",
                    ("decision", "calendar"),
                    ("FLOW-004",),
                ),
                (
                    ActivityCharacteristic.REQUIRES_APPROVAL,
                    ActivityCharacteristic.SENSITIVE,
                    ActivityCharacteristic.DATA_DEPENDENT,
                ),
                AutomationMode.HUMAN_APPROVAL_REQUIRED,
                AutomationReadiness.REQUIRES_AUTHORITY_CLARIFICATION,
                "Prepare a draft and wait; never send it.",
                staff,
                ("E2",),
                ("REQ-002",),
                ("CAP-002",),
                ("ARCH-001", "FLOW-004"),
                (),
                ("Who may approve a lesson confirmation?",),
                ("Confirmed lesson details",),
                ApprovalBoundary(
                    "staff",
                    ApprovalState.AWAITING_APPROVAL,
                    "Eligible for external action",
                    "No external action",
                ),
                (),
                (AutomationRiskCategory.UNAUTHORIZED_ACTION,),
                ("Is front desk approval authority established?",),
            ),
            AutomationAssessment(
                "AUT-004",
                WorkflowActivity("calendar", "Create calendar entry", ("calendar",), ("FLOW-004",)),
                (
                    ActivityCharacteristic.REPETITIVE,
                    ActivityCharacteristic.RULE_BASED,
                    ActivityCharacteristic.EXCEPTION_PRONE,
                    ActivityCharacteristic.DATA_DEPENDENT,
                ),
                AutomationMode.RULE_BASED_AUTOMATION,
                AutomationReadiness.REQUIRES_DATA_VALIDATION,
                "Create one internal candidate entry only after confirmation and conflict checks.",
                staff,
                ("E2", "E4"),
                ("REQ-002",),
                ("CAP-002",),
                ("ARCH-001", "FLOW-004"),
                ("Only a complete, confirmed, non-duplicate lesson is eligible.",),
                ("Duplicate handling and confirmation completeness are not established.",),
                ("Confirmation state", "Complete schedule", "Calendar interface feasibility"),
                None,
                (
                    ExceptionPath(
                        "Known instructor schedule conflict",
                        "Stop and create human review",
                        "staff",
                    ),
                ),
                (
                    AutomationRiskCategory.DUPLICATE_ACTION,
                    AutomationRiskCategory.MISSED_EXCEPTION,
                    AutomationRiskCategory.INCORRECT_ACTION,
                ),
                ("How is a duplicate identified?",),
            ),
            AutomationAssessment(
                "AUT-005",
                WorkflowActivity(
                    "conflict", "Resolve schedule conflict", ("calendar",), ("FLOW-004",)
                ),
                (
                    ActivityCharacteristic.REQUIRES_JUDGMENT,
                    ActivityCharacteristic.HIGH_VARIATION,
                    ActivityCharacteristic.EXCEPTION_PRONE,
                ),
                AutomationMode.HUMAN_DECISION_REQUIRED,
                AutomationReadiness.REQUIRES_AUTHORITY_CLARIFICATION,
                "Identify and present a possible conflict.",
                staff,
                ("E4",),
                ("REQ-002",),
                ("CAP-002",),
                ("ARCH-001", "FLOW-004"),
                (),
                ("Conflict-resolution authority and deterministic rules are not established.",),
                ("Instructor availability",),
                None,
                (ExceptionPath("Requested time conflicts", "Route to human review", "staff"),),
                (
                    AutomationRiskCategory.MISSED_EXCEPTION,
                    AutomationRiskCategory.UNCLEAR_ACCOUNTABILITY,
                ),
                ("Who may change the requested time?",),
            ),
            AutomationAssessment(
                "AUT-006",
                WorkflowActivity(
                    "decline", "Escalate or close a declined inquiry", ("declined-unknown",)
                ),
                (ActivityCharacteristic.REQUIRES_JUDGMENT,),
                AutomationMode.NOT_EVALUATED,
                AutomationReadiness.NOT_READY,
                "No system action.",
                manager,
                ("E1",),
                (),
                (),
                (),
                (),
                ("Escalation, closure rule, and receiving authority are undefined.",),
                (),
                None,
                (),
                (
                    AutomationRiskCategory.UNAUTHORIZED_ACTION,
                    AutomationRiskCategory.UNCLEAR_ACCOUNTABILITY,
                ),
                ("What does escalation mean and who receives it?",),
            ),
        ),
        (
            UnsupportedAutomationProposal(
                "Automatically reject inquiries that appear unlikely to convert.",
                None,
                None,
                None,
                ranks_people=True,
            ),
        ),
    )


def validate_automation_plan(  # noqa: C901 - explicit guardrails aid learner stepping.
    plan: AutomationPlan,
    process: BusinessProcess,
    stakeholders: StakeholderMap,
    architecture_analysis: ArchitectureAnalysis,
    integration_analysis: IntegrationAnalysis,
) -> AutomationAnalysis:
    """Validate supplied assessments without selecting or changing their modes."""
    findings: list[AutomationFinding] = []
    step_ids = {item.identifier for item in process.steps}
    role_ids = {item.identifier for item in stakeholders.roles}
    for assessment in plan.assessments:
        if not assessment.evidence_ids or not assessment.requirement_ids:
            findings.append(
                AutomationFinding(
                    assessment.identifier,
                    "Missing traceability",
                    "Supporting evidence or requirement is absent.",
                )
            )
        if not set(assessment.activity.process_step_ids) <= step_ids:
            findings.append(
                AutomationFinding(
                    assessment.identifier,
                    "Unknown process activity",
                    "A referenced current-process step does not exist.",
                )
            )
        if assessment.human_responsibility.role_id not in role_ids:
            findings.append(
                AutomationFinding(
                    assessment.identifier,
                    "Unknown accountable role",
                    assessment.human_responsibility.role_id,
                )
            )
        if assessment.unresolved_rules:
            findings.append(
                AutomationFinding(
                    assessment.identifier,
                    "NOT_READY_FOR_AUTOMATION",
                    "; ".join(assessment.unresolved_rules),
                )
            )
        if (
            assessment.approval_boundary
            and assessment.approval_boundary.approver_role_id not in role_ids
        ):
            findings.append(
                AutomationFinding(
                    assessment.identifier,
                    "Unknown approver",
                    assessment.approval_boundary.approver_role_id,
                )
            )
    for number, proposal in enumerate(plan.unsupported_proposals, start=1):
        reasons = []
        if proposal.supporting_requirement_id is None:
            reasons.append("no supporting requirement")
        if proposal.decision_rule is None:
            reasons.append("no established decision rule")
        if proposal.accountable_role_id is None:
            reasons.append("unclear accountability")
        if proposal.ranks_people:
            reasons.append("inappropriate ranking of people")
        if reasons:
            findings.append(
                AutomationFinding(
                    f"UNSUPPORTED-{number:03}",
                    "Unsupported automation proposal",
                    ", ".join(reasons),
                )
            )
    return AutomationAnalysis(
        plan, process, stakeholders, architecture_analysis, integration_analysis, tuple(findings)
    )


def simulate_reminder(state: ReminderState) -> ReminderState:
    """Create a reminder exactly once when explicit scenario conditions are satisfied."""
    if state.inquiry_active and state.threshold_condition_satisfied and not state.reminder_created:
        return replace(state, reminder_created=True)
    return state


def simulate_approval(decision: ApprovalState) -> ApprovalResult:
    """Demonstrate approval and rejection without performing an external action."""
    if decision not in (ApprovalState.APPROVED, ApprovalState.REJECTED, ApprovalState.CANCELLED):
        raise ValueError("a terminal staff decision is required")
    return ApprovalResult(decision, decision is ApprovalState.APPROVED)


def simulate_exception_routing(*, known_conflict: bool) -> ExceptionRoutingResult:
    """Stop automatic completion and route a known scheduling conflict."""
    if known_conflict:
        return ExceptionRoutingResult(
            automatically_completed=False,
            human_review_created=True,
            review_owner_role_id="staff",
        )
    return ExceptionRoutingResult(
        automatically_completed=True,
        human_review_created=False,
        review_owner_role_id=None,
    )


def excessive_automation_experiment(plan: AutomationPlan) -> AutomationPlan:
    """Return a new unsupported closure proposal, leaving the source plan unchanged."""
    proposal = UnsupportedAutomationProposal(
        "Automatically close any inquiry without a response after a fixed period.", None, None, None
    )
    return replace(plan, unsupported_proposals=(*plan.unsupported_proposals, proposal))


def new_rule_evidence_experiment(plan: AutomationPlan) -> AutomationPlan:
    """Supply fictional rule evidence and authority; implementability is not desirability."""
    proposal = UnsupportedAutomationProposal(
        "Fictional experiment: close after explicit scenario period and manager approval.",
        "REQ-FICTIONAL-CLOSE",
        "Explicit period elapsed AND manager approved",
        "manager",
    )
    return replace(plan, unsupported_proposals=(*plan.unsupported_proposals, proposal))


def analyze_harbor_street_automation() -> AutomationAnalysis:
    """Build the complete evidence chain using the canonical prior-chapter objects."""
    from sales_lab.examples.harbor_street_music import (  # noqa: PLC0415
        harbor_street_music_architectures,
        harbor_street_music_business_process,
        harbor_street_music_capability_map,
        harbor_street_music_current_capability_inventory,
        harbor_street_music_requirements,
        harbor_street_music_solution_options,
        harbor_street_music_stakeholder_map,
    )
    from sales_lab.services.approaches import analyze_solution_approaches  # noqa: PLC0415
    from sales_lab.services.architecture import analyze_architectures  # noqa: PLC0415
    from sales_lab.services.capabilities import analyze_capabilities  # noqa: PLC0415
    from sales_lab.services.gaps import analyze_gaps  # noqa: PLC0415
    from sales_lab.services.integrations import (  # noqa: PLC0415
        analyze_integrations,
        harbor_street_integration_strategies,
        integration_questions,
    )

    stakeholders = harbor_street_music_stakeholder_map()
    capabilities = analyze_capabilities(
        harbor_street_music_requirements(), stakeholders, harbor_street_music_capability_map()
    )
    gaps = analyze_gaps(capabilities, harbor_street_music_current_capability_inventory())
    approaches = analyze_solution_approaches(gaps, harbor_street_music_solution_options())
    architecture = analyze_architectures(approaches, harbor_street_music_architectures())
    integrations = analyze_integrations(
        architecture, harbor_street_integration_strategies(), integration_questions()
    )
    return validate_automation_plan(
        harbor_street_automation_plan(),
        harbor_street_music_business_process(),
        stakeholders,
        architecture,
        integrations,
    )
