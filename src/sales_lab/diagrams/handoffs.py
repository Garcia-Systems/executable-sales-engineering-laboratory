"""Mermaid views of the Chapter 17 handoff and lifecycle."""


def render_handoff_mermaid() -> str:
    """Render the decision-gated delivery flow."""
    return """flowchart LR
    Recommendation[Recommendation] --> Proposal[Proposal]
    Proposal --> Decision{Customer Decision}
    Decision -->|Not Approved| Hold[No Implementation Handoff]
    Decision -->|Approved Scope| Baseline[Delivery Baseline]
    Baseline --> Readiness[Readiness Assessment]
    Readiness -->|Ready| Delivery[Implementation May Begin]
    Readiness -->|Conditional| Limited[Limited Work Boundary]
    Readiness -->|Not Ready| Resolve[Resolve Blocking Conditions]
    Resolve --> Readiness
"""


def render_lifecycle_mermaid() -> str:
    """Render only supported lifecycle transitions."""
    return """stateDiagram-v2
    [*] --> Recommended
    Recommended --> Proposed
    Proposed --> Presented
    Presented --> Approved
    Presented --> Rejected
    Approved --> ReadyForDelivery
    Approved --> OnHold
    ReadyForDelivery --> InImplementation
    InImplementation --> Implemented
    Implemented --> Validated
"""
