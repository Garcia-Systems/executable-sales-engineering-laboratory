"""Deterministic Chapter 8 comparison matrix and Markdown report."""

from sales_lab.diagrams.approaches import render_approach_mermaid
from sales_lab.services.approaches import SolutionApproachAnalysis


def render_approach_comparison_matrix(analysis: SolutionApproachAnalysis) -> str:
    """Render authored facts without scores, totals, rankings, or a winner."""
    rows = [
        (
            "| Approach | Existing Tools | New Software | Custom Development | "
            "Feasibility | Evidence Needed |"
        ),
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in analysis.approaches:
        evidence = "; ".join(item.evidence_needs) or "None recorded"
        rows.append(
            f"| {item.name} | {item.uses_existing_tools} | {item.needs_new_software} | "
            f"{item.needs_custom_development} | {item.feasibility.value} | {evidence} |"
        )
    return "\n".join(rows) + "\n"


def render_solution_approach_report(analysis: SolutionApproachAnalysis) -> str:
    """Render the complete educational analysis in deterministic authored order."""
    capabilities = {
        item.identifier: item.name
        for item in analysis.gap_analysis.required.capability_map.capabilities
    }

    def bullets(items: tuple[str, ...]) -> list[str]:
        return [f"- {item}" for item in (items or ("None.",))]

    lines = ["# Solution Approach Analysis", "", "## Engagement"]
    lines.extend(bullets((analysis.option_set.engagement,)))
    lines.extend(("", "## Established Capability Gaps"))
    lines.extend(
        bullets(
            tuple(
                f"{item.capability_id} ({capabilities[item.capability_id]}): {item.description}"
                for item in analysis.gap_analysis.gaps
            )
        )
    )
    lines.extend(("", "## Candidate Solution Approaches"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {item.name} [{item.approach_type.value}] — {item.description}"
                for item in analysis.approaches
            )
        )
    )
    lines.extend(("", "## Gap-to-Approach Traceability"))
    lines.extend(
        bullets(
            tuple(
                f"{gap_id} ({capabilities.get(gap_id, 'No established gap')}) → "
                f"{item.identifier} ({item.name})"
                for item in analysis.approaches
                for gap_id in (item.gap_capability_ids or ("NONE",))
            )
        )
    )
    lines.extend(("", "## Assumptions"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {assumption.statement} Evidence: {assumption.evidence}. "
                f"Status: {assumption.status.value}."
                for item in analysis.approaches
                for assumption in item.assumptions
            )
        )
    )
    lines.extend(("", "## Constraints"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: REQ-003 — No software budget has yet been approved; "
                "this affects evaluation but does not automatically eliminate the approach."
                for item in analysis.approaches
                if "REQ-003" in item.constraint_requirement_ids
            )
        )
    )
    lines.extend(("", "## Tradeoffs"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {tradeoff.dimension.value} = {tradeoff.state.value} — "
                f"{tradeoff.rationale}"
                for item in analysis.approaches
                for tradeoff in item.tradeoffs
            )
        )
    )
    lines.extend(("", "## Feasibility"))
    lines.extend(
        bullets(
            tuple(f"{item.identifier}: {item.feasibility.value}" for item in analysis.approaches)
        )
    )
    lines.extend(("", "## Evidence Still Required"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: {need}"
                for item in analysis.approaches
                for need in item.evidence_needs
            )
        )
    )
    lines.extend(("", "## Unsupported Approaches"))
    lines.extend(
        bullets(
            tuple(
                f"{item.identifier}: Unsupported solution approach. No established capability "
                "gap currently justifies this approach."
                for item in analysis.unsupported_approaches
            )
        )
    )
    lines.extend(("", "## Comparison Matrix", render_approach_comparison_matrix(analysis).rstrip()))
    status_quo = tuple(
        item for item in analysis.approaches if item.approach_type.value == "Status Quo"
    )
    lines.extend(("", "## Status Quo"))
    lines.extend(
        bullets(
            tuple(
                f"{item.name}: {item.description} Its consequences require evaluation alongside "
                "the costs and risks of change."
                for item in status_quo
            )
        )
    )
    lines.extend(("", "## Open Questions"))
    lines.extend(bullets(analysis.option_set.open_questions))
    lines.extend(
        (
            "",
            "## Educational Limitations",
            "- These categories are an educational heuristic, not a universal industry taxonomy.",
            (
                "- Candidates are alternatives, not recommendations; no fit score, ranking, "
                "winner, vendor, cost, ROI, or architecture is produced."
            ),
            (
                "- Technical feasibility not yet established means validation is needed; "
                "UNKNOWN is not NOT_FEASIBLE."
            ),
            "- Capability first. Approach second. Product later.",
            "",
            "## Mermaid Diagram",
            "```mermaid",
            render_approach_mermaid().rstrip(),
            "```",
        )
    )
    return "\n".join(lines) + "\n"
