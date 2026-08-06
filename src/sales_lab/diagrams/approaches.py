"""Chapter 8 multiple-path solution-approach diagram."""


def render_approach_mermaid() -> str:
    """Render alternatives converging only on later evaluation."""
    return """flowchart TD
    Gap[Capability Gap]
    Gap --> Process[Change Process]
    Gap --> Configure[Configure Existing]
    Gap --> Integrate[Integrate Existing]
    Gap --> Buy[Buy]
    Gap --> Build[Build]
    Gap --> Hybrid[Hybrid]
    Gap --> StatusQuo[Status Quo]
    Process --> Evaluate[Future Evaluation]
    Configure --> Evaluate
    Integrate --> Evaluate
    Buy --> Evaluate
    Build --> Evaluate
    Hybrid --> Evaluate
    StatusQuo --> Evaluate
"""
