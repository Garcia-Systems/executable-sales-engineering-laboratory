"""Deterministic Mermaid generation from the structured stakeholder map."""

from sales_lab.services.stakeholders import StakeholderAnalysis


def render_stakeholder_mermaid(analysis: StakeholderAnalysis) -> str:
    """Render roles and their evidenced relationships in recorded order."""
    roles = analysis.stakeholder_map.roles
    aliases = {role.identifier: f"R{index}" for index, role in enumerate(roles, 1)}
    lines = ["flowchart LR"]
    lines.extend(f"    {aliases[role.identifier]}[{role.name}]" for role in roles)
    for relationship in analysis.stakeholder_map.relationships:
        arrow = " -.->" if relationship.is_unknown else " -->"
        lines.append(
            f"    {aliases[relationship.source_role_id]}{arrow}|{relationship.description}| "
            f"{aliases[relationship.target_role_id]}"
        )
    return "\n".join(lines) + "\n"
