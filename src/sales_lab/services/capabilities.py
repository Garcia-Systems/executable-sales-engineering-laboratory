"""Deterministic capability mapping and solution-first validation."""

from dataclasses import dataclass, replace

from sales_lab.domain.capabilities import (
    Capability,
    CapabilityGap,
    CapabilityMap,
    CapabilityRequirementLink,
    CoverageStatus,
)
from sales_lab.domain.requirements import Requirement, RequirementSet, RequirementStatus
from sales_lab.domain.stakeholders import StakeholderMap


@dataclass(frozen=True, slots=True)
class RequirementCoverage:
    """One established requirement's supporting capabilities and coverage state."""

    requirement: Requirement
    capability_ids: tuple[str, ...]
    status: CoverageStatus


@dataclass(frozen=True, slots=True)
class CapabilityAnalysis:
    """Validated mapping plus stable, derived views and traceability inputs."""

    requirement_set: RequirementSet
    stakeholder_map: StakeholderMap
    capability_map: CapabilityMap
    coverage: tuple[RequirementCoverage, ...]
    gaps: tuple[CapabilityGap, ...]
    unsupported_capabilities: tuple[CapabilityGap, ...]
    incomplete_mappings: tuple[CapabilityGap, ...]


def analyze_capabilities(
    requirements: RequirementSet, stakeholder_map: StakeholderMap, capability_map: CapabilityMap
) -> CapabilityAnalysis:
    """Validate only explicit definitions and links; never infer capabilities from prose."""
    established = tuple(
        item for item in requirements.requirements if item.status is RequirementStatus.ESTABLISHED
    )
    requirement_ids = {item.identifier for item in established}
    capability_ids = {item.identifier for item in capability_map.capabilities}
    incomplete: list[CapabilityGap] = []
    valid_links: list[CapabilityRequirementLink] = []
    for link in capability_map.links:
        if link.requirement_id not in requirement_ids or link.capability_id not in capability_ids:
            incomplete.append(
                CapabilityGap(
                    f"{link.requirement_id} → {link.capability_id}",
                    "Incomplete Mapping",
                    "The link references an unknown established requirement or capability.",
                )
            )
        else:
            valid_links.append(link)

    coverage: list[RequirementCoverage] = []
    gaps: list[CapabilityGap] = []
    for requirement in established:
        links = tuple(link for link in valid_links if link.requirement_id == requirement.identifier)
        identifiers = tuple(link.capability_id for link in links)
        if not links:
            status = CoverageStatus.NOT_COVERED
            gaps.append(
                CapabilityGap(
                    requirement.identifier,
                    "Requirement Gap",
                    "No capability is mapped to this established requirement.",
                )
            )
        elif any(link.coverage is CoverageStatus.NOT_EVALUATED for link in links):
            status = CoverageStatus.NOT_EVALUATED
        elif any(link.coverage is CoverageStatus.PARTIALLY_COVERED for link in links):
            status = CoverageStatus.PARTIALLY_COVERED
        elif all(link.coverage is CoverageStatus.NOT_COVERED for link in links):
            status = CoverageStatus.NOT_COVERED
        else:
            status = CoverageStatus.COVERED
        coverage.append(RequirementCoverage(requirement, identifiers, status))

    linked_capabilities = {link.capability_id for link in valid_links}
    unsupported = tuple(
        CapabilityGap(
            capability.identifier,
            "Unsupported Capability",
            "No established requirement currently justifies this capability.",
        )
        for capability in capability_map.capabilities
        if capability.identifier not in linked_capabilities
    )
    return CapabilityAnalysis(
        requirements,
        stakeholder_map,
        capability_map,
        tuple(coverage),
        tuple(gaps),
        unsupported,
        tuple(incomplete),
    )


def add_capability(capability_map: CapabilityMap, capability: Capability) -> CapabilityMap:
    """Return an experimental map without mutating the original map."""
    return replace(capability_map, capabilities=(*capability_map.capabilities, capability))
