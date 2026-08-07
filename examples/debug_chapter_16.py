"""Chapter 16 debugging laboratory: inspect proposal construction and validation."""

# ruff: noqa: T201

from sales_lab.services.proposals import build_harbor_street_proposal


def main() -> None:
    """Create named inspection points rather than relying on source line numbers."""
    proposal = build_harbor_street_proposal()
    executive_summary = proposal.executive_summary
    scope = proposal.scope
    exclusions = proposal.exclusions
    deliverables = proposal.deliverables
    risks = proposal.risks
    assumptions = proposal.assumptions
    commercial_placeholders = proposal.commercial_placeholders
    decision_request = proposal.decision_request
    validation_findings = proposal.validation_findings
    print(executive_summary.requested_decision)
    print(len(scope), len(exclusions), len(deliverables), len(risks), len(assumptions))
    print(commercial_placeholders, decision_request, validation_findings)


if __name__ == "__main__":
    main()
