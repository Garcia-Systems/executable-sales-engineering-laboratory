"""Deterministic validation and summarization of current-state processes."""

# Relationship validation is intentionally centralized so learners can step through every check.
# ruff: noqa: C901, PERF401, PLR0912, PLR0915

from dataclasses import dataclass

from sales_lab.domain.business_process import BusinessProcess, ProcessStep, WorkflowTransition


class ProcessValidationError(ValueError):
    """Report all detected workflow problems in learner-friendly language."""

    def __init__(self, messages: tuple[str, ...]) -> None:
        """Retain individual messages as well as a readable combined message."""
        self.messages = messages
        super().__init__("Workflow validation failed:\n- " + "\n- ".join(messages))


@dataclass(frozen=True, slots=True)
class ProcessModel:
    """A validated process plus deterministic derived observations."""

    process: BusinessProcess
    ordered_steps: tuple[ProcessStep, ...]
    start_step: ProcessStep
    terminal_steps: tuple[ProcessStep, ...]
    incomplete_transitions: tuple[WorkflowTransition, ...]
    unknown_steps: tuple[ProcessStep, ...]


def _duplicates(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return tuple(duplicates)


def _has_cycle(step_ids: tuple[str, ...], transitions: tuple[WorkflowTransition, ...]) -> bool:
    edges: dict[str, list[str]] = {step_id: [] for step_id in step_ids}
    for transition in transitions:
        if transition.source_step_id in edges and transition.target_step_id in edges:
            edges[transition.source_step_id].append(transition.target_step_id)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(step_id: str) -> bool:
        if step_id in visiting:
            return True
        if step_id in visited:
            return False
        visiting.add(step_id)
        if any(visit(target) for target in edges[step_id]):
            return True
        visiting.remove(step_id)
        visited.add(step_id)
        return False

    return any(visit(step_id) for step_id in step_ids)


def validate_business_process(process: BusinessProcess) -> ProcessModel:
    """Validate references, reachability, ordering, boundaries, and unknown gaps."""
    messages: list[str] = []
    step_ids = tuple(step.identifier for step in process.steps)
    actor_ids = tuple(actor.identifier for actor in process.actors)
    artifact_ids = tuple(artifact.identifier for artifact in process.artifacts)
    for kind, values in (("step", step_ids), ("actor", actor_ids), ("artifact", artifact_ids)):
        duplicates = _duplicates(values)
        if duplicates:
            messages.append(f"Duplicate {kind} identifier(s): {', '.join(duplicates)}.")

    known_steps = set(step_ids)
    known_actors = set(actor_ids)
    if process.boundary.start_step_id is None:
        messages.append("A process start step is required.")
    elif process.boundary.start_step_id not in known_steps:
        messages.append(
            f"Start step '{process.boundary.start_step_id}' does not reference a recorded step."
        )
    if not process.boundary.terminal_step_ids:
        messages.append("At least one terminal step is required.")
    for terminal_id in process.boundary.terminal_step_ids:
        if terminal_id not in known_steps:
            messages.append(f"Terminal step '{terminal_id}' does not reference a recorded step.")

    positions = {step_id: index for index, step_id in enumerate(step_ids)}
    for step in process.steps:
        if step.actor_id is not None and step.actor_id not in known_actors:
            messages.append(f"Step '{step.identifier}' references unknown actor '{step.actor_id}'.")
    for artifact in process.artifacts:
        for step_id in artifact.used_at_step_ids:
            if step_id not in known_steps:
                messages.append(
                    f"Artifact '{artifact.identifier}' references unknown step '{step_id}'."
                )
    for decision in process.decisions:
        if decision.step_id not in known_steps:
            messages.append(f"Decision references unknown step '{decision.step_id}'.")

    valid_edges: list[WorkflowTransition] = []
    for transition in process.transitions:
        source_known = transition.source_step_id in known_steps
        target_known = transition.target_step_id in known_steps
        if not source_known:
            messages.append(
                f"Transition source '{transition.source_step_id}' is not a recorded step."
            )
        if transition.target_step_id is None:
            if not transition.is_unknown:
                messages.append(
                    f"Transition from '{transition.source_step_id}' has no target; mark it unknown."
                )
        elif not target_known:
            messages.append(
                f"Transition target '{transition.target_step_id}' is not a recorded step."
            )
        if source_known and target_known:
            valid_edges.append(transition)
            target_id = transition.target_step_id
            if target_id is None:  # Defensive narrowing; target_known already excludes this case.
                continue
            if positions[transition.source_step_id] >= positions[target_id]:
                messages.append(
                    f"Transition '{transition.source_step_id}' to '{transition.target_step_id}' "
                    "does not follow the recorded step order."
                )

    if _has_cycle(step_ids, tuple(valid_edges)):
        messages.append("Circular workflow references are not supported.")

    start_id = process.boundary.start_step_id
    if start_id in known_steps:
        reachable = {start_id}
        changed = True
        while changed:
            changed = False
            for edge in valid_edges:
                if edge.source_step_id in reachable and edge.target_step_id not in reachable:
                    reachable.add(edge.target_step_id)  # type: ignore[arg-type]
                    changed = True
        unreachable = tuple(step_id for step_id in step_ids if step_id not in reachable)
        if unreachable:
            messages.append(f"Unreachable step(s): {', '.join(unreachable)}.")

    outgoing = {transition.source_step_id for transition in process.transitions}
    for terminal_id in process.boundary.terminal_step_ids:
        if terminal_id in outgoing:
            messages.append(f"Terminal step '{terminal_id}' must not have outgoing transitions.")
    if messages:
        raise ProcessValidationError(tuple(messages))

    step_by_id = {step.identifier: step for step in process.steps}
    return ProcessModel(
        process=process,
        ordered_steps=process.steps,
        start_step=step_by_id[process.boundary.start_step_id],  # type: ignore[index]
        terminal_steps=tuple(step_by_id[item] for item in process.boundary.terminal_step_ids),
        incomplete_transitions=tuple(
            transition for transition in process.transitions if transition.target_step_id is None
        ),
        unknown_steps=tuple(step for step in process.steps if step.is_unknown),
    )
