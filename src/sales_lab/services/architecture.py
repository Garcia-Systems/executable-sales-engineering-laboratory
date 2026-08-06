"""Deterministic Chapter 9 architecture validation and experiments."""

# Referential checks stay together so learners can step through one validation path.
# ruff: noqa: C901, EM101, EM102, TRY003

from dataclasses import dataclass, replace

from sales_lab.domain.architecture import (
    ArchitectureComponent,
    ArchitectureDependency,
    DependencyState,
    SolutionArchitecture,
)
from sales_lab.services.approaches import SolutionApproachAnalysis


@dataclass(frozen=True, slots=True)
class ArchitectureFinding:
    """A stable, separately classified validation result."""

    subject_id: str
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class ArchitectureValidation:
    """Validated candidate plus coverage and guardrail findings."""

    architecture: SolutionArchitecture
    uncovered_capabilities: tuple[ArchitectureFinding, ...]
    unjustified_components: tuple[ArchitectureFinding, ...]
    unknown_dependencies: tuple[ArchitectureFinding, ...]
    disconnected_components: tuple[ArchitectureFinding, ...]


@dataclass(frozen=True, slots=True)
class ArchitectureAnalysis:
    """Multiple candidates retained without scoring, ranking, or selection."""

    approach_analysis: SolutionApproachAnalysis
    validations: tuple[ArchitectureValidation, ...]


def validate_architecture(
    approach_analysis: SolutionApproachAnalysis, architecture: SolutionArchitecture
) -> ArchitectureValidation:
    """Validate explicit references and derive educational coverage findings."""
    if architecture.engagement != approach_analysis.option_set.engagement:
        raise ValueError("architecture and approaches must describe the same engagement")
    approach_ids = {item.identifier for item in approach_analysis.approaches}
    unknown_approaches = set(architecture.approach_ids) - approach_ids
    if unknown_approaches:
        raise ValueError(f"architecture references unknown approach '{min(unknown_approaches)}'")
    ids = [item.identifier for item in architecture.components]
    if any(not item.strip() for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("component identifiers must be non-blank and unique")
    actor_ids = {item.identifier for item in architecture.actors}
    endpoint_ids = set(ids) | actor_ids
    connection_ids: set[str] = set()
    connected: set[str] = set()
    for connection in architecture.connections:
        if connection.identifier in connection_ids:
            raise ValueError("connection identifiers must be unique")
        connection_ids.add(connection.identifier)
        missing = {connection.source_id, connection.destination_id} - endpoint_ids
        if missing:
            raise ValueError(f"connection references missing component or actor '{min(missing)}'")
        connected.update((connection.source_id, connection.destination_id))
    for flow in architecture.information_flows:
        if flow.connection_id not in connection_ids:
            raise ValueError(
                f"information flow references missing connection '{flow.connection_id}'"
            )

    capability_ids = {
        item.identifier
        for item in approach_analysis.gap_analysis.required.capability_map.capabilities
    }
    requirement_ids = {
        item.identifier
        for item in approach_analysis.gap_analysis.required.requirement_set.requirements
    }
    for component in architecture.components:
        unknown_capabilities = set(component.capability_ids) - capability_ids
        unknown_requirements = set(component.requirement_ids) - requirement_ids
        if unknown_capabilities:
            raise ValueError(
                f"component references unknown capability '{min(unknown_capabilities)}'"
            )
        if unknown_requirements:
            raise ValueError(
                f"component references unknown requirement '{min(unknown_requirements)}'"
            )
    covered = {item for component in architecture.components for item in component.capability_ids}
    uncovered = tuple(
        ArchitectureFinding(
            capability.identifier,
            "Uncovered Capability",
            "A required capability has no architecture component supporting it.",
        )
        for capability in approach_analysis.gap_analysis.required.capability_map.capabilities
        if capability.identifier not in covered
    )
    unjustified = tuple(
        ArchitectureFinding(
            component.identifier,
            "Unjustified Component",
            "No established requirement, capability, constraint, or architectural dependency "
            "currently explains why this component exists.",
        )
        for component in architecture.components
        if not (
            component.capability_ids
            or component.requirement_ids
            or component.constraint_ids
            or component.necessity
        )
    )
    unknown = tuple(
        ArchitectureFinding(item.identifier, "Unknown Dependency", item.description)
        for item in architecture.dependencies
        if item.state is DependencyState.UNKNOWN
    )
    disconnected = tuple(
        ArchitectureFinding(
            item.identifier,
            "Disconnected Component",
            "The component participates in no architecture connection.",
        )
        for item in architecture.components
        if item.identifier not in connected
    )
    return ArchitectureValidation(architecture, uncovered, unjustified, unknown, disconnected)


def analyze_architectures(
    approach_analysis: SolutionApproachAnalysis,
    architectures: tuple[SolutionArchitecture, ...],
) -> ArchitectureAnalysis:
    """Validate candidates in authored order without selecting a winner."""
    identifiers = [item.identifier for item in architectures]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("architecture identifiers must be unique")
    return ArchitectureAnalysis(
        approach_analysis,
        tuple(validate_architecture(approach_analysis, item) for item in architectures),
    )


def add_components(
    architecture: SolutionArchitecture, components: tuple[ArchitectureComponent, ...]
) -> SolutionArchitecture:
    """Create an overengineering experiment without mutating the original."""
    return replace(architecture, components=(*architecture.components, *components))


def remove_component(architecture: SolutionArchitecture, component_id: str) -> SolutionArchitecture:
    """Create a completeness experiment and remove dependent flows/connections immutably."""
    removed_connections = {
        item.identifier
        for item in architecture.connections
        if component_id in (item.source_id, item.destination_id)
    }
    return replace(
        architecture,
        components=tuple(
            item for item in architecture.components if item.identifier != component_id
        ),
        connections=tuple(
            item for item in architecture.connections if item.identifier not in removed_connections
        ),
        information_flows=tuple(
            item
            for item in architecture.information_flows
            if item.connection_id not in removed_connections
        ),
    )


def unknown_dependencies(
    dependencies: tuple[ArchitectureDependency, ...],
) -> tuple[ArchitectureDependency, ...]:
    """Expose deterministic dependency filtering for learner inspection."""
    return tuple(item for item in dependencies if item.state is DependencyState.UNKNOWN)
