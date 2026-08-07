"""Deterministic executive, technical, and customer proposal views."""

# ruff: noqa: E501, FLY002

from sales_lab.domain.proposals import ProposalPackage


def _bullets(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- None"


def render_customer_proposal(proposal: ProposalPackage) -> str:
    """Render the customer-facing view from the shared structured package."""
    summary = proposal.executive_summary
    sections = [
        "# Harbor Street Music — Sales Engineering Recommendation Package",
        "## 1. Executive Summary\n"
        + " ".join(
            (
                summary.customer_situation,
                summary.problem,
                summary.recommended_direction,
                summary.rationale,
                summary.major_conditions,
                summary.requested_decision,
            )
        ),
        "## 2. Customer Situation\n### Established\n"
        + _bullets(proposal.established_situation)
        + "\n### Assumed\n"
        + _bullets(proposal.assumed_situation)
        + "\n### Unknown\n"
        + _bullets(proposal.unknown_situation),
        "## 3. Evidence-Supported Problem\n" + summary.problem,
        "## 4. Recommended Direction\n"
        + proposal.recommendation.statement
        + "\n\nThis recommendation has not been approved.",
        "## 5. Scope\n"
        + _bullets(tuple(f"{item.identifier}: {item.statement}" for item in proposal.scope)),
        "## 6. Exclusions\n" + _bullets(proposal.exclusions),
        "## 7. Proposed Deliverables\n"
        + _bullets(tuple(f"{item.identifier}: {item.statement}" for item in proposal.deliverables)),
        "## 8. Demonstration Findings\n"
        + _bullets(
            tuple(
                f"{item.identifier} — {item.state.value}: {item.description}"
                for item in proposal.demonstration_findings
            )
        )
        + "\n\nLimitations:\n"
        + _bullets(tuple(item.description for item in proposal.demonstration_limitations)),
        "## 9. Value Summary\nCalculation readiness: "
        + proposal.value_summary.calculation_readiness
        + "\n\nBenefit hypotheses:\n"
        + _bullets(proposal.value_summary.benefit_hypotheses)
        + "\n\nUnresolved costs:\n"
        + _bullets(proposal.value_summary.unresolved_cost_information)
        + "\n\nROI is not ready.",
        "## 10. Risks\n"
        + _bullets(
            tuple(
                f"{risk.identifier}: Cause: {risk.cause} Event: {risk.event} "
                f"Consequence: {risk.consequence} Planned response: "
                f"{next((response.action for response in proposal.risk_responses if response.risk_id == risk.identifier), 'not established')} "
                f"Residual uncertainty: "
                f"{next((residual.statement for residual in proposal.residual_risks if residual.risk_id == risk.identifier), 'not established')}"
                for risk in proposal.risks
            )
        ),
        "## 11. Assumptions\n"
        + _bullets(
            tuple(
                f"{item.identifier} [{item.validation_status.value}]: {item.statement}; validate: {item.validation_action.action if item.validation_action else 'not defined'}; if false: {item.consequence_if_false}"
                for item in proposal.assumptions
            )
        ),
        "## 12. Dependencies\n"
        + _bullets(
            tuple(
                f"{item.identifier} [{item.status.value}]: {item.statement}; resolve: {item.resolution_action.action if item.resolution_action else 'not defined'}; if unmet: {item.consequence_if_unmet}"
                for item in proposal.dependencies
            )
        ),
        "## 13. Commercial Information\n"
        + _bullets(
            tuple(
                f"{item.label}: {item.status.value}" + (f" — {item.value}" if item.value else "")
                for item in proposal.commercial_placeholders
            )
        ),
        "## 14. Decision Requested\n" + proposal.decision_request.statement,
        "## 15. Proposed Next Steps\n"
        + "\n".join(f"{item.order}. {item.statement}" for item in proposal.next_steps),
        "## 16. Limitations\n" + _bullets(proposal.limitations),
    ]
    return "\n\n".join(sections) + "\n"


def render_traceability(proposal: ProposalPackage) -> str:
    """Render stable scope-to-evidence traceability."""
    rows = [
        "| Proposal Item | Requirement | Capability | Recommendation Finding | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    rows.extend(
        f"| {item.identifier} | {', '.join(item.requirement_ids) or '—'} | {', '.join(item.capability_ids) or '—'} | {', '.join(item.recommendation_finding_ids)} | {', '.join(item.evidence_ids)} |"
        for item in proposal.scope
    )
    return "\n".join(rows) + "\n"


def render_executive_view(proposal: ProposalPackage) -> str:
    """Render business-oriented information without changing the conclusion."""
    return render_customer_proposal(proposal)


def render_technical_view(proposal: ProposalPackage) -> str:
    """Render technical traceability and unresolved evidence from the same package."""
    return (
        "# Internal Decision Package\n\n## 1. Evidence Traceability\n"
        + render_traceability(proposal)
        + "\n## 2. Requirements Coverage\n"
        + _bullets(
            tuple(
                sorted(
                    {identifier for item in proposal.scope for identifier in item.requirement_ids}
                )
            )
        )
        + "\n\n## 3. Capability Coverage\n"
        + _bullets(
            tuple(
                sorted(
                    {identifier for item in proposal.scope for identifier in item.capability_ids}
                )
            )
        )
        + "\n\n## 4. Candidate Alternatives\n"
        + _bullets(
            tuple(
                f"{item.approach_id}: {item.description}"
                for item in proposal.recommendation.alternatives
            )
        )
        + "\n\n## 5. Architecture Summary\nExisting-tool configuration retains the manual calendar boundary.\n\n## 6. Integration Questions\n"
        + _bullets(proposal.unknown_situation)
        + "\n\n## 7. Automation Boundaries\nNo live communications or calendar automation is proposed.\n\n## 8. Value Readiness\n"
        + proposal.value_summary.calculation_readiness
        + "\n\n## 9. Risk Register\n"
        + _bullets(tuple(item.identifier for item in proposal.risks))
        + "\n\n## 10. Demonstration Coverage\n"
        + _bullets(
            tuple(
                f"{item.identifier}: {item.state.value}" for item in proposal.demonstration_findings
            )
        )
        + "\n\n## 11. Recommendation Conditions\n"
        + _bullets(
            tuple(
                f"{item.identifier}: {item.description}"
                for item in proposal.recommendation.conditions
            )
        )
        + "\n\n## 12. Change Triggers\n"
        + _bullets(
            tuple(
                f"{item.identifier}: {item.condition}"
                for item in proposal.recommendation.change_triggers
            )
        )
        + "\n\n## 13. Proposal Validation Findings\n"
        + (
            _bullets(proposal.validation_findings)
            if proposal.validation_findings
            else "- No validation findings."
        )
        + "\n"
    )
