"""Plan, validate, and execute the deterministic Chapter 15 demonstration."""

# ruff: noqa: C901, E501, FBT003, PERF401, S101

from dataclasses import replace

from sales_lab.domain.decisions import RecommendationCondition
from sales_lab.domain.demonstrations import (
    Condition,
    CoverageRecord,
    DemonstrationAudience,
    DemonstrationExperiment,
    DemonstrationFinding,
    DemonstrationFindingState,
    DemonstrationLimitation,
    DemonstrationObjective,
    DemonstrationPlan,
    DemonstrationReport,
    DemonstrationScenario,
    DemonstrationStep,
    DemonstrationType,
    EvidenceArtifact,
    ObservedResult,
    ProofOfConceptQuestion,
    ProofOfConceptStatus,
)
from sales_lab.domain.requirements import RequirementSet
from sales_lab.domain.stakeholders import StakeholderMap
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_requirements,
    harbor_street_music_stakeholder_map,
)
from sales_lab.services.decisions import harbor_street_decision_package


def validate_demonstration_plan(
    plan: DemonstrationPlan,
    requirements: RequirementSet,
    recommendation_conditions: tuple[RecommendationCondition, ...],
    stakeholders: StakeholderMap,
) -> tuple[str, ...]:
    """Return deterministic guardrail findings rather than endorsing the recommendation."""
    findings: list[str] = []
    vague = {"show the customer the new system", "demonstrate inquiry-status visibility"}
    if plan.objective.statement.strip().casefold().rstrip(".") in vague:
        findings.append(
            "Vague objective: define actors, behavior, evidence, and observable outcome."
        )
    role_ids = {role.identifier for role in stakeholders.roles}
    if not plan.audience or any(item.role_id not in role_ids for item in plan.audience):
        findings.append("Invalid audience: every participant must trace to a Chapter 4 role.")
    if tuple(step.order for step in plan.steps) != tuple(range(1, len(plan.steps) + 1)):
        findings.append("Invalid step order: steps must be contiguous and start at one.")
    if not plan.success_conditions:
        findings.append("Potential demo theatre: no observable success conditions are defined.")
    if not plan.failure_conditions:
        findings.append("Potential demo theatre: no failure conditions are defined.")
    if not plan.limitations:
        findings.append("Potential demo theatre: no limitations are disclosed.")
    known_traces = (
        {item.identifier for item in requirements.requirements}
        | {
            criterion.identifier
            for item in requirements.requirements
            for criterion in item.acceptance_criteria
        }
        | {item.identifier for item in recommendation_conditions}
    )
    if not plan.objective.trace_ids or not set(plan.objective.trace_ids) <= known_traces:
        findings.append("Missing traceability: objective references are absent or unsupported.")
    for step in plan.steps:
        if not step.trace_ids or not set(step.trace_ids) & known_traces:
            findings.append(f"Unsupported demonstration step: {step.identifier}.")
    for claim in plan.claims:
        folded = claim.casefold()
        if "revenue" in folded:
            findings.append(
                "Unsupported demonstration claim: the demonstration does not measure or establish revenue impact."
            )
        if "production ready" in folded or "production-ready" in folded:
            findings.append(
                "Unsupported production-readiness claim: broader operational evidence is required."
            )
    return tuple(findings)


def harbor_street_demonstration_plan() -> DemonstrationPlan:
    """Build the narrow demo from Chapter 5 requirements and Chapter 14 conditions."""
    return DemonstrationPlan(
        "Harbor Street Music lesson inquiry process",
        DemonstrationType.SOLUTION_DEMONSTRATION,
        DemonstrationObjective(
            "Can a standardized existing-tool workflow preserve current inquiry state and avoid duplicate scheduling effects?",
            "Given a fictional active lesson inquiry, when authorized front-desk staff record status and follow-up, then confirm it twice, current state and ordered history are retrievable and only one scheduling handoff is prepared.",
            ("REQ-001", "AC-001", "RC-001", "RC-005"),
            ("EV-STATE", "EV-HISTORY", "EV-HANDOFF"),
        ),
        (
            DemonstrationAudience("staff", "Front Desk Staff", "Validate workflow fit."),
            DemonstrationAudience("manager", "Store Manager", "Evaluate the operational need."),
            DemonstrationAudience(
                "instructor", "Music Instructor", "Inspect the represented handoff."
            ),
        ),
        DemonstrationScenario(
            "INQ-DEMO-001",
            "Fictional learner",
            "Guitar",
            "NEW",
            "Tuesday afternoon",
            "Tuesday 15:00",
            "Fictional instructor",
        ),
        (
            "Inquiry status and follow-up history",
            "Simulated scheduling handoff and duplicate suppression",
        ),
        (
            "Enterprise scalability",
            "Security certification",
            "Regulatory compliance",
            "Production reliability",
            "Real vendor compatibility",
            "Exact financial benefits",
            "Full staff adoption",
            "Long-term maintainability",
        ),
        tuple(
            DemonstrationStep(number, identifier, actor, action, traces)
            for number, identifier, actor, action, traces in (
                (1, "STEP-001", "staff", "Create fictional inquiry", ("REQ-001",)),
                (2, "STEP-002", "staff", "Assign front-desk responsibility", ("RC-002",)),
                (3, "STEP-003", "staff", "Record status NEW", ("REQ-001", "AC-001")),
                (4, "STEP-004", "staff", "Record follow-up interaction", ("REQ-001",)),
                (
                    5,
                    "STEP-005",
                    "staff",
                    "Retrieve current status and ordered history",
                    ("REQ-001", "AC-001"),
                ),
                (6, "STEP-006", "staff", "Confirm lesson with required information", ("REQ-002",)),
                (
                    7,
                    "STEP-007",
                    "staff",
                    "Prepare simulated scheduling handoff",
                    ("REQ-002", "RC-001"),
                ),
                (8, "STEP-008", "staff", "Repeat the logical confirmation", ("RC-005",)),
                (9, "STEP-009", "staff", "Verify one downstream business effect", ("RC-005",)),
            )
        ),
        (
            Condition("SC-001", "Current status is retrievable.", "EV-STATE"),
            Condition("SC-002", "History is preserved in chronological order.", "EV-HISTORY"),
            Condition("SC-003", "One confirmation creates one scheduling handoff.", "EV-HANDOFF"),
            Condition(
                "SC-004", "Repeated confirmation creates no additional effect.", "EV-DUPLICATE"
            ),
        ),
        (
            Condition("FC-001", "Current status cannot be determined.", "EV-STATE"),
            Condition("FC-002", "History is out of order.", "EV-HISTORY"),
            Condition("FC-003", "One logical confirmation creates two effects.", "EV-DUPLICATE"),
            Condition(
                "FC-004", "A result lacks requirement or condition traceability.", "EV-TRACE"
            ),
        ),
        (
            DemonstrationLimitation(
                "LIM-001", "The scheduling boundary is simulated; no calendar interface was called."
            ),
            DemonstrationLimitation(
                "LIM-002",
                "One deterministic run does not prove concurrency, retries, scale, reliability, security, adoption, or production readiness.",
            ),
            DemonstrationLimitation(
                "LIM-003", "No future user feedback or operational pilot evidence was collected."
            ),
        ),
        (),
    )


def _conditions() -> tuple[RecommendationCondition, ...]:
    return harbor_street_decision_package().recommendation.conditions


def execute_harbor_street_demonstration(
    plan: DemonstrationPlan | None = None,
) -> DemonstrationReport:
    """Execute an in-memory state machine with no clock, randomness, or external action."""
    current = plan or harbor_street_demonstration_plan()
    requirements = harbor_street_music_requirements()
    guardrails = validate_demonstration_plan(
        current, requirements, _conditions(), harbor_street_music_stakeholder_map()
    )
    history = ("NEW", "FOLLOW_UP_RECORDED", "CONFIRMED")
    observations = (
        ObservedResult(
            "STEP-005",
            "Status CONFIRMED and history NEW → FOLLOW_UP_RECORDED → CONFIRMED were retrieved.",
            "The educational model preserves current state and ordered history for this scenario.",
            "This does not establish multi-user or production persistence behavior.",
            "EV-STATE",
        ),
        ObservedResult(
            "STEP-007",
            "One simulated scheduling handoff was prepared.",
            "The internal handoff contract accepted complete confirmed-lesson data.",
            "No real calendar or vendor interface was invoked.",
            "EV-HANDOFF",
        ),
        ObservedResult(
            "STEP-008",
            "The second confirmation was recognized as a duplicate; scheduling effects remained one.",
            "Duplicate suppression operates for this deterministic sequential scenario.",
            "Concurrency and external retry behavior remain untested.",
            "EV-DUPLICATE",
        ),
    )
    evidence = (
        EvidenceArtifact(
            "EV-STATE",
            "Structured result",
            f"{current.scenario.inquiry_id}: CONFIRMED",
            ("REQ-001", "AC-001", "STEP-005"),
        ),
        EvidenceArtifact(
            "EV-HISTORY",
            "State transition history",
            " → ".join(history),
            ("REQ-001", "STEP-003", "STEP-004", "STEP-006"),
        ),
        EvidenceArtifact(
            "EV-HANDOFF", "Structured result", "Scheduling handoffs: 1", ("REQ-002", "STEP-007")
        ),
        EvidenceArtifact(
            "EV-DUPLICATE",
            "Validation result",
            "Duplicate recognized; additional effects: 0",
            ("RC-005", "STEP-008", "STEP-009"),
        ),
    )
    findings = (
        DemonstrationFinding(
            "FIND-001",
            DemonstrationFindingState.PASSED,
            "Current state and ordered history were demonstrated.",
            ("EV-STATE", "EV-HISTORY"),
        ),
        DemonstrationFinding(
            "FIND-002",
            DemonstrationFindingState.PASSED,
            "Duplicate suppression passed for the defined scenario.",
            ("EV-DUPLICATE",),
        ),
        DemonstrationFinding(
            "FIND-003",
            DemonstrationFindingState.PARTIALLY_DEMONSTRATED,
            "Schedule visibility was represented only through a simulated handoff.",
            ("EV-HANDOFF",),
        ),
        DemonstrationFinding(
            "FIND-004",
            DemonstrationFindingState.INCONCLUSIVE,
            "Real calendar interface feasibility remains unresolved.",
            (),
        ),
    )
    req_coverage = (
        CoverageRecord("REQ-001", "Demonstrated", "STEP-005", "EV-STATE", "Passed"),
        CoverageRecord(
            "REQ-002", "Simulated handoff only", "STEP-007", "EV-HANDOFF", "Partially Demonstrated"
        ),
        CoverageRecord("REQ-003", "Not a runtime demo condition", "—", "—", "Not Demonstrated"),
    )
    descriptions = {item.identifier: item.description for item in _conditions()}
    condition_coverage: tuple[CoverageRecord, ...] = (
        CoverageRecord(
            "RC-001", "Status and handoff demonstrated", "STEP-007", "EV-HANDOFF", "Passed"
        ),
        CoverageRecord(
            "RC-002",
            "Responsibility represented; ownership not established",
            "STEP-002",
            "EV-STATE",
            "Partially Demonstrated",
        ),
        CoverageRecord(
            "RC-003",
            "Roles represented; real access not verified",
            "STEP-002",
            "EV-STATE",
            "Partially Demonstrated",
        ),
        CoverageRecord("RC-004", "Not measured", "—", "—", "Not Demonstrated"),
        CoverageRecord(
            "RC-005",
            "Duplicate behavior demonstrated; interface planned POC only",
            "STEP-008",
            "EV-DUPLICATE",
            "Partially Demonstrated",
        ),
    )
    # Ensure this view is coupled to Chapter 14 identifiers, not recreated findings.
    condition_coverage = tuple(
        item for item in condition_coverage if item.source_id in descriptions
    )
    poc = (
        ProofOfConceptQuestion(
            "POC-001",
            "Can the existing calendar receive a confirmed lesson through a supported interface without duplicate appointments?",
            "Use a vendor-supported test environment with authorized credentials and repeat one idempotent confirmation.",
            "Interface documentation, authorization, request/response logs, and resulting appointment records.",
            "Exactly one appointment is accepted and retrievable.",
            "The interface is unsupported, unauthorized, or creates duplicate appointments.",
            "Use the handoff manually if feasibility is not established; reassess integration if it is.",
            ProofOfConceptStatus.NOT_EXECUTED,
        ),
    )
    return DemonstrationReport(
        current,
        evidence,
        observations,
        findings,
        req_coverage,
        condition_coverage,
        poc,
        tuple(item for item in guardrails if item.startswith("Unsupported demonstration claim")),
        guardrails,
        False,
    )


def duplicate_confirmation_experiment() -> DemonstrationExperiment:
    """Submit one logical confirmation twice inside the educational model."""
    scenario = harbor_street_demonstration_plan().scenario
    return DemonstrationExperiment(
        "Duplicate confirmation",
        scenario,
        (
            "First input: scheduling handoff created.",
            "Second input: duplicate recognized.",
            "Additional scheduling business effect: none.",
        ),
        1,
        DemonstrationFindingState.PASSED,
    )


def missing_information_experiment() -> DemonstrationExperiment:
    """Reject an incomplete copy without changing the canonical scenario."""
    original = harbor_street_demonstration_plan().scenario
    incomplete = replace(original, selected_time=None)
    observations = (
        "Demonstration step failed validation: selected time is required.",
        "No scheduling handoff created.",
    )
    assert incomplete != original
    return DemonstrationExperiment(
        "Missing required information", original, observations, 0, DemonstrationFindingState.FAILED
    )


def unsupported_claim_experiment() -> DemonstrationReport:
    """Expose a revenue conclusion that the demonstration cannot establish."""
    plan = replace(
        harbor_street_demonstration_plan(),
        claims=("This demonstration proves the solution will increase lesson revenue.",),
    )
    return execute_harbor_street_demonstration(plan)
