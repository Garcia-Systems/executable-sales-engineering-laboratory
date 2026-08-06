"""Markdown and matrix presentation for validated stakeholder analysis."""

from sales_lab.diagrams.stakeholders import render_stakeholder_mermaid
from sales_lab.domain.stakeholders import ResponsibilityCategory
from sales_lab.services.stakeholders import StakeholderAnalysis, authority_for

MATRIX_CATEGORIES = (
    ResponsibilityCategory.PERFORMS_WORK,
    ResponsibilityCategory.OWNS_OUTCOME,
    ResponsibilityCategory.APPROVES_CHANGE,
    ResponsibilityCategory.USES_SYSTEM,
    ResponsibilityCategory.AFFECTED_BY_CHANGE,
)


def render_responsibility_matrix(analysis: StakeholderAnalysis) -> str:
    """Render evidence-dependent categories without forcing binary answers."""
    stakeholder_map = analysis.stakeholder_map
    headings = ("Stakeholder", *(category.value for category in MATRIX_CATEGORIES))
    lines = ("| " + " | ".join(headings) + " |", "| " + " | ".join("---" for _ in headings) + " |")
    rows: list[str] = list(lines)
    for role in stakeholder_map.roles:
        established = {
            item.category
            for item in stakeholder_map.responsibilities
            if item.role_id == role.identifier
        }
        values: list[str] = []
        for category in MATRIX_CATEGORIES:
            if category is ResponsibilityCategory.APPROVES_CHANGE:
                values.append(authority_for(analysis, role).value)
            else:
                values.append("Established" if category in established else "Not Established")
        rows.append("| " + " | ".join((role.name, *values)) + " |")
    return "\n".join(rows) + "\n"


def render_stakeholder_report(analysis: StakeholderAnalysis) -> str:
    """Render the Chapter 4 report with a fixed, auditable section order."""
    stakeholder_map = analysis.stakeholder_map
    role_names = {role.identifier: role.name for role in stakeholder_map.roles}
    evidence = {item.identifier: item for item in stakeholder_map.evidence}
    step_names = {step.identifier: step.description for step in analysis.process.steps}
    sections: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("Engagement", (stakeholder_map.engagement,)),
        ("Stakeholder Roles", tuple(role.name for role in stakeholder_map.roles)),
        (
            "Responsibilities",
            tuple(
                f"{role_names[item.role_id]} — {item.category.value} (evidence: {item.evidence_id})"
                for item in stakeholder_map.responsibilities
            ),
        ),
        (
            "Process Participation",
            tuple(
                f"{role_names[item.role_id]} — {step_names[item.step_id]} "
                f"(step: {item.step_id}; evidence: {item.evidence_id})"
                for item in stakeholder_map.participations
            ),
        ),
        (
            "Decision Authority",
            tuple(
                f"{role_names[item.role_id]} — {item.decision}: {item.state.value} "
                f"(evidence: {item.evidence_id})"
                for item in stakeholder_map.authority
            ),
        ),
        (
            "Stakeholder Relationships",
            tuple(
                f"{role_names[item.source_role_id]} → {role_names[item.target_role_id]}: "
                f"{item.description} (evidence: {item.evidence_id})"
                for item in stakeholder_map.relationships
            ),
        ),
        (
            "Evidence",
            tuple(
                f"{item.identifier}: {item.statement} — Source: {item.source}"
                for item in evidence.values()
            ),
        ),
        ("Missing Perspectives", tuple(item.description for item in analysis.missing_perspectives)),
        ("Follow-Up Questions", analysis.follow_up_questions),
        (
            "Educational Limitations",
            (
                "Roles, relationships, responsibilities, evidence, and unknowns are documented; "
                "stakeholders are not scored or ranked.",
                "The analysis describes the current process and people involved; it does not "
                "define requirements or design a solution.",
            ),
        ),
    )
    lines = ["# Stakeholder Analysis"]
    for heading, items in sections:
        lines.extend(("", f"## {heading}"))
        lines.extend(f"- {item}" for item in (items or ("None established.",)))
    lines.extend(
        (
            "",
            "## Stakeholder Responsibility Matrix",
            render_responsibility_matrix(analysis).rstrip(),
            "",
            "## Mermaid Diagram",
            "```mermaid",
            render_stakeholder_mermaid(analysis).rstrip(),
            "```",
        )
    )
    return "\n".join(lines) + "\n"
