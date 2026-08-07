"""Stable Markdown report for Chapter 10 integration alternatives."""

from sales_lab.diagrams.integrations import (
    render_api_pattern_mermaid,
    render_event_pattern_mermaid,
    render_integration_boundary_mermaid,
)
from sales_lab.services.integrations import IntegrationAnalysis


def render_integration_report(analysis: IntegrationAnalysis) -> str:
    """Render all required sections without scores, ranking, or a selected pattern."""
    strategies = analysis.strategies

    def bullets(items: tuple[str, ...]) -> list[str]:
        return [f"- {item}" for item in (items or ("None.",))]

    lines = ["# Integration Strategy Analysis", "", "## 1. Engagement"]
    lines.extend(bullets(("Harbor Street Music",)))
    lines.extend(("", "## 2. Architecture Information Flows"))
    lines.extend(
        bullets(tuple(f"{item.information_flow_id}: {item.information}" for item in strategies[:1]))
    )
    lines.extend(("", "## 3. Integration Boundaries"))
    lines.extend(bullets((f"{strategies[0].source_id} → {strategies[0].destination_id}",)))
    lines.extend(("", "## 4. Candidate Integration Patterns"))
    lines.extend(bullets(tuple(f"{item.identifier}: {item.pattern.value}" for item in strategies)))
    lines.extend(
        (
            "",
            "## 5. Pattern Comparison",
            "",
            "| Pattern | Timing | Human Work | Interface Dependency | "
            "Failure Considerations | Feasibility |",
            "|---|---|---|---|---|---|",
        )
    )
    lines.extend(
        f"| {item.pattern.value} | {item.timing.value} | {item.human_work} | "
        f"{item.interface_dependency} | {', '.join(mode.value for mode in item.failure_modes)} | "
        f"{item.feasibility.value} |"
        for item in strategies
    )
    lines.extend(("", "## 6. Data Ownership"))
    lines.extend(
        bullets((f"Inquiry status authoritative source: {strategies[0].data_ownership.value}",))
    )
    lines.extend(("", "## 7. Timing"))
    lines.extend(
        bullets(tuple(f"{item.pattern.value}: {item.timing.value}" for item in strategies))
    )
    for number, category in ((8, "Authentication"), (9, "Authorization")):
        lines.extend(("", f"## {number}. {category} Questions"))
        lines.extend(
            bullets(
                tuple(item.question for item in analysis.questions if item.category == category)
            )
        )
    lines.extend(("", "## 10. Dependencies"))
    lines.extend(
        bullets(
            tuple(
                f"{dependency.identifier}: {dependency.description}"
                for item in strategies
                for dependency in item.dependencies
            )
        )
    )
    lines.extend(("", "## 11. Assumptions"))
    lines.extend(
        bullets(
            tuple(
                f"{assumption.identifier}: {assumption.statement} [{assumption.status.value}]"
                for item in strategies
                for assumption in item.assumptions
            )
        )
    )
    lines.extend(("", "## 12. Technical Feasibility"))
    lines.extend(
        bullets(tuple(f"{item.identifier}: {item.feasibility.value}" for item in strategies))
    )
    lines.extend(("", "## 13. Failure Modes"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {', '.join(mode.value for mode in item.failure_modes)}"
                for item in strategies
            )
        )
    )
    lines.extend(("", "## 14. Duplicate Delivery Considerations"))
    lines.extend(
        bullets(
            (
                "A repeated event can create two effects unless requirements establish "
                "idempotent handling.",
            )
        )
    )
    lines.extend(("", "## 15. Unknown Interfaces"))
    lines.extend(
        bullets(
            tuple(
                f"{finding.strategy_id}: {finding.message}"
                for finding in analysis.findings
                if finding.kind == "Unverified External Interface"
            )
        )
    )
    lines.extend(("", "## 16. Traceability"))
    lines.extend(
        bullets(tuple(" → ".join((*item.traceability, item.identifier)) for item in strategies))
    )
    lines.extend(("", "## 17. Open Technical Questions"))
    lines.extend(bullets(tuple(f"{item.category}: {item.question}" for item in analysis.questions)))
    lines.extend(
        (
            "",
            "## 18. Educational Limitations",
            "- This analysis does not build an API, broker, file transfer, identity platform, "
            "or retry engine.",
            "- Candidates are not numeric scores, a ranking, a winner, or a technical promise.",
            "- Unknown interface does not mean impossible integration; vendor claims do not "
            "establish a design.",
            "",
            "## Mermaid Diagrams",
            "",
            "```mermaid",
            render_integration_boundary_mermaid(strategies[0]).rstrip(),
            "```",
            "",
            "```mermaid",
            render_api_pattern_mermaid(strategies[2]).rstrip(),
            "```",
            "",
            "```mermaid",
            render_event_pattern_mermaid(strategies[4]).rstrip(),
            "```",
            "",
        )
    )
    return "\n".join(lines)
