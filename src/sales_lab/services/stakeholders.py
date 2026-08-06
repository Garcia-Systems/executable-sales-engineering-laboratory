"""Validation and deterministic derivation for stakeholder maps."""

# Validation is kept together so learners can step through referential checks.
# ruff: noqa: C901, PERF401

from dataclasses import dataclass

from sales_lab.domain.business_process import BusinessProcess
from sales_lab.domain.stakeholders import (
    AuthorityState,
    PerspectiveGap,
    StakeholderMap,
    StakeholderRole,
)


@dataclass(frozen=True, slots=True)
class StakeholderAnalysis:
    """A validated map and the Chapter 3 process on which it is based."""

    stakeholder_map: StakeholderMap
    process: BusinessProcess
    missing_perspectives: tuple[PerspectiveGap, ...]
    follow_up_questions: tuple[str, ...]


def analyze_stakeholders(
    process: BusinessProcess, stakeholder_map: StakeholderMap
) -> StakeholderAnalysis:
    """Validate all references and preserve the author's explicit stable ordering."""
    role_ids = tuple(role.identifier for role in stakeholder_map.roles)
    evidence_ids = tuple(item.identifier for item in stakeholder_map.evidence)
    step_ids = tuple(step.identifier for step in process.steps)
    if len(role_ids) != len(set(role_ids)):
        message = "stakeholder role identifiers must be unique"
        raise ValueError(message)
    if len(evidence_ids) != len(set(evidence_ids)):
        message = "stakeholder evidence identifiers must be unique"
        raise ValueError(message)
    known_roles, known_evidence, known_steps = set(role_ids), set(evidence_ids), set(step_ids)
    references: list[tuple[str, str]] = []
    for responsibility in stakeholder_map.responsibilities:
        references.append((responsibility.role_id, responsibility.evidence_id))
    for authority in stakeholder_map.authority:
        references.append((authority.role_id, authority.evidence_id))
    for participation in stakeholder_map.participations:
        references.append((participation.role_id, participation.evidence_id))
        if participation.step_id not in known_steps:
            message = f"participation references unknown process step '{participation.step_id}'"
            raise ValueError(message)
    for relationship in stakeholder_map.relationships:
        references.extend(
            (
                (relationship.source_role_id, relationship.evidence_id),
                (relationship.target_role_id, relationship.evidence_id),
            )
        )
    for role_id, evidence_id in references:
        if role_id not in known_roles:
            message = f"stakeholder assertion references unknown role '{role_id}'"
            raise ValueError(message)
        if evidence_id not in known_evidence:
            message = f"stakeholder assertion references unknown evidence '{evidence_id}'"
            raise ValueError(message)
    return StakeholderAnalysis(
        stakeholder_map,
        process,
        stakeholder_map.perspective_gaps,
        tuple(gap.follow_up_question for gap in stakeholder_map.perspective_gaps),
    )


def authority_for(analysis: StakeholderAnalysis, role: StakeholderRole) -> AuthorityState:
    """Return recorded change authority, without converting missing evidence to no."""
    matches = tuple(
        item.state for item in analysis.stakeholder_map.authority if item.role_id == role.identifier
    )
    return matches[0] if matches else AuthorityState.UNKNOWN
