"""Build and deterministically assess the Chapter 17 delivery handoff."""

# ruff: noqa: FBT001, FBT003

from dataclasses import replace

from sales_lab.domain.handoffs import (
    AcceptanceBaselineItem,
    ArchitectureBaseline,
    AutomationReadinessItem,
    ChangeControlBoundary,
    ConditionStatus,
    ConditionType,
    DeliveryPackage,
    DeliveryReadiness,
    DeliveryScopeItem,
    DiscoveryStage,
    Finding,
    HandoffArtifact,
    HandoffType,
    ImplementationHandoff,
    IntegrationReadinessItem,
    LifecycleStatus,
    ReadinessCondition,
    RequirementsBaseline,
    ResponsibilityAssignment,
    ResponsibilityCategory,
    ScopeStatus,
    TechnicalDiscoveryItem,
    UnresolvedDecision,
)
from sales_lab.examples.harbor_street_music import harbor_street_music_requirements
from sales_lab.services.automation import analyze_harbor_street_automation
from sales_lab.services.proposals import build_harbor_street_proposal

OWNER_NOT_ESTABLISHED = "OWNER_NOT_ESTABLISHED"
UNSUPPORTED_COMMITMENT_PHRASES = (
    "in two weeks",
    "unlimited users",
    "all historical data",
    "eliminate scheduling errors",
)


def _condition(
    condition: ConditionType,
    satisfied: bool,
    evidence: str,
    next_action: str,
) -> ReadinessCondition:
    return ReadinessCondition(
        condition,
        ConditionStatus.SATISFIED if satisfied else ConditionStatus.UNSATISFIED,
        evidence,
        not satisfied,
        next_action,
    )


def assess_delivery_readiness(handoff: ImplementationHandoff) -> DeliveryPackage:
    """Assess evidence explicitly; absence never means approval."""
    approved = any(item.status is ScopeStatus.APPROVED for item in handoff.scope_items)
    all_approved = bool(handoff.scope_items) and all(
        item.status is ScopeStatus.APPROVED for item in handoff.scope_items
    )
    essential_areas = {"business process", "technical delivery", "acceptance"}
    assigned = {
        item.area
        for item in handoff.responsibilities
        if item.category is not ResponsibilityCategory.NOT_ESTABLISHED
    }
    owners_assigned = essential_areas <= assigned
    integration_ok = all(
        item.feasibility in {"Established", "Not applicable"}
        for item in handoff.integration_readiness
        if any(
            scope.status is ScopeStatus.APPROVED and scope.identifier in item.scope_ids
            for scope in handoff.scope_items
        )
    )
    conditions = (
        _condition(
            ConditionType.SCOPE_APPROVED,
            all_approved,
            "Explicit scope statuses",
            "Record approval for the delivery boundary.",
        ),
        _condition(
            ConditionType.REQUIREMENTS_BASELINED,
            bool(handoff.requirements_baseline.included_ids),
            handoff.requirements_baseline.identifier,
            "Resolve baseline omissions.",
        ),
        _condition(
            ConditionType.ACCEPTANCE_CRITERIA_DEFINED,
            bool(handoff.acceptance_baseline),
            "Chapter 5 criteria mapped for delivery",
            "Define observable acceptance criteria.",
        ),
        _condition(
            ConditionType.ARCHITECTURE_REVIEWED,
            handoff.architecture_baseline.final,
            f"{handoff.architecture_baseline.candidate_id} remains candidate",
            "Review and authorize the candidate architecture.",
        ),
        _condition(
            ConditionType.DEPENDENCIES_IDENTIFIED,
            bool(handoff.dependencies),
            "Chapter 13 dependencies transferred",
            "Identify delivery dependencies.",
        ),
        _condition(
            ConditionType.OWNERS_ASSIGNED,
            owners_assigned,
            "Role-based responsibility assignments",
            "Assign process, technical-delivery, and acceptance roles.",
        ),
        _condition(
            ConditionType.RISKS_ACKNOWLEDGED,
            bool(handoff.risks),
            "Chapter 13 risks transferred; acknowledgement not recorded",
            "Delivery authority acknowledges relevant risks.",
        ),
        _condition(
            ConditionType.INTEGRATION_FEASIBILITY_ESTABLISHED,
            integration_ok,
            "Integration evidence for approved scope",
            "Verify or defer the calendar mechanism.",
        ),
        _condition(
            ConditionType.CHANGE_CONTROL_DEFINED,
            handoff.change_control.approval_authority != OWNER_NOT_ESTABLISHED,
            "Change-control boundary",
            "Establish change approval authority.",
        ),
        _condition(
            ConditionType.VALIDATION_PLAN_DEFINED,
            all(
                item.validating_role != OWNER_NOT_ESTABLISHED
                for item in handoff.acceptance_baseline
            ),
            "Acceptance baseline",
            "Assign an acceptance-validating role.",
        ),
    )
    baseline_ids = {item.identifier for item in handoff.scope_items}
    unsupported_scope = tuple(
        Finding(
            "UNSUPPORTED-SCOPE", f"Unsupported delivery scope: {item.statement}", (item.identifier,)
        )
        for item in handoff.delivery_items
        if item.identifier not in baseline_ids and not set(item.trace_ids) & baseline_ids
    )
    unsupported_commitments = tuple(
        Finding("UNSUPPORTED-COMMITMENT", f"Unsupported presales commitment: {statement}", ())
        for statement in handoff.commitments
        if any(phrase in statement.casefold() for phrase in UNSUPPORTED_COMMITMENT_PHRASES)
    )
    blockers = [
        Finding(f"BLOCK-{index:03}", item.next_action, ())
        for index, item in enumerate(conditions, 1)
        if item.blocking
    ]
    blockers.extend(unsupported_scope)
    blockers.extend(unsupported_commitments)
    non_blocking = (
        Finding(
            "FOLLOW-001",
            "Refine delivery-document formatting during implementation without changing behavior.",
            (),
        ),
    )
    if not approved:
        readiness = DeliveryReadiness.NOT_READY
    elif blockers:
        readiness = DeliveryReadiness.CONDITIONALLY_READY
    else:
        readiness = DeliveryReadiness.READY
    next_actions = tuple(dict.fromkeys(item.statement for item in blockers)) or (
        "Begin delivery within the approved baseline.",
    )
    return DeliveryPackage(
        handoff,
        readiness,
        conditions,
        tuple(blockers),
        non_blocking,
        unsupported_scope,
        unsupported_commitments,
        next_actions,
    )


def build_harbor_street_handoff() -> ImplementationHandoff:
    """Transfer Chapters 5 and 9-16 without manufacturing approval or ownership."""
    proposal = build_harbor_street_proposal()
    requirement_set = harbor_street_music_requirements()
    acceptance = tuple(
        AcceptanceBaselineItem(
            requirement.identifier,
            f"Given {criterion.given}; when {criterion.when}; then {criterion.then}",
            "Stakeholder-observed scenario",
            OWNER_NOT_ESTABLISHED,
            f"Acceptance record for {criterion.identifier}",
        )
        for requirement in requirement_set.requirements
        for criterion in requirement.acceptance_criteria
    )
    automation = analyze_harbor_street_automation()
    return ImplementationHandoff(
        proposal.engagement,
        HandoffType.IMPLEMENTATION_HANDOFF,
        LifecycleStatus.PROPOSED,
        tuple(
            DeliveryScopeItem(
                item.identifier,
                item.statement,
                ScopeStatus.PROPOSED,
                item.requirement_ids + item.capability_ids + item.evidence_ids,
            )
            for item in proposal.scope
        ),
        proposal.exclusions,
        RequirementsBaseline(
            "HSM-REQ-BASELINE-v1",
            tuple(item.identifier for item in requirement_set.requirements),
            (),
            tuple(item.area for item in requirement_set.unresolved),
            tuple(
                dict.fromkeys(
                    evidence
                    for item in requirement_set.requirements
                    for evidence in item.source_evidence_ids
                )
            ),
        ),
        ArchitectureBaseline(
            "ARCH-001",
            ("Inquiry interface", "Workflow state", "Shared inquiry data"),
            ("Existing spreadsheet", "Existing calendar"),
            ("Inquiry capture", "Confirmed-lesson handoff"),
            ("Spreadsheet access controls", "Calendar interface mechanism"),
        ),
        (
            IntegrationReadinessItem(
                "INT-CALENDAR",
                ("SCOPE-006",),
                "Inquiry workflow",
                "Existing calendar",
                "Confirmed lesson details",
                "Candidate manual handoff or unverified interface",
                "Requires validation",
                "No interface evidence established",
                "Duplicate-safe behavior required",
                "Retain manual handoff and surface failure",
                ("What supported calendar interface, if any, exists?",),
            ),
        ),
        tuple(
            AutomationReadinessItem(
                item.identifier,
                item.automation_mode.value,
                item.human_responsibility.accountable_for,
                item.approval_boundary.approval_result
                if item.approval_boundary
                else "No external-action approval boundary",
                "; ".join(item.required_rules) or "No automated decision rule",
                item.exception_paths[0].result if item.exception_paths else "Manual review",
                "; ".join(item.data_dependencies) or "None established",
                item.readiness.value,
            )
            for item in automation.plan.assessments
        ),
        acceptance,
        (
            UnresolvedDecision(
                "DEC-001",
                "Who owns the inquiry process?",
                ("SCOPE-001", "SCOPE-002"),
                OWNER_NOT_ESTABLISHED,
                "Before implementation",
                "No accountable operating boundary.",
            ),
            UnresolvedDecision(
                "DEC-002",
                "Is calendar integration in the first implementation phase?",
                ("SCOPE-006",),
                OWNER_NOT_ESTABLISHED,
                "Before calendar work",
                "Calendar scope remains blocked or deferred.",
            ),
            UnresolvedDecision(
                "DEC-003",
                "Who approves scope changes?",
                tuple(item.identifier for item in proposal.scope),
                OWNER_NOT_ESTABLISHED,
                "Before delivery baseline",
                "Changes cannot be governed.",
            ),
        ),
        (
            TechnicalDiscoveryItem(
                "TD-001",
                "Verify calendar interface capabilities.",
                DiscoveryStage.PRE_IMPLEMENTATION_DISCOVERY,
                ("SCOPE-006",),
                True,
            ),
            TechnicalDiscoveryItem(
                "TD-002",
                "Confirm spreadsheet access-control options.",
                DiscoveryStage.IMPLEMENTATION_DISCOVERY,
                ("SCOPE-003",),
                False,
            ),
            TechnicalDiscoveryItem(
                "TD-003",
                "Confirm production duplicate-identification behavior.",
                DiscoveryStage.PRE_IMPLEMENTATION_DISCOVERY,
                ("SCOPE-004",),
                True,
            ),
        ),
        tuple(
            ResponsibilityAssignment(
                area, OWNER_NOT_ESTABLISHED, ResponsibilityCategory.NOT_ESTABLISHED
            )
            for area in (
                "business process",
                "product decision",
                "technical delivery",
                "integration",
                "data",
                "acceptance",
                "training",
                "maintenance",
                "support",
            )
        ),
        ChangeControlBoundary(
            "Chapter 16 proposed scope; no approved baseline exists",
            "Wording may be improved without changing required behavior.",
            "New behavior or deliverable without baseline traceability requires review.",
            OWNER_NOT_ESTABLISHED,
            "Update requirement, scope, delivery-work, and acceptance links.",
            "Revise affected criteria and obtain explicit acceptance authority review.",
        ),
        tuple(
            HandoffArtifact(name, chapter, "Available", consumer, limitation)
            for name, chapter, consumer, limitation in (
                (
                    "Discovery Summary",
                    2,
                    "Delivery team",
                    "Evidence remains bounded to recorded discovery.",
                ),
                (
                    "Current-State Process",
                    3,
                    "Process owner",
                    "Current state, not an implementation workflow.",
                ),
                (
                    "Requirements Baseline",
                    5,
                    "Delivery and validation",
                    "Unresolved requirements remain visible.",
                ),
                (
                    "Selected Recommendation",
                    14,
                    "Delivery lead",
                    "Conditional recommendation is not approval.",
                ),
                (
                    "Demonstration Findings",
                    15,
                    "Engineering and validation",
                    "Educational behavior is not production acceptance.",
                ),
                (
                    "Scope and Exclusions",
                    16,
                    "Delivery and decision authority",
                    "Scope is proposed, not approved.",
                ),
            )
        ),
        tuple(f"{item.title}: {item.event}; {item.consequence}" for item in proposal.risks),
        tuple(item.statement for item in proposal.assumptions),
        tuple(item.statement for item in proposal.dependencies),
        tuple(
            f"{item.identifier}: {item.state.value} — {item.description}"
            for item in proposal.demonstration_findings
        ),
    )


def approval_experiment(original: ImplementationHandoff) -> DeliveryPackage:
    """Fictionally approve only the reversible process-validation boundary."""
    approved_ids = {"SCOPE-001", "SCOPE-003", "SCOPE-004", "SCOPE-006"}
    changed = replace(
        original,
        lifecycle_status=LifecycleStatus.APPROVED,
        scope_items=tuple(
            replace(item, status=ScopeStatus.APPROVED) if item.identifier in approved_ids else item
            for item in original.scope_items
        ),
    )
    return assess_delivery_readiness(changed)


def owner_assignment_experiment(original: ImplementationHandoff) -> DeliveryPackage:
    """Assign fictional organizational roles, never named people."""
    roles = {
        "business process": ("Lesson Operations Lead", ResponsibilityCategory.ACCOUNTABLE),
        "technical delivery": ("Delivery Engineer", ResponsibilityCategory.RESPONSIBLE),
        "acceptance": ("Customer Decision Role", ResponsibilityCategory.ACCOUNTABLE),
    }
    changed = replace(
        original,
        responsibilities=tuple(
            replace(item, role=roles[item.area][0], category=roles[item.area][1])
            if item.area in roles
            else item
            for item in original.responsibilities
        ),
        acceptance_baseline=tuple(
            replace(item, validating_role="Customer Decision Role")
            for item in original.acceptance_baseline
        ),
    )
    return assess_delivery_readiness(changed)


def unsupported_scope_experiment(original: ImplementationHandoff) -> DeliveryPackage:
    """Add an untraceable native application while preserving the original."""
    mobile = DeliveryScopeItem(
        "DELIVERY-MOBILE", "Native mobile application", ScopeStatus.UNDER_REVIEW, ()
    )
    return assess_delivery_readiness(replace(original, delivery_items=(mobile,)))


def failed_integration_experiment(original: ImplementationHandoff) -> DeliveryPackage:
    """Establish failure for the calendar mechanism without changing unrelated scope."""
    changed = replace(
        original,
        integration_readiness=tuple(
            replace(
                item,
                feasibility="Not feasible",
                interface_evidence="Test evidence disproves assumed mechanism",
                unresolved_questions=(),
            )
            for item in original.integration_readiness
        ),
        scope_items=tuple(
            replace(item, status=ScopeStatus.DEFERRED) if item.identifier == "SCOPE-006" else item
            for item in original.scope_items
        ),
    )
    return assess_delivery_readiness(changed)
