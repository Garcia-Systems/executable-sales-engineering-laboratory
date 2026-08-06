"""Deterministic Chapter 7 matrix and Markdown report."""

from sales_lab.diagrams.gaps import render_gap_mermaid
from sales_lab.domain.gaps import GapType
from sales_lab.services.gaps import GapAnalysis


def render_current_capability_matrix(analysis: GapAnalysis) -> str:
    """Render required capabilities against evidenced current resources."""
    capabilities = {item.identifier: item for item in analysis.required.capability_map.capabilities}
    resources = {item.identifier: item for item in analysis.inventory.resources}
    rows = [
        "| Required Capability | Current Resource | Current State | Gap |",
        "| --- | --- | --- | --- |",
    ]
    for item in analysis.assessments:
        resource_names = (
            ", ".join(
                resources[identifier].name
                for identifier in item.current_resource_ids
                if identifier in resources
            )
            or "None evidenced"
        )
        gap = item.gap_type.value if item.gap_type is not None else "No established gap"
        rows.append(
            f"| {capabilities[item.capability_id].name} ({item.capability_id}) | "
            f"{resource_names} | {item.state.value} | {gap} |"
        )
    return "\n".join(rows) + "\n"


def render_gap_report(analysis: GapAnalysis) -> str:
    """Render all required Chapter 7 sections in stable capability order."""
    capabilities = {item.identifier: item for item in analysis.required.capability_map.capabilities}
    resources = {item.identifier: item for item in analysis.inventory.resources}
    evidence = {item.identifier: item for item in analysis.inventory.evidence}

    def bullets(items: tuple[str, ...]) -> list[str]:
        return [f"- {item}" for item in (items or ("None.",))]

    lines = ["# Current Capability & Gap Analysis", "", "## Engagement"]
    lines.extend(bullets((analysis.inventory.engagement,)))
    lines.extend(("", "## Required Capabilities"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {item.name} — {item.description}"
                for item in analysis.required.capability_map.capabilities
            )
        )
    )
    lines.extend(("", "## Current Resources"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {item.name} — {item.description} "
                f"(evidence: {', '.join(item.evidence_ids)})"
                for item in analysis.inventory.resources
            )
        )
    )
    lines.extend(("", "## Current Capability Assessments"))
    lines.extend(
        bullets(
            tuple(
                f"{item.capability_id}: {item.state.value} — {item.rationale}"
                for item in analysis.assessments
            )
        )
    )
    lines.extend(("", "## Capability Matrix", render_current_capability_matrix(analysis).rstrip()))
    lines.extend(("", "## Established Gaps"))
    lines.extend(
        bullets(
            tuple(
                f"{item.capability_id} [{item.gap_type.value}]: {item.description}"
                for item in analysis.gaps
                if item.gap_type is not GapType.EVIDENCE_GAP
            )
        )
    )
    lines.extend(("", "## Partial Capabilities"))
    lines.extend(
        bullets(
            tuple(
                f"{capabilities[item.capability_id].name}: Further investigation required."
                for item in analysis.partial_capabilities
            )
        )
    )
    lines.extend(("", "## Unknown Capabilities"))
    lines.extend(
        bullets(
            tuple(capabilities[item.capability_id].name for item in analysis.unknown_capabilities)
        )
    )
    lines.extend(("", "## Evidence Gaps"))
    lines.extend(
        bullets(
            tuple(
                f"{item.capability_id}: {item.missing_evidence}"
                for item in analysis.assessments
                if item.missing_evidence is not None
            )
        )
    )
    lines.extend(("", "## Existing Resources Requiring Further Investigation"))
    lines.extend(
        bullets(
            tuple(
                f"{item.name}: {item.investigation_question}"
                for item in analysis.inventory.resources
                if item.investigation_question is not None
            )
        )
    )
    lines.extend(("", "## Follow-Up Questions"))
    lines.extend(bullets(analysis.follow_up_questions))
    lines.extend(("", "## Traceability"))
    requirement_by_capability: dict[str, list[str]] = {}
    for link in analysis.required.capability_map.links:
        requirement_by_capability.setdefault(link.capability_id, []).append(link.requirement_id)
    requirements = {
        item.identifier: item for item in analysis.required.requirement_set.requirements
    }
    roles = {item.identifier: item.name for item in analysis.required.stakeholder_map.roles}
    for item in analysis.assessments:
        for requirement_id in requirement_by_capability.get(item.capability_id, []):
            requirement = requirements[requirement_id]
            sources = (
                ", ".join(
                    f"{identifier} ({evidence[identifier].source})"
                    for identifier in item.evidence_ids
                    if identifier in evidence
                )
                or "No assessment evidence"
            )
            current = (
                ", ".join(resources[identifier].name for identifier in item.current_resource_ids)
                or "No evidenced resource"
            )
            lines.append(
                f"- {sources} → {roles[requirement.stakeholder_id]} → {requirement_id} → "
                f"{item.capability_id} → {current} → {item.state.value} → "
                f"{item.gap_type.value if item.gap_type else 'No established gap'}"
            )
    lines.extend(
        (
            "",
            "## Educational Limitations",
            "- UNKNOWN is not NOT_AVAILABLE; insufficient evidence is not evidence of absence.",
            "- A resource is not automatically a capability, and technical features are not "
            "assumed to be configured or used.",
            "- Before proposing technology, investigate existing resources, configuration, "
            "process, and training.",
            "- A gap does not recommend replacement, a product, a vendor, architecture, or "
            "build-versus-buy. Solution approaches belong in Chapter 8.",
            "",
            "## Mermaid Diagram",
            "```mermaid",
            render_gap_mermaid().rstrip(),
            "```",
        )
    )
    return "\n".join(lines) + "\n"
