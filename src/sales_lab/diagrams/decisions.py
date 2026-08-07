"""Mermaid generation for transparent decision analysis."""

from sales_lab.domain.decisions import DecisionPackage


def render_decision_mermaid(package: DecisionPackage) -> str:
    """Render the fixed concept flow only when its structured stages exist."""
    if not package.criteria or not package.evaluations:
        message = "decision diagram requires criteria and evaluations"
        raise ValueError(message)
    return """flowchart TD
    Evidence[Evidence] --> Criteria[Decision Criteria]
    Criteria --> Evaluate[Approach Evaluations]
    Evaluate --> Conditions[Mandatory Conditions]
    Evaluate --> Tradeoffs[Tradeoffs]
    Evaluate --> Risks[Risks and Unknowns]
    Conditions --> Judgment[Professional Judgment]
    Tradeoffs --> Judgment
    Risks --> Judgment
    Judgment --> Recommendation[Conditional Recommendation]
    Recommendation --> Validate[Validation Conditions]
    Recommendation --> Alternatives[Retained Alternatives]
    Recommendation --> Triggers[Change Triggers]
"""
