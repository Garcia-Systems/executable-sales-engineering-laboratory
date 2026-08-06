"""Immutable concepts used to describe a documented current-state process."""

from dataclasses import dataclass


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        msg = f"{field_name} must not be blank"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ProcessActor:
    """A documented participant in the workflow."""

    identifier: str
    name: str

    def __post_init__(self) -> None:
        """Require usable identifiers and labels."""
        _require_text(self.identifier, "actor identifier")
        _require_text(self.name, "actor name")


@dataclass(frozen=True, slots=True)
class ProcessStep:
    """One activity, or an explicit placeholder for an unknown activity."""

    identifier: str
    description: str
    actor_id: str | None = None
    is_unknown: bool = False

    def __post_init__(self) -> None:
        """Require a stable identifier and visible description."""
        _require_text(self.identifier, "step identifier")
        _require_text(self.description, "step description")


@dataclass(frozen=True, slots=True)
class DecisionPoint:
    """A documented choice attached to one workflow step."""

    step_id: str
    question: str

    def __post_init__(self) -> None:
        """Require the referenced step and documented question."""
        _require_text(self.step_id, "decision step_id")
        _require_text(self.question, "decision question")


@dataclass(frozen=True, slots=True)
class InformationArtifact:
    """Information read, created, or updated during the process."""

    identifier: str
    name: str
    used_at_step_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        """Require a stable identifier and visible name."""
        _require_text(self.identifier, "artifact identifier")
        _require_text(self.name, "artifact name")


@dataclass(frozen=True, slots=True)
class ProcessBoundary:
    """Documented start and terminal steps delimiting the model."""

    start_step_id: str | None
    terminal_step_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WorkflowTransition:
    """A directed, documented connection between workflow steps."""

    source_step_id: str
    target_step_id: str | None
    label: str | None = None
    is_unknown: bool = False

    def __post_init__(self) -> None:
        """Require a source; incomplete targets are validated by the service."""
        _require_text(self.source_step_id, "transition source_step_id")
        if self.label is not None:
            _require_text(self.label, "transition label")


@dataclass(frozen=True, slots=True)
class BusinessProcess:
    """An evidence-bounded current-state workflow in recorded sequence."""

    name: str
    purpose: str
    actors: tuple[ProcessActor, ...]
    steps: tuple[ProcessStep, ...]
    decisions: tuple[DecisionPoint, ...]
    artifacts: tuple[InformationArtifact, ...]
    boundary: ProcessBoundary
    transitions: tuple[WorkflowTransition, ...]

    def __post_init__(self) -> None:
        """Require only intrinsic text; relationship checks belong to the service."""
        _require_text(self.name, "process name")
        _require_text(self.purpose, "process purpose")
