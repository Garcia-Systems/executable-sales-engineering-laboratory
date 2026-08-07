"""Deterministic Chapter 15 Mermaid diagrams."""

from sales_lab.domain.demonstrations import DemonstrationPlan


def render_demonstration_sequence(plan: DemonstrationPlan) -> str:
    """Render the canonical scenario without implying a real calendar call."""
    actions = {
        "STEP-001": "Staff->>Inquiry: Create fictional inquiry",
        "STEP-002": "Staff->>Inquiry: Assign responsibility",
        "STEP-003": "Staff->>Inquiry: Record status NEW",
        "STEP-004": "Staff->>Inquiry: Record follow-up",
        "STEP-005": "Staff->>Inquiry: Retrieve current state and history",
        "STEP-006": "Staff->>Inquiry: Confirm lesson",
        "STEP-007": "Inquiry->>Handoff: Prepare simulated scheduling handoff",
        "STEP-008": "Staff->>Inquiry: Repeat confirmation",
        "STEP-009": "Inquiry-->>Staff: Duplicate recognized; one effect",
    }
    lines = [
        "sequenceDiagram",
        "    participant Staff as Front Desk Staff",
        "    participant Inquiry as Inquiry Workflow",
        "    participant Handoff as Simulated Scheduling Handoff",
    ]
    lines.extend(f"    {actions[step.identifier]}" for step in plan.steps)
    return "\n".join(lines) + "\n"


def render_demonstration_lifecycle() -> str:
    """Show evidence informing rather than authorizing a later decision."""
    return (
        "flowchart LR\n"
        "    Question[Question] --> Objective[Demonstration Objective]\n"
        "    Objective --> Plan[Plan]\n"
        "    Plan --> Execute[Execute]\n"
        "    Execute --> Evidence[Evidence]\n"
        "    Evidence --> Finding[Finding]\n"
        "    Finding --> Decision[Future Decision]\n"
        "    Finding --> Limitations[Limitations]\n"
    )
