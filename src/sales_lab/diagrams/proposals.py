"""Chapter 16 proposal-flow diagram."""


def render_proposal_mermaid() -> str:
    """Show that the package informs rather than makes the decision."""
    return """flowchart LR
    Evidence[Evidence] --> Recommendation[Recommendation]
    Recommendation --> Scope[Scope]
    Recommendation --> Exclusions[Exclusions]
    Scope --> Deliverables[Proposed Deliverables]
    Risks[Risks] --> Package[Decision Package]
    Assumptions[Assumptions and Dependencies] --> Package
    Value[Value Findings] --> Package
    Demo[Demonstration Evidence] --> Package
    Recommendation --> Package
    Deliverables --> Package
    Exclusions --> Package
    Package --> Decision[Customer Decision]
"""
