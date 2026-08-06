"""Stable Markdown report for future-state candidate architectures."""

# Long trace expressions intentionally mirror the educational chain in one place.
# ruff: noqa: E501

from sales_lab.diagrams.architecture import (
    render_architecture_comparison_mermaid,
    render_architecture_mermaid,
)
from sales_lab.services.architecture import ArchitectureAnalysis


def render_architecture_report(analysis: ArchitectureAnalysis) -> str:
    """Render traceability, coverage, comparisons, and unknowns without a winner."""
    validations = analysis.validations
    required = analysis.approach_analysis.gap_analysis.required
    capability_names = {item.identifier: item.name for item in required.capability_map.capabilities}
    requirements = {item.identifier: item for item in required.requirement_set.requirements}
    capability_requirements = {
        capability.identifier: tuple(
            link.requirement_id
            for link in required.capability_map.links
            if link.capability_id == capability.identifier
        )
        for capability in required.capability_map.capabilities
    }

    def bullets(items: tuple[str, ...]) -> list[str]:
        return [f"- {item}" for item in (items or ("None.",))]

    lines = ["# Future-State Solution Architecture", "", "## Engagement"]
    lines.extend(bullets((validations[0].architecture.engagement,)))
    lines.extend(("", "## Architecture Goals"))
    lines.extend(bullets(validations[0].architecture.goals))
    lines.extend(("", "## Architecture Boundaries"))
    lines.extend(
        bullets(
            tuple(
                f"{validation.architecture.identifier} / {component.identifier}: "
                f"{component.boundary.value}"
                for validation in validations
                for component in validation.architecture.components
            )
        )
    )
    lines.extend(("", "## Actors"))
    lines.extend(
        bullets(
            tuple(f"{item.identifier}: {item.name}" for item in validations[0].architecture.actors)
        )
    )
    lines.extend(("", "## Candidate Architectures"))
    lines.extend(
        bullets(
            tuple(
                f"{item.architecture.identifier}: {item.architecture.name} — Chapter 8 "
                f"approach(es) {', '.join(item.architecture.approach_ids)}"
                for item in validations
            )
        )
    )
    lines.extend(("", "## Architecture Components"))
    lines.extend(
        bullets(
            tuple(
                f"{validation.architecture.identifier} / {item.identifier}: {item.name} "
                f"[{item.component_type.value}]"
                for validation in validations
                for item in validation.architecture.components
            )
        )
    )
    lines.extend(("", "## Information Flows"))
    lines.extend(
        bullets(
            tuple(
                f"{validation.architecture.identifier} / {item.identifier}: {item.information} — "
                f"{item.purpose}"
                for validation in validations
                for item in validation.architecture.information_flows
            )
        )
    )
    lines.extend(("", "## Capability Coverage"))
    lines.extend(
        bullets(
            tuple(
                f"{validation.architecture.identifier}: {capability_id} "
                f"({capability_names[capability_id]}) → {component.identifier} ({component.name})"
                for validation in validations
                for component in validation.architecture.components
                for capability_id in component.capability_ids
            )
        )
    )
    lines.extend(("", "## Requirement Traceability"))
    lines.extend(
        bullets(
            tuple(
                f"{requirements[requirement_id].source_evidence_ids[0]} → "
                f"{requirements[requirement_id].stakeholder_id} → {requirement_id} → "
                f"{capability.identifier} → "
                f"{next((gap.capability_id for gap in analysis.approach_analysis.gap_analysis.gaps if gap.capability_id == capability.identifier), 'No current gap')} → "
                f"{validation.architecture.approach_ids[0]} → {component.identifier} → "
                f"{next((flow.identifier for flow in validation.architecture.information_flows if any(connection.identifier == flow.connection_id and component.identifier in (connection.source_id, connection.destination_id) for connection in validation.architecture.connections)), 'No direct flow')}"
                for validation in validations
                for component in validation.architecture.components
                for capability_id in component.capability_ids
                for capability in required.capability_map.capabilities
                if capability.identifier == capability_id
                for requirement_id in capability_requirements[capability_id]
            )
        )
    )
    lines.extend(("", "## Architecture Decisions"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {item.decision} Reason: {item.reason} Alternatives: "
                f"{'; '.join(item.alternatives)} Status: {item.status}."
                for validation in validations
                for item in validation.architecture.decisions
            )
        )
    )
    lines.extend(("", "## Assumptions"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {item.statement}"
                for validation in validations
                for item in validation.architecture.assumptions
            )
        )
    )
    for heading, attribute in (
        ("Unknown Dependencies", "unknown_dependencies"),
        ("Uncovered Capabilities", "uncovered_capabilities"),
        ("Unjustified Components", "unjustified_components"),
    ):
        lines.extend(("", f"## {heading}"))
        lines.extend(
            bullets(
                tuple(
                    f"{validation.architecture.identifier} / {item.subject_id}: {item.message}"
                    for validation in validations
                    for item in getattr(validation, attribute)
                )
            )
        )
    lines.extend(("", "## Architecture Comparison"))
    lines.extend(
        bullets(
            tuple(
                f"{validation.architecture.identifier}: {item.dimension.value} = {item.state.value} — {item.rationale}"
                for validation in validations
                for item in validation.architecture.comparison
            )
        )
    )
    lines.extend(("", "## Open Technical Questions"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {item.question}"
                for item in validations[0].architecture.questions
            )
        )
    )
    lines.extend(("", "## Validation Findings"))
    lines.extend(
        bullets(
            tuple(
                f"{validation.architecture.identifier}: {item.kind} — {item.message}"
                for validation in validations
                for item in (
                    *validation.disconnected_components,
                    *validation.unknown_dependencies,
                    *validation.uncovered_capabilities,
                    *validation.unjustified_components,
                )
            )
        )
    )
    lines.extend(
        (
            "",
            "## Educational Limitations",
            "- These are logical candidates, not approved designs, implementation plans, scores, rankings, or recommendations.",
            "- No vendor, cloud provider, API, protocol, detailed contract, event schema, or database schema is selected or invented.",
            "- Unknown interface does not mean impossible integration; feasibility requires validation.",
            "",
            "## Mermaid Architecture Diagrams",
        )
    )
    for validation in validations:
        lines.extend(
            (
                f"### {validation.architecture.name}",
                "```mermaid",
                render_architecture_mermaid(validation.architecture).rstrip(),
                "```",
            )
        )
    lines.extend(
        (
            "",
            "### Candidate Comparison",
            "```mermaid",
            render_architecture_comparison_mermaid(
                tuple(item.architecture for item in validations)
            ).rstrip(),
            "```",
        )
    )
    return "\n".join(lines) + "\n"
