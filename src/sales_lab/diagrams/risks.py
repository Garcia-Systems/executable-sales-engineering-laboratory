"""Mermaid views generated from the Chapter 13 model."""

from sales_lab.domain.risks import RiskAnalysis


def render_risk_relationship_mermaid(analysis: RiskAnalysis) -> str:
    """Render model-supported relationships rather than disconnected prose."""
    has_mitigation = any(
        response.response_type.value != "Contingency" for response in analysis.register.responses
    )
    lines = [
        "flowchart LR",
        "    Assumption[Unverified Assumption] --> Risk[Risk Event]",
        "    Dependency[Dependency] --> Risk",
        "    Constraint[Constraint] --> Approach[Solution Approach]",
        "    Risk --> Consequence[Consequence]",
    ]
    if has_mitigation:
        lines.extend(
            ("    Risk --> Mitigation[Mitigation]", "    Mitigation --> Residual[Residual Risk]")
        )
    if any(
        response.response_type.value == "Contingency" for response in analysis.register.responses
    ):
        lines.append("    Risk --> Contingency[Contingency]")
    return "\n".join(lines) + "\n"


def render_risk_lifecycle_mermaid() -> str:
    """Render only lifecycle transitions supported by RiskStatus."""
    return """stateDiagram-v2
    [*] --> Identified
    Identified --> UnderReview
    UnderReview --> ResponsePlanned
    ResponsePlanned --> Mitigated
    ResponsePlanned --> Accepted
    Mitigated --> Closed
    Mitigated --> UnderReview
    Accepted --> Closed
"""
