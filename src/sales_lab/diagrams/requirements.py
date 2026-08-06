"""Chapter 5 evidence-to-requirement Mermaid diagram."""


def render_requirements_mermaid() -> str:
    """Render the fixed conceptual boundary without implying a product choice."""
    return (
        "flowchart LR\n"
        "    Evidence[Discovery Evidence] --> Requirements[Requirements]\n"
        "    Process[Current-State Process] --> Requirements\n"
        "    Stakeholders[Stakeholders] --> Requirements\n"
        "    Requirements --> Acceptance[Acceptance Criteria]\n"
        "    Requirements --> Future[Future Capability Mapping]\n"
    )
