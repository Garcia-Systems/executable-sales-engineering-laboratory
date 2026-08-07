"""Structured Mermaid renderers for Chapter 10."""

from sales_lab.domain.integrations import IntegrationStrategy


def render_integration_boundary_mermaid(strategy: IntegrationStrategy) -> str:
    """Render the actual endpoints and information from a strategy."""
    return (
        "flowchart LR\n"
        f"    {strategy.source_id}[{strategy.source_id}] -->|{strategy.information}| "
        f"{strategy.destination_id}[{strategy.destination_id}]\n"
        "    CMP-SCHEDULE -.->|Integration mechanism unknown| CMP-CALENDAR[Existing Calendar]\n"
    )


def render_api_pattern_mermaid(strategy: IntegrationStrategy) -> str:
    """Render a conceptual request/response exchange."""
    return (
        "sequenceDiagram\n"
        f"    participant A as {strategy.source_id}\n"
        f"    participant B as {strategy.destination_id}\n"
        f"    A->>B: Request: {strategy.information}\n"
        "    B-->>A: Response\n"
    )


def render_event_pattern_mermaid(strategy: IntegrationStrategy) -> str:
    """Render producer, event/channel, and consumer roles."""
    return (
        "flowchart LR\n"
        f"    {strategy.source_id}[Producer] --> EVENT[Confirmed Lesson Event]\n"
        f"    EVENT --> {strategy.destination_id}[Consumer]\n"
    )
