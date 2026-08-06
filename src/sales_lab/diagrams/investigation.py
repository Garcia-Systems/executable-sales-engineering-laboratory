"""Mermaid source for the Chapter 1 evidence flow."""


def investigation_flowchart() -> str:
    """Return a stable diagram that deliberately ends before recommendations."""
    return """flowchart TD
    A[Customer Statement] --> B[Evidence Collection]
    B --> C[Verified Facts]
    B --> D[Observations]
    C --> E[Problem Hypotheses]
    D --> E
    E --> F[Future Chapters]
    F --> G[No recommendations in Chapter 1]
"""
