"""Mermaid generation for Chapter 12 value traceability."""


def render_value_mermaid() -> str:
    """Show that transparent analysis informs rather than makes a decision."""
    return """flowchart LR
    Evidence[Discovery Evidence] --> Requirement[Requirement]
    Requirement --> Gap[Capability Gap]
    Gap --> Approach[Solution Approach]
    Approach --> Costs[Cost Estimates]
    Approach --> Benefits[Benefit Hypotheses]
    Costs --> Assumptions[Assumptions and Ranges]
    Benefits --> Assumptions
    Assumptions --> Scenarios[Scenario Analysis]
    Scenarios --> Results[Transparent Calculations]
    Results --> Decision[Future Decision Process]
"""
