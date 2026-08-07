"""Build and validate the evidence-linked Chapter 16 proposal."""

# ruff: noqa: C901, E501, PERF401, PLR0912, RUF005

from dataclasses import replace

from sales_lab.domain.proposals import (
    CommercialPlaceholder,
    CommercialStatus,
    DecisionRequest,
    ExecutiveSummary,
    NextStep,
    ProposalExperiment,
    ProposalLifecycle,
    ProposalPackage,
    ProposalType,
    ProposedDeliverable,
    ScopeItem,
    ValueSummary,
)
from sales_lab.services.decisions import harbor_street_decision_package
from sales_lab.services.demonstrations import execute_harbor_street_demonstration
from sales_lab.services.risks import analyze_harbor_street_risks
from sales_lab.services.value import analyze_harbor_street_value

OVERSTATEMENTS = (
    "guaranteed",
    "transformative",
    "risk-free",
    "best-in-class",
    "will increase revenue",
    "will eliminate",
    "fully secure",
    "production ready",
    "production-ready",
)


def persuasion_findings(statements: tuple[str, ...]) -> tuple[str, ...]:
    """Flag deterministic overstatement phrases; never silently rewrite prose."""
    return tuple(
        f"Unsupported outcome promise requires review: {statement}"
        for statement in statements
        if any(phrase in statement.casefold() for phrase in OVERSTATEMENTS)
    )


def validate_proposal(proposal: ProposalPackage) -> tuple[str, ...]:
    """Return stable consistency findings without granting customer approval."""
    findings: list[str] = []
    if not proposal.recommendation.statement.strip():
        findings.append("Proposal has no recommendation.")
    if not proposal.recommendation.evidence_ids:
        findings.append("Proposal has no evidence.")
    for scope_item in proposal.scope:
        if (
            not (scope_item.requirement_ids or scope_item.recommendation_finding_ids)
            or not scope_item.evidence_ids
        ):
            findings.append(f"Scope item without traceability: {scope_item.identifier}.")
    scope_ids = {item.identifier for item in proposal.scope}
    for deliverable in proposal.deliverables:
        if not deliverable.scope_ids or not set(deliverable.scope_ids) <= scope_ids:
            findings.append(f"Deliverable outside scope: {deliverable.identifier}.")
    if not proposal.exclusions:
        findings.append("Missing exclusions.")
    findings.extend(
        persuasion_findings(
            (
                proposal.executive_summary.problem,
                proposal.executive_summary.recommended_direction,
                proposal.decision_request.statement,
            )
        )
    )
    for commercial in proposal.commercial_placeholders:
        if commercial.status is CommercialStatus.NOT_ESTABLISHED and commercial.value is not None:
            findings.append(f"Invented commercial information: {commercial.label}.")
    if proposal.recommendation.approved:
        findings.append("Implementation approval implied without customer authority.")
    if not set(proposal.decision_request.scope_ids) <= scope_ids:
        findings.append("Decision request is inconsistent with scope.")
    request = proposal.decision_request.statement.casefold()
    if "approve production" in request or "production ready" in request:
        findings.append("Unsupported production-readiness or implementation approval claim.")
    for assumption in proposal.assumptions:
        if assumption.statement in proposal.established_situation:
            findings.append(f"Unresolved assumption presented as fact: {assumption.identifier}.")
    return tuple(findings)


def build_harbor_street_proposal() -> ProposalPackage:
    """Reuse Chapters 12-15 to construct the canonical, unapproved package."""
    decision = harbor_street_decision_package()
    recommendation = decision.recommendation
    demonstration = execute_harbor_street_demonstration()
    risk_analysis = analyze_harbor_street_risks()
    value = analyze_harbor_street_value()
    scope = tuple(
        ScopeItem(*item)
        for item in (
            (
                "SCOPE-001",
                "Define inquiry statuses and the confirmed-lesson handoff.",
                ("REQ-001", "REQ-002"),
                ("CAP-001",),
                ("RC-001",),
                ("E2", "DEP-002"),
            ),
            (
                "SCOPE-002",
                "Assign process ownership and document staff editing responsibilities.",
                ("REQ-001",),
                ("CAP-001",),
                ("RC-002",),
                ("E5", "COND-002"),
            ),
            (
                "SCOPE-003",
                "Configure the existing shared spreadsheet for status and follow-up visibility.",
                ("REQ-001",),
                ("CAP-001",),
                ("RC-001", "RC-003"),
                ("E2", "GAP-001"),
            ),
            (
                "SCOPE-004",
                "Validate deterministic status history and duplicate-safe scheduling handoff behavior.",
                ("REQ-001", "REQ-002"),
                ("CAP-001",),
                ("FIND-001", "FIND-002"),
                ("EV-STATE", "EV-DUPLICATE"),
            ),
            (
                "SCOPE-005",
                "Collect baseline handling-time and inquiry-outcome measures.",
                ("REQ-001",),
                (),
                ("RC-004",),
                ("VAL-BASELINE", "RISK-004"),
            ),
            (
                "SCOPE-006",
                "Investigate calendar interface feasibility separately.",
                ("REQ-004",),
                ("CAP-004",),
                ("RC-005", "FIND-004"),
                ("INT-UNKNOWN", "RISK-001"),
            ),
        )
    )
    deliverables = (
        ProposedDeliverable(
            "DEL-001",
            "Defined inquiry workflow and responsibility baseline",
            ("SCOPE-001", "SCOPE-002"),
        ),
        ProposedDeliverable("DEL-002", "Configured educational tracking model", ("SCOPE-003",)),
        ProposedDeliverable("DEL-003", "Demonstration evidence and limitations", ("SCOPE-004",)),
        ProposedDeliverable("DEL-004", "Success-measurement baseline plan", ("SCOPE-005",)),
        ProposedDeliverable("DEL-005", "Calendar integration-feasibility findings", ("SCOPE-006",)),
        ProposedDeliverable(
            "DEL-006",
            "Updated risk, assumption, and implementation-readiness recommendation",
            ("SCOPE-001", "SCOPE-005", "SCOPE-006"),
        ),
    )
    decision_request = DecisionRequest(
        "Approve a limited validation and process-standardization phase; this is not approval for production implementation.",
        "Harbor Street Music decision-maker—not established",
        tuple(item.identifier for item in scope),
    )
    executive = ExecutiveSummary(
        "Lesson inquiries are recorded in a shared spreadsheet and confirmed appointments are copied manually to a separate calendar.",
        "The current process does not provide a consistently defined and visible inquiry state across staff follow-up and scheduling roles.",
        "Proceed conditionally with a limited, reversible process-standardization and existing-tool validation phase.",
        recommendation.confidence.basis,
        "Define states and ownership, verify access, collect baselines, and investigate calendar feasibility separately.",
        decision_request.statement,
    )
    placeholders = tuple(
        CommercialPlaceholder(label, CommercialStatus.NOT_ESTABLISHED)
        for label in (
            "Pricing",
            "Payment Terms",
            "Implementation Schedule",
            "Support Terms",
            "Contractual Commitments",
        )
    )
    package = ProposalPackage(
        "Harbor Street Music lesson inquiry process",
        ProposalType.RECOMMENDATION_PACKAGE,
        ProposalLifecycle.DRAFT,
        executive,
        (
            "Approximately 30 lesson inquiries arrive per week.",
            "Two staff members respond to inquiries.",
            "A shared spreadsheet records inquiries; a separate calendar records confirmed appointments.",
            "No documented follow-up process exists.",
        ),
        ("The existing calendar may support a programmatic interface.",),
        (
            "Frequency and meaning of missed inquiries.",
            "Final spending and technology ownership.",
            "Calendar interface, access, and duplicate behavior.",
        ),
        recommendation,
        scope,
        (
            "Production custom application or commercial-platform purchase",
            "Live production calendar integration",
            "Historical-data migration or real customer communications",
            "Security certification, performance testing, and long-term support",
            "Guaranteed business or financial outcomes",
        ),
        deliverables,
        risk_analysis.register.assumptions,
        risk_analysis.register.dependencies,
        risk_analysis.register.risks,
        risk_analysis.register.responses,
        risk_analysis.register.residual_risks,
        ValueSummary(
            value.baseline.known_costs,
            value.baseline.unknown_costs + tuple(cost.description for cost in value.costs),
            tuple(item.hypothesis for item in value.benefits[:2]),
            f"{value.readiness.value}: {value.readiness_reason}",
            tuple(
                item.hypothesis for item in value.benefits if item.value_kind.value == "Intangible"
            ),
            "Illustrative sensitivities vary materially with unestablished time assumptions; they are not canonical ROI.",
        ),
        demonstration.findings,
        demonstration.plan.limitations,
        placeholders,
        decision_request,
        tuple(
            NextStep(index, statement)
            for index, statement in enumerate(
                (
                    "Confirm inquiry-status and handoff definitions.",
                    "Assign process ownership and staff responsibilities.",
                    "Verify authorized access and configure the shared tracking workflow.",
                    "Repeat the defined demonstration with stakeholders.",
                    "Collect baseline handling-time and outcome measures.",
                    "Execute the separately authorized calendar-interface investigation.",
                    "Reassess the recommendation against the new evidence.",
                ),
                1,
            )
        ),
        (
            "This proposal is educational, non-binding, unpriced, and not customer approval.",
            "Demonstration success does not establish security, scale, adoption, reliability, or production readiness.",
            "Proposed deliverables have not yet been delivered.",
        ),
    )
    return replace(package, validation_findings=validate_proposal(package))


def pricing_experiment(original: ProposalPackage) -> ProposalExperiment:
    """Add explicitly fictional terms without mutating canonical facts."""
    changed = replace(
        original,
        commercial_placeholders=(
            CommercialPlaceholder(
                "Implementation Cost", CommercialStatus.EXPERIMENTAL, "USD 1,000 fictional"
            ),
            CommercialPlaceholder(
                "Recurring Cost", CommercialStatus.EXPERIMENTAL, "USD 100/month fictional"
            ),
            CommercialPlaceholder(
                "Payment Assumptions",
                CommercialStatus.EXPERIMENTAL,
                "Fictional: due after validation",
            ),
        ),
    )
    return ProposalExperiment(
        "EXPERIMENTAL COMMERCIAL SCENARIO",
        original,
        changed,
        "Fictional supplied values are visible only in the changed package.",
    )


def scope_expansion_experiment(original: ProposalPackage) -> ProposalExperiment:
    """Expose an untraceable mobile-app expansion."""
    changed = replace(
        original,
        deliverables=original.deliverables
        + (ProposedDeliverable("DEL-MOBILE", "Custom mobile application", ("SCOPE-MISSING",)),),
    )
    changed = replace(changed, validation_findings=validate_proposal(changed))
    return ProposalExperiment(
        "Unsupported scope expansion",
        original,
        changed,
        "The proposed deliverable is not justified by the current recommendation or established requirements.",
    )


def unsupported_promise_experiment(original: ProposalPackage) -> ProposalExperiment:
    """Expose an absolute benefit promise."""
    summary = replace(
        original.executive_summary,
        recommended_direction="This solution will eliminate missed inquiries.",
    )
    changed = replace(original, executive_summary=summary)
    changed = replace(changed, validation_findings=validate_proposal(changed))
    return ProposalExperiment(
        "Unsupported promise",
        original,
        changed,
        "Evidence supports potential visibility and consistency, not guaranteed elimination.",
    )
