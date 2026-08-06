"""Deterministic Chapter 6 matrices and Markdown report."""

from sales_lab.diagrams.capabilities import render_capability_mermaid
from sales_lab.services.capabilities import CapabilityAnalysis


def render_capability_matrix(analysis: CapabilityAnalysis) -> str:
    """Render capabilities by established requirements without numeric scoring."""
    requirement_ids = tuple(item.requirement.identifier for item in analysis.coverage)
    rows = [
        "| " + " | ".join(("Capability", *requirement_ids)) + " |",
        "| " + " | ".join("---" for _ in range(len(requirement_ids) + 1)) + " |",
    ]
    links = {(link.capability_id, link.requirement_id) for link in analysis.capability_map.links}
    for capability in analysis.capability_map.capabilities:
        cells = tuple(
            "Supports" if (capability.identifier, requirement_id) in links else "—"
            for requirement_id in requirement_ids
        )
        rows.append("| " + " | ".join((capability.name, *cells)) + " |")
    return "\n".join(rows) + "\n"


def render_requirement_coverage(analysis: CapabilityAnalysis) -> str:
    """Render the inverse mapping and qualitative coverage state."""
    rows = [
        "| Requirement | Supporting Capabilities | Coverage |",
        "| --- | --- | --- |",
    ]
    rows.extend(
        f"| {item.requirement.identifier} | {', '.join(item.capability_ids) or 'None'} | "
        f"{item.status.value} |"
        for item in analysis.coverage
    )
    return "\n".join(rows) + "\n"


def render_capability_report(analysis: CapabilityAnalysis) -> str:
    """Render the mandated analysis sections in stable input order."""
    capabilities = analysis.capability_map.capabilities
    links = analysis.capability_map.links
    evidence = {item.identifier: item for item in analysis.stakeholder_map.evidence}
    requirements = tuple(item.requirement for item in analysis.coverage)
    role_names = {item.identifier: item.name for item in analysis.stakeholder_map.roles}

    def bullets(items: tuple[str, ...]) -> list[str]:
        return [f"- {item}" for item in (items or ("None.",))]

    lines = ["# Capability Mapping Analysis", "", "## Engagement"]
    lines.extend(bullets((analysis.capability_map.engagement,)))
    lines.extend(("", "## Established Requirements"))
    lines.extend(bullets(tuple(f"{item.identifier}: {item.statement}" for item in requirements)))
    lines.extend(("", "## Candidate Capabilities"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {item.name} ({item.category.value}) — {item.description}"
                for item in capabilities
            )
        )
    )
    lines.extend(("", "## Requirement-to-Capability Mapping"))
    lines.extend(
        bullets(
            tuple(
                f"{item.requirement_id} → {item.capability_id} ({item.coverage.value})"
                for item in links
            )
        )
    )
    lines.extend(("", "## Capability Matrix", render_capability_matrix(analysis).rstrip()))
    lines.extend(("", "## Requirement Coverage", render_requirement_coverage(analysis).rstrip()))
    lines.extend(("", "## Capability Gaps"))
    gap_items = (*analysis.gaps, *analysis.incomplete_mappings)
    lines.extend(
        bullets(tuple(f"{item.subject_id} [{item.kind}]: {item.message}" for item in gap_items))
    )
    lines.extend(("", "## Unsupported Capabilities"))
    lines.extend(
        bullets(
            tuple(
                f"{item.subject_id}: Unsupported capability. {item.message}"
                for item in analysis.unsupported_capabilities
            )
        )
    )
    lines.extend(("", "## Open Questions"))
    lines.extend(bullets(analysis.capability_map.open_questions))
    lines.extend(("", "## Traceability"))
    for link in links:
        requirement = next(
            (item for item in requirements if item.identifier == link.requirement_id), None
        )
        if requirement is not None:
            sources = ", ".join(
                f"{identifier} ({evidence[identifier].source})"
                for identifier in requirement.source_evidence_ids
                if identifier in evidence
            )
            lines.append(
                f"- {link.capability_id} ← {requirement.identifier} ← "
                f"{role_names.get(requirement.stakeholder_id, requirement.stakeholder_id)} ← "
                f"{sources or 'Evidence unavailable'}"
            )
    lines.extend(
        (
            "",
            "## Educational Limitations",
            "- Coverage records explicit mappings; it does not rank products or prove solution "
            "fit.",
            "- Categories are educational organization mechanisms, not universal standards.",
            "- No capability is invented from natural-language requirements; professional review "
            "remains necessary.",
            "- This chapter makes no vendor, architecture, build-versus-buy, ROI, or "
            "implementation decision.",
            "",
            "## Mermaid Diagram",
            "```mermaid",
            render_capability_mermaid(analysis).rstrip(),
            "```",
        )
    )
    return "\n".join(lines) + "\n"
