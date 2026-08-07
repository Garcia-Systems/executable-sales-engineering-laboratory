"""Generated Chapter 19 dependency and traceability diagrams."""

from sales_lab.domain.engagements import SalesEngineeringEngagement
from sales_lab.services.engagements import STAGE_DEPENDENCIES


def render_engagement_mermaid() -> str:
    """Render the stage dependency graph from its structured definition."""
    lines = ["flowchart TD"]
    for target, sources in STAGE_DEPENDENCIES.items():
        target_id = target.name.title().replace("_", "")
        for source in sources:
            source_id = source.name.title().replace("_", "")
            lines.append(f"    {source_id}[{source.value}] --> {target_id}[{target.value}]")
    return "\n".join(lines) + "\n"


def render_traceability_mermaid(engagement: SalesEngineeringEngagement) -> str:
    """Render one actual canonical chain beginning with legacy evidence identifier E2."""
    wanted = {"E2", "REQ-001", "CAP-001", "APP-001", "ARCH-001", "REC-001"}
    links = [
        item
        for item in engagement.trace_links
        if item.source_id in wanted and item.target_id in wanted
    ]
    lines = ["flowchart LR"]
    lines.extend(
        f'    {index}["{item.source_id}"] --> {index + 1}["{item.target_id}"]'
        for index, item in enumerate(links)
    )
    return "\n".join(lines) + "\n"
