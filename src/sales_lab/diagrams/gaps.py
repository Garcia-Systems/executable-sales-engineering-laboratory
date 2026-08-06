"""Chapter 7 current-versus-required capability diagram."""


def render_gap_mermaid() -> str:
    """Render the stable teaching flow, including the no-purchase boundary."""
    return """flowchart LR
    R[Requirements] --> RC[Required Capabilities]
    CR[Current Resources] --> CC[Current Capabilities]
    RC --> Compare{Compare evidence}
    CC --> Compare
    Compare --> Existing[Capability Available]
    Compare --> Partial[Partially Available]
    Compare --> Gap[Capability Gap]
    Compare --> Unknown[Unknown]
    Partial --> Investigate[Further Investigation]
    Unknown --> Investigate
    Gap --> Future[Future Solution Analysis]
    Future --> Boundary[Gap ≠ Purchase]
"""
