"""Deterministic Chapter 17 Markdown delivery package."""

# ruff: noqa: E501

from sales_lab.diagrams.handoffs import render_handoff_mermaid, render_lifecycle_mermaid
from sales_lab.domain.handoffs import DeliveryPackage, ResponsibilityCategory, ScopeStatus


def _bullets(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def _scope(package: DeliveryPackage, status: ScopeStatus) -> tuple[str, ...]:
    return tuple(
        f"{item.identifier}: {item.statement} [{item.status.value}]"
        for item in package.handoff.scope_items
        if item.status is status
    )


def render_handoff_checklist(package: DeliveryPackage) -> str:
    """Render explicit conditions without a deceptive percentage."""
    rows = [
        "| Readiness Condition | Status | Evidence | Blocking? | Next Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    rows.extend(
        f"| {item.condition.value} | {item.status.value} | {item.evidence} | {'Yes' if item.blocking else 'No'} | {item.next_action} |"
        for item in package.readiness_conditions
    )
    return "\n".join(rows) + "\n"


def render_handoff_report(package: DeliveryPackage) -> str:
    """Render the complete delivery-facing baseline in stable source order."""
    handoff = package.handoff
    proposed = _scope(package, ScopeStatus.PROPOSED) + _scope(package, ScopeStatus.UNDER_REVIEW)
    approved = _scope(package, ScopeStatus.APPROVED)
    deferred = _scope(package, ScopeStatus.DEFERRED) + _scope(package, ScopeStatus.REJECTED)
    requirements = tuple(
        f"Included: {item}" for item in handoff.requirements_baseline.included_ids
    ) + tuple(f"Unresolved: {item}" for item in handoff.requirements_baseline.unresolved)
    integrations = tuple(
        f"{item.identifier}: {item.source} → {item.destination}; {item.pattern}; feasibility={item.feasibility}; questions={'; '.join(item.unresolved_questions) or 'None'}"
        for item in handoff.integration_readiness
    )
    automations = tuple(
        f"{item.identifier}: {item.mode}; {item.readiness}; human={item.human_responsibility}"
        for item in handoff.automation_readiness
    )
    acceptance = tuple(
        f"{item.requirement_id}: {item.criterion}; method={item.validation_method}; validator={item.validating_role}; status={item.status.value}"
        for item in handoff.acceptance_baseline
    )
    responsibilities = tuple(
        f"{item.area}: {item.role} [{item.category.value}]" for item in handoff.responsibilities
    )
    ownership_gaps = tuple(
        item.area
        for item in handoff.responsibilities
        if item.category is ResponsibilityCategory.NOT_ESTABLISHED
    )
    trace = tuple(
        f"{item.trace_ids[0] if item.trace_ids else 'No evidence'} → {' / '.join(item.trace_ids[1:]) if len(item.trace_ids) > 1 else 'baseline'} → {item.identifier} → acceptance evidence"
        for item in handoff.scope_items
    )
    sections = (
        ("Engagement", (handoff.engagement,)),
        ("Handoff Type", (handoff.handoff_type.value,)),
        ("Lifecycle Status", (handoff.lifecycle_status.value,)),
        (
            "Delivery Readiness",
            (package.readiness.value, "No numeric readiness score is calculated."),
        ),
        ("Proposed Scope", proposed),
        ("Approved Scope", approved),
        ("Deferred and Rejected Scope", deferred),
        ("Exclusions", handoff.exclusions),
        ("Requirements Baseline", (handoff.requirements_baseline.identifier, *requirements)),
        (
            "Architecture Baseline",
            (
                f"Candidate {handoff.architecture_baseline.candidate_id}; final={handoff.architecture_baseline.final}",
                *handoff.architecture_baseline.known_components,
                *handoff.architecture_baseline.unresolved_choices,
            ),
        ),
        ("Integration Readiness", integrations),
        ("Automation Readiness", automations),
        ("Acceptance Baseline", acceptance),
        ("Risks", handoff.risks),
        ("Assumptions", handoff.assumptions),
        ("Dependencies", handoff.dependencies),
        (
            "Unresolved Decisions",
            tuple(
                f"{item.identifier}: {item.question}; owner={item.owner}; due={item.due_point}; consequence={item.consequence}"
                for item in handoff.unresolved_decisions
            ),
        ),
        (
            "Technical Discovery",
            tuple(
                f"{item.identifier}: {item.stage.value}; {item.question}; blocking={item.blocking}"
                for item in handoff.technical_discovery
            ),
        ),
        (
            "Responsibilities",
            responsibilities + tuple(f"Ownership gap: {item}" for item in ownership_gaps),
        ),
        (
            "Change-Control Boundary",
            (
                handoff.change_control.baseline,
                f"Clarification: {handoff.change_control.clarification}",
                f"Scope change: {handoff.change_control.scope_change}",
                f"Authority: {handoff.change_control.approval_authority}",
                handoff.change_control.traceability_update,
                handoff.change_control.acceptance_effect,
            ),
        ),
        (
            "Blocking Conditions",
            tuple(f"{item.identifier}: {item.statement}" for item in package.blocking_findings),
        ),
        (
            "Non-Blocking Follow-Up",
            tuple(item.statement for item in package.non_blocking_follow_up),
        ),
        (
            "Handoff Artifacts",
            tuple(
                f"{item.name} (Chapter {item.source_chapter}) — {item.status}; consumer={item.consumer}; limitation={item.limitation}"
                for item in handoff.artifacts
            ),
        ),
        ("Traceability", trace),
        ("Next Decision", package.next_actions),
        (
            "Educational Limitations",
            (
                "This package is educational and is not customer approval, a contract, a schedule, production deployment, or customer acceptance.",
                "DEMONSTRATION_RESULT != CUSTOMER_ACCEPTANCE",
                "A candidate architecture is not silently promoted to final.",
            ),
        ),
    )
    body = ["# Implementation Handoff and Delivery Readiness Report", ""]
    for heading, items in sections:
        body.extend((f"## {heading}", _bullets(items), ""))
    body.extend(
        (
            "## Handoff Checklist",
            render_handoff_checklist(package),
            "## Handoff Flow",
            "```mermaid",
            render_handoff_mermaid().rstrip(),
            "```",
            "",
            "## Lifecycle",
            "```mermaid",
            render_lifecycle_mermaid().rstrip(),
            "```",
            "",
        )
    )
    return "\n".join(body)
