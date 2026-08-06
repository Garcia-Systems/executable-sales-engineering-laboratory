"""Markdown report generation for a validated current-state process."""

from sales_lab.services.business_process import ProcessModel

LIMITATIONS = (
    "This model describes only the documented current state.",
    "Unknown information remains explicit; no undocumented activity is inferred.",
    "No future state, software recommendation, prioritization, architecture, ROI, or outcome is "
    "provided.",
)


def render_business_process_report(model: ProcessModel) -> str:
    """Render the fixed Chapter 3 report sections in stable order."""
    process = model.process
    actor_by_id = {actor.identifier: actor.name for actor in process.actors}

    def actor_name(actor_id: str | None) -> str:
        return (
            actor_by_id.get(actor_id, "Unknown/not documented")
            if actor_id
            else "Unknown/not documented"
        )

    sections = (
        ("Process Purpose", (process.purpose,)),
        ("Actors", tuple(actor.name for actor in process.actors) or ("None documented.",)),
        (
            "Workflow Steps",
            tuple(
                f"{index}. {step.description} — Actor: "
                f"{actor_name(step.actor_id)}" + (" [UNKNOWN]" if step.is_unknown else "")
                for index, step in enumerate(model.ordered_steps, 1)
            ),
        ),
        (
            "Information Artifacts",
            tuple(
                f"{artifact.name} — used at: {', '.join(artifact.used_at_step_ids)}"
                for artifact in process.artifacts
            )
            or ("None documented.",),
        ),
        (
            "Decision Points",
            tuple(f"{item.question} (step: {item.step_id})" for item in process.decisions)
            or ("None documented.",),
        ),
        (
            "Known Gaps",
            tuple(
                f"Transition after '{item.source_step_id}' has no documented destination."
                for item in model.incomplete_transitions
            )
            or ("None recorded.",),
        ),
        (
            "Unknown Areas",
            tuple(step.description for step in model.unknown_steps) or ("None recorded.",),
        ),
        ("Educational Limitations", LIMITATIONS),
    )
    lines = ["# Current-State Business Process"]
    for heading, items in sections:
        lines.extend(("", f"## {heading}"))
        lines.extend(f"- {item}" for item in items)
    return "\n".join(lines) + "\n"
