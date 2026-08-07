"""Mermaid rendering for Chapter 11 structured automation data."""

from sales_lab.domain.automation import AutomationAssessment


def render_human_loop_mermaid(assessment: AutomationAssessment) -> str:
    """Render the reminder path using the supplied assessment label."""
    return (
        "flowchart TD\n"
        "    Inquiry[Active Inquiry] --> Check[Evaluate Reminder Rule]\n"
        "    Check -->|Rule not satisfied| Stop[No Action]\n"
        f"    Check -->|Rule satisfied| Reminder[{assessment.activity.name}]\n"
        "    Reminder --> Staff[Staff Reviews Inquiry]\n"
        "    Staff --> Decision{Human Decision}\n"
        "    Decision -->|Follow Up| Contact[Contact Prospect]\n"
        "    Decision -->|Close| Close[Close Inquiry]\n"
        "    Decision -->|More Information Needed| Research[Gather Information]\n"
    )


def render_approval_mermaid(assessment: AutomationAssessment) -> str:
    """Render an explicit approval boundary from the authored assessment."""
    if assessment.approval_boundary is None:
        message = "assessment has no approval boundary"
        raise ValueError(message)
    return (
        "stateDiagram-v2\n"
        "    [*] --> Drafted\n"
        "    Drafted --> AwaitingApproval\n"
        "    AwaitingApproval --> Approved\n"
        "    AwaitingApproval --> Rejected\n"
        "    Approved --> ReadyForExternalAction\n"
        "    Rejected --> [*]\n"
    )
