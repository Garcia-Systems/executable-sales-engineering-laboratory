"""Tests for immutable, deterministic current-state process modeling."""

from dataclasses import FrozenInstanceError, replace

import pytest

from sales_lab.diagrams.business_process import render_process_mermaid
from sales_lab.domain.business_process import (
    BusinessProcess,
    DecisionPoint,
    InformationArtifact,
    ProcessActor,
    ProcessBoundary,
    ProcessStep,
    WorkflowTransition,
)
from sales_lab.examples.harbor_street_music import harbor_street_music_business_process
from sales_lab.reports.business_process import render_business_process_report
from sales_lab.services.business_process import ProcessValidationError, validate_business_process


def test_workflow_objects_are_immutable_and_preserve_sequence() -> None:
    """Frozen objects retain exactly the documented sequence."""
    process = harbor_street_music_business_process()
    model = validate_business_process(process)
    assert tuple(step.identifier for step in model.ordered_steps) == (
        "inquiry",
        "spreadsheet",
        "review",
        "contact",
        "decision",
        "calendar",
        "declined-unknown",
    )
    with pytest.raises(FrozenInstanceError):
        process.name = "Changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: ProcessActor("", "Staff"), "actor identifier must not be blank"),
        (lambda: ProcessActor("staff", " "), "actor name must not be blank"),
        (lambda: ProcessStep("", "Work"), "step identifier must not be blank"),
        (lambda: ProcessStep("step", ""), "step description must not be blank"),
        (lambda: DecisionPoint("", "Question?"), "decision step_id must not be blank"),
        (lambda: DecisionPoint("step", " "), "decision question must not be blank"),
        (lambda: InformationArtifact("", "Record", ()), "artifact identifier must not be blank"),
        (lambda: InformationArtifact("record", "", ()), "artifact name must not be blank"),
        (lambda: WorkflowTransition("", "target"), "transition source_step_id must not be blank"),
        (lambda: WorkflowTransition("source", "target", " "), "transition label must not be blank"),
    ],
)
def test_concepts_reject_blank_intrinsic_text(factory: object, message: str) -> None:
    """Each small domain concept rejects unusable intrinsic text."""
    with pytest.raises(ValueError, match=message):
        factory()  # type: ignore[operator]


def test_process_rejects_blank_name_and_purpose() -> None:
    """The aggregate requires a stated name and purpose."""
    process = harbor_street_music_business_process()
    with pytest.raises(ValueError, match="process name must not be blank"):
        replace(process, name="")
    with pytest.raises(ValueError, match="process purpose must not be blank"):
        replace(process, purpose=" ")


def test_boundaries_and_unknown_branch_are_derived_without_inference() -> None:
    """The validated model exposes its documented start, ends, and explicit unknown."""
    model = validate_business_process(harbor_street_music_business_process())
    assert model.start_step.identifier == "inquiry"
    assert tuple(step.identifier for step in model.terminal_steps) == (
        "calendar",
        "declined-unknown",
    )
    assert tuple(step.identifier for step in model.unknown_steps) == ("declined-unknown",)
    assert model.incomplete_transitions == ()


def test_mermaid_is_deterministic_and_marks_decisions_and_unknowns() -> None:
    """Mermaid aliases follow tuple order and do not conceal missing evidence."""
    model = validate_business_process(harbor_street_music_business_process())
    first = render_process_mermaid(model)
    assert first == render_process_mermaid(model)
    assert "S5{Student accepts or declines}" in first
    assert "S5 -->|Accepts| S6" in first
    assert "S5 -->|Declines| S7" in first
    assert "S7[Unknown: What happens after the student declines is not documented]" in first


def test_report_has_required_sections_and_evidence_boundaries() -> None:
    """The report clearly separates the documented workflow from unknown information."""
    report = render_business_process_report(
        validate_business_process(harbor_street_music_business_process())
    )
    assert report.startswith("# Current-State Business Process")
    for heading in (
        "Process Purpose",
        "Actors",
        "Workflow Steps",
        "Information Artifacts",
        "Decision Points",
        "Known Gaps",
        "Unknown Areas",
        "Educational Limitations",
    ):
        assert f"## {heading}" in report
    assert "Unknown/not documented [UNKNOWN]" in report
    assert "No future state, software recommendation" in report


def test_incomplete_unknown_transition_is_visible_in_diagram_and_report() -> None:
    """A permitted unknown destination becomes a visible gap instead of a guessed node."""
    process = harbor_street_music_business_process()
    process = replace(
        process,
        transitions=(*process.transitions, WorkflowTransition("decision", None, is_unknown=True)),
    )
    model = validate_business_process(process)
    assert len(model.incomplete_transitions) == 1
    assert "U1[Unknown transition]" in render_process_mermaid(model)
    assert "S5 --> U1" in render_process_mermaid(model)
    assert "has no documented destination" in render_business_process_report(model)


def test_report_empty_collection_fallbacks_are_explicit() -> None:
    """Optional documented collections render transparent empty states."""
    process = BusinessProcess(
        "Minimal",
        "Observe a single bounded activity.",
        (),
        (ProcessStep("only", "Observed activity"),),
        (),
        (),
        ProcessBoundary("only", ("only",)),
        (),
    )
    report = render_business_process_report(validate_business_process(process))
    documented_fallback_count = 3
    recorded_fallback_count = 2
    assert report.count("None documented.") == documented_fallback_count
    assert report.count("None recorded.") == recorded_fallback_count


def test_validation_collects_duplicate_reference_and_boundary_errors() -> None:
    """Learners receive friendly messages for all independently visible defects."""
    process = BusinessProcess(
        "Invalid",
        "Exercise validation.",
        (ProcessActor("same", "One"), ProcessActor("same", "Two")),
        (
            ProcessStep("duplicate", "First", "missing-actor"),
            ProcessStep("duplicate", "Second"),
        ),
        (DecisionPoint("missing-decision", "Known?"),),
        (
            InformationArtifact("same-artifact", "One", ("missing-artifact-step",)),
            InformationArtifact("same-artifact", "Two", ()),
        ),
        ProcessBoundary("missing-start", ("missing-terminal",)),
        (
            WorkflowTransition("missing-source", "duplicate"),
            WorkflowTransition("duplicate", "missing-target"),
            WorkflowTransition("duplicate", None),
        ),
    )
    with pytest.raises(ProcessValidationError) as error:
        validate_business_process(process)
    text = str(error.value)
    assert error.value.messages
    for expected in (
        "Duplicate step identifier(s): duplicate.",
        "Duplicate actor identifier(s): same.",
        "Duplicate artifact identifier(s): same-artifact.",
        "Start step 'missing-start'",
        "Terminal step 'missing-terminal'",
        "unknown actor 'missing-actor'",
        "Artifact 'same-artifact' references unknown step",
        "Decision references unknown step",
        "Transition source 'missing-source'",
        "Transition target 'missing-target'",
        "has no target; mark it unknown",
    ):
        assert expected in text


def test_validation_detects_missing_boundaries_and_unreachable_step() -> None:
    """Missing boundary values and disconnected recorded work are rejected."""
    base = harbor_street_music_business_process()
    with pytest.raises(ProcessValidationError, match="A process start step is required"):
        validate_business_process(replace(base, boundary=ProcessBoundary(None, ())))
    disconnected = replace(
        base,
        transitions=tuple(
            item for item in base.transitions if item.target_step_id != "spreadsheet"
        ),
    )
    with pytest.raises(ProcessValidationError, match=r"Unreachable step\(s\): spreadsheet"):
        validate_business_process(disconnected)


def test_validation_detects_order_cycle_and_terminal_outgoing_transition() -> None:
    """Unsupported backward edges reveal ordering, cycle, and terminal defects."""
    base = harbor_street_music_business_process()
    broken = replace(
        base,
        transitions=(*base.transitions, WorkflowTransition("calendar", "inquiry")),
    )
    with pytest.raises(ProcessValidationError) as error:
        validate_business_process(broken)
    text = str(error.value)
    assert "does not follow the recorded step order" in text
    assert "Circular workflow references are not supported" in text
    assert "Terminal step 'calendar' must not have outgoing transitions" in text
