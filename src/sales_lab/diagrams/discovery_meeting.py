"""Mermaid source for the Chapter 2 discovery workflow."""


def discovery_meeting_flowchart() -> str:
    """Return the fixed flow that places discovery before future design."""
    return """flowchart LR
    A[Prepare Questions]
    --> B[Discovery Meeting]
    --> C[Capture Responses]
    --> D[Evidence Records]
    --> E[Open Questions]
    --> F[Future Requirements Gathering]
"""
