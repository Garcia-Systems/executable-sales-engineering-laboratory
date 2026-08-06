"""Mermaid generation from structured Chapter 9 architecture data."""

import re

from sales_lab.domain.architecture import DependencyState, SolutionArchitecture


def _alias(identifier: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", identifier)


def render_architecture_mermaid(architecture: SolutionArchitecture) -> str:
    """Render components, actors, and information flows in authored order."""
    names = {item.identifier: item.name for item in architecture.actors}
    names.update({item.identifier: item.name for item in architecture.components})
    lines = ["flowchart LR"]
    lines.extend(f"    {_alias(actor.identifier)}([{actor.name}])" for actor in architecture.actors)
    lines.extend(
        f"    {_alias(component.identifier)}[{component.name}]"
        for component in architecture.components
    )
    connections = {item.identifier: item for item in architecture.connections}
    dependencies = {item.identifier: item for item in architecture.dependencies}
    for flow in architecture.information_flows:
        connection = connections[flow.connection_id]
        unknown = (
            flow.dependency_id is not None
            and dependencies[flow.dependency_id].state is DependencyState.UNKNOWN
        )
        arrow = "-.->" if unknown else "-->"
        label = flow.information
        if unknown:
            label += " (interface not yet established)"
        lines.append(
            f"    {_alias(connection.source_id)} {arrow}|{label}| "
            f"{_alias(connection.destination_id)}"
        )
    return "\n".join(lines) + "\n"


def render_architecture_comparison_mermaid(
    architectures: tuple[SolutionArchitecture, ...],
) -> str:
    """Show candidates side by side without winner or recommendation semantics."""
    lines = ["flowchart LR"]
    lines.extend(
        f"    {_alias(architecture.identifier)}[{architecture.name}]"
        for architecture in architectures
    )
    if len(architectures) > 1:
        lines.append(
            f"    {_alias(architectures[0].identifier)} ---|Compare, do not rank| "
            f"{_alias(architectures[1].identifier)}"
        )
    return "\n".join(lines) + "\n"
