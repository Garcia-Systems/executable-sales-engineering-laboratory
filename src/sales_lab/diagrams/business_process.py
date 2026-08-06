"""Deterministic Mermaid rendering for validated current-state processes."""

from sales_lab.services.business_process import ProcessModel


def render_process_mermaid(model: ProcessModel) -> str:
    """Render recorded nodes and transitions without supplying missing information."""
    decision_ids = {decision.step_id for decision in model.process.decisions}
    aliases = {step.identifier: f"S{index}" for index, step in enumerate(model.ordered_steps, 1)}
    lines = ["flowchart TD"]
    for step in model.ordered_steps:
        alias = aliases[step.identifier]
        label = f"Unknown: {step.description}" if step.is_unknown else step.description
        brackets = ("{", "}") if step.identifier in decision_ids else ("[", "]")
        lines.append(f"    {alias}{brackets[0]}{label}{brackets[1]}")
    unknown_index = 0
    for transition in model.process.transitions:
        source = aliases[transition.source_step_id]
        if transition.target_step_id is None:
            unknown_index += 1
            target = f"U{unknown_index}"
            lines.append(f"    {target}[Unknown transition]")
        else:
            target = aliases[transition.target_step_id]
        arrow = f" -->|{transition.label}| " if transition.label else " --> "
        lines.append(f"    {source}{arrow}{target}")
    return "\n".join(lines) + "\n"
