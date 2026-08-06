"""Deterministic, evidence-based current capability gap analysis."""

# Referential validation is intentionally kept together for the debugging laboratory.
# ruff: noqa: C901, PLR0912

from dataclasses import dataclass, replace

from sales_lab.domain.gaps import (
    CapabilityAssessment,
    CapabilityGap,
    CapabilityState,
    CurrentCapabilityInventory,
    EvidenceReference,
)
from sales_lab.services.capabilities import CapabilityAnalysis


@dataclass(frozen=True, slots=True)
class GapAnalysis:
    """Chapter 6 required capabilities compared with an explicit current inventory."""

    required: CapabilityAnalysis
    inventory: CurrentCapabilityInventory
    assessments: tuple[CapabilityAssessment, ...]
    gaps: tuple[CapabilityGap, ...]
    partial_capabilities: tuple[CapabilityAssessment, ...]
    unknown_capabilities: tuple[CapabilityAssessment, ...]
    follow_up_questions: tuple[str, ...]


def analyze_gaps(
    required: CapabilityAnalysis, inventory: CurrentCapabilityInventory
) -> GapAnalysis:
    """Validate references and derive stable views without recommending remedies."""
    capability_ids = tuple(item.identifier for item in required.capability_map.capabilities)
    resource_ids = {item.identifier for item in inventory.resources}
    evidence_ids = {item.identifier for item in inventory.evidence}
    if inventory.engagement != required.capability_map.engagement:
        message = "current inventory and required capabilities must describe the same engagement"
        raise ValueError(message)
    if len(resource_ids) != len(inventory.resources):
        message = "current resource identifiers must be unique"
        raise ValueError(message)
    if len(evidence_ids) != len(inventory.evidence):
        message = "current evidence identifiers must be unique"
        raise ValueError(message)
    for resource in inventory.resources:
        for evidence_id in resource.evidence_ids:
            if evidence_id not in evidence_ids:
                message = f"resource references unknown evidence '{evidence_id}'"
                raise ValueError(message)
    authored = {item.capability_id: item for item in inventory.assessments}
    if len(authored) != len(inventory.assessments):
        message = "capability assessments must have unique capability identifiers"
        raise ValueError(message)
    unknown_capability_ids = set(authored).difference(capability_ids)
    if unknown_capability_ids:
        message = f"assessment references unknown capability '{sorted(unknown_capability_ids)[0]}'"
        raise ValueError(message)
    missing_capability_ids = set(capability_ids).difference(authored)
    if missing_capability_ids:
        message = f"required capability '{sorted(missing_capability_ids)[0]}' lacks an assessment"
        raise ValueError(message)
    for assessment in inventory.assessments:
        for resource_id in assessment.current_resource_ids:
            if resource_id not in resource_ids:
                message = f"assessment references unknown resource '{resource_id}'"
                raise ValueError(message)
        for evidence_id in assessment.evidence_ids:
            if evidence_id not in evidence_ids:
                message = f"assessment references unknown evidence '{evidence_id}'"
                raise ValueError(message)
        needs_gap = assessment.state is not CapabilityState.AVAILABLE
        if needs_gap and (assessment.gap_type is None or assessment.follow_up_question is None):
            message = (
                f"non-available assessment '{assessment.capability_id}' needs a gap and question"
            )
            raise ValueError(message)

    assessments = tuple(authored[item] for item in capability_ids if item in authored)
    gaps = tuple(
        CapabilityGap(item.capability_id, item.gap_type, item.rationale)
        for item in assessments
        if item.state is not CapabilityState.AVAILABLE and item.gap_type is not None
    )
    return GapAnalysis(
        required,
        inventory,
        assessments,
        gaps,
        tuple(item for item in assessments if item.state is CapabilityState.PARTIALLY_AVAILABLE),
        tuple(item for item in assessments if item.state is CapabilityState.UNKNOWN),
        tuple(
            item.follow_up_question for item in assessments if item.follow_up_question is not None
        ),
    )


def add_assessment_evidence(
    inventory: CurrentCapabilityInventory,
    evidence: EvidenceReference,
    revised_assessment: CapabilityAssessment,
) -> CurrentCapabilityInventory:
    """Return a new experimental inventory; never rewrite the original evidence record."""
    assessments = tuple(
        revised_assessment if item.capability_id == revised_assessment.capability_id else item
        for item in inventory.assessments
    )
    return replace(
        inventory,
        evidence=(*inventory.evidence, evidence),
        assessments=assessments,
    )
