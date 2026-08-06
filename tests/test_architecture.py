"""Chapter 9 logical architecture, traceability, validation, and experiments."""

from dataclasses import FrozenInstanceError, replace

import pytest

from sales_lab.diagrams.architecture import (
    render_architecture_comparison_mermaid,
    render_architecture_mermaid,
)
from sales_lab.domain.architecture import (
    ArchitectureComponent,
    BoundaryPosition,
    ComponentType,
)
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_architectures,
    harbor_street_music_capability_map,
    harbor_street_music_current_capability_inventory,
    harbor_street_music_requirements,
    harbor_street_music_solution_options,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.architecture import render_architecture_report
from sales_lab.services.approaches import analyze_solution_approaches
from sales_lab.services.architecture import (
    ArchitectureAnalysis,
    add_components,
    analyze_architectures,
    remove_component,
    unknown_dependencies,
    validate_architecture,
)
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.gaps import analyze_gaps


def canonical_analysis() -> ArchitectureAnalysis:
    """Compose established Chapters 4-9 objects rather than copied labels."""
    required = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    gaps = analyze_gaps(required, harbor_street_music_current_capability_inventory())
    approaches = analyze_solution_approaches(gaps, harbor_street_music_solution_options())
    return analyze_architectures(approaches, harbor_street_music_architectures())


def test_models_are_immutable_and_classify_components_boundaries_and_actors() -> None:
    """Frozen models explicitly separate logical responsibility and boundary position."""
    architecture = canonical_analysis().validations[0].architecture
    with pytest.raises(FrozenInstanceError):
        architecture.name = "Winner"  # type: ignore[misc]
    assert architecture.components[0].component_type is ComponentType.USER_INTERFACE
    assert architecture.components[0].boundary is BoundaryPosition.INSIDE
    assert architecture.components[3].boundary is BoundaryPosition.EXTERNAL
    assert tuple(item.stakeholder_id for item in architecture.actors) == (
        "prospective-student",
        "staff",
        "instructor",
    )


def test_connections_flows_traceability_coverage_and_order_are_explicit() -> None:
    """Authored ordering and Chapter 5/6 links survive validation unchanged."""
    analysis = canonical_analysis()
    first = analysis.validations[0]
    assert tuple(item.identifier for item in first.architecture.connections) == tuple(
        f"CON-{number:03}" for number in range(1, 8)
    )
    assert first.architecture.information_flows[0].information == "Lesson Inquiry"
    assert first.uncovered_capabilities == ()
    assert first.unjustified_components == ()
    assert first.disconnected_components == ()
    assert tuple(item.subject_id for item in first.unknown_dependencies) == ("DEP-CALENDAR",)
    assert unknown_dependencies(first.architecture.dependencies) == first.architecture.dependencies
    assert first.architecture.components[1].capability_ids == ("CAP-001", "CAP-003")
    assert first.architecture.approach_ids == ("APP-001", "APP-002", "APP-003")


def test_overengineering_experiment_is_unjustified_and_immutable() -> None:
    """Sophistication is not quality when no traceable reason exists."""
    analysis = canonical_analysis()
    original = analysis.validations[0].architecture
    additions = (
        ArchitectureComponent(
            "CMP-ML",
            "Machine Learning Recommendation Engine",
            ComponentType.WORKFLOW,
            BoundaryPosition.INSIDE,
        ),
        ArchitectureComponent(
            "CMP-STREAM",
            "Real-Time Analytics Pipeline",
            ComponentType.REPORTING,
            BoundaryPosition.INSIDE,
        ),
    )
    experiment = add_components(original, additions)
    result = validate_architecture(analysis.approach_analysis, experiment)
    assert tuple(item.subject_id for item in result.unjustified_components) == (
        "CMP-ML",
        "CMP-STREAM",
    )
    assert len(original.components) + 2 == len(experiment.components)
    assert all(item.identifier not in {"CMP-ML", "CMP-STREAM"} for item in original.components)


def test_missing_capability_experiment_preserves_original() -> None:
    """Removing sole CAP-004 support exposes completeness without mutation."""
    analysis = canonical_analysis()
    original = analysis.validations[0].architecture
    experiment = remove_component(original, "CMP-EVALUATION")
    result = validate_architecture(analysis.approach_analysis, experiment)
    assert tuple(item.subject_id for item in result.uncovered_capabilities) == ("CAP-004",)
    assert any(item.identifier == "CMP-EVALUATION" for item in original.components)
    assert all(item.identifier != "CMP-EVALUATION" for item in experiment.components)


def test_validation_rejects_invalid_references_and_identifiers() -> None:
    """Missing endpoints, links, flows, approaches, and duplicates fail clearly."""
    analysis = canonical_analysis()
    architecture = analysis.validations[0].architecture
    component = architecture.components[0]
    cases = (
        (replace(architecture, engagement="Other"), "same engagement"),
        (replace(architecture, approach_ids=("APP-404",)), "unknown approach"),
        (replace(architecture, components=(component, component)), "identifiers"),
        (replace(architecture, components=(replace(component, identifier=" "),)), "identifiers"),
        (
            replace(
                architecture,
                components=(
                    replace(component, capability_ids=("CAP-404",)),
                    *architecture.components[1:],
                ),
            ),
            "unknown capability",
        ),
        (
            replace(
                architecture,
                components=(
                    replace(component, requirement_ids=("REQ-404",)),
                    *architecture.components[1:],
                ),
            ),
            "unknown requirement",
        ),
        (
            replace(
                architecture,
                connections=(replace(architecture.connections[0], destination_id="CMP-404"),),
            ),
            "missing component",
        ),
        (
            replace(
                architecture, connections=(architecture.connections[0], architecture.connections[0])
            ),
            "connection identifiers",
        ),
        (
            replace(
                architecture,
                information_flows=(
                    replace(architecture.information_flows[0], connection_id="CON-404"),
                ),
            ),
            "missing connection",
        ),
    )
    for candidate, message in cases:
        with pytest.raises(ValueError, match=message):
            validate_architecture(analysis.approach_analysis, candidate)
    with pytest.raises(ValueError, match="architecture identifiers"):
        analyze_architectures(analysis.approach_analysis, (architecture, architecture))


def test_mermaid_comparison_adr_and_report_are_deterministic_and_neutral() -> None:
    """Generated views contain structured facts but no implementation leap or winner."""
    analysis = canonical_analysis()
    first = analysis.validations[0].architecture
    diagram = render_architecture_mermaid(first)
    assert diagram.startswith("flowchart LR")
    assert "interface not yet established" in diagram
    comparison = render_architecture_comparison_mermaid(
        tuple(item.architecture for item in analysis.validations)
    )
    assert "Compare, do not rank" in comparison
    report = render_architecture_report(analysis)
    assert render_architecture_report(analysis) == report
    for heading in (
        "Engagement",
        "Architecture Goals",
        "Architecture Boundaries",
        "Actors",
        "Candidate Architectures",
        "Architecture Components",
        "Information Flows",
        "Capability Coverage",
        "Requirement Traceability",
        "Architecture Decisions",
        "Assumptions",
        "Unknown Dependencies",
        "Uncovered Capabilities",
        "Unjustified Components",
        "Architecture Comparison",
        "Open Technical Questions",
        "Educational Limitations",
    ):
        assert f"## {heading}" in report
    assert "ADR-001" in report
    assert "Candidate architecture decision" in report
    assert "E2 → staff → REQ-001 → CAP-001" in report
    for forbidden in (
        "recommended architecture",
        "winning architecture",
        "aws",
        "kubernetes",
        "rest api",
        "architecture score",
    ):
        assert forbidden not in report.lower()
