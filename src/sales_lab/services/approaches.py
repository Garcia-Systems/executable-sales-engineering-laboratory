"""Deterministic validation and analysis of candidate solution approaches."""

from dataclasses import dataclass, replace

from sales_lab.domain.approaches import FeasibilityState, SolutionApproach, SolutionOptionSet
from sales_lab.services.gaps import GapAnalysis


@dataclass(frozen=True, slots=True)
class SolutionApproachAnalysis:
    """Validated candidates and stable derived views, without selection or ranking."""

    gap_analysis: GapAnalysis
    option_set: SolutionOptionSet
    approaches: tuple[SolutionApproach, ...]
    unsupported_approaches: tuple[SolutionApproach, ...]
    unresolved_feasibility: tuple[SolutionApproach, ...]


def analyze_solution_approaches(
    gap_analysis: GapAnalysis, option_set: SolutionOptionSet
) -> SolutionApproachAnalysis:
    """Validate references and preserve authored order; never choose a winner."""
    if option_set.engagement != gap_analysis.inventory.engagement:
        message = "solution options and gaps must describe the same engagement"
        raise ValueError(message)
    identifiers = [item.identifier for item in option_set.approaches]
    if len(set(identifiers)) != len(identifiers):
        message = "solution approach identifiers must be unique"
        raise ValueError(message)
    requirement_ids = {
        item.identifier for item in gap_analysis.required.requirement_set.requirements
    }
    for approach in option_set.approaches:
        unknown_constraints = set(approach.constraint_requirement_ids) - requirement_ids
        if unknown_constraints:
            message = f"approach references unknown constraint '{sorted(unknown_constraints)[0]}'"
            raise ValueError(message)
        if approach.feasibility is FeasibilityState.NOT_FEASIBLE and not approach.evidence_needs:
            message = "NOT_FEASIBLE requires explicit evidence explaining impossibility"
            raise ValueError(message)
    gap_ids = {item.capability_id for item in gap_analysis.gaps}
    unsupported = tuple(
        item
        for item in option_set.approaches
        if not item.gap_capability_ids or not set(item.gap_capability_ids).intersection(gap_ids)
    )
    unresolved = tuple(
        item
        for item in option_set.approaches
        if item.feasibility
        in (FeasibilityState.REQUIRES_VALIDATION, FeasibilityState.NOT_EVALUATED)
    )
    return SolutionApproachAnalysis(
        gap_analysis, option_set, option_set.approaches, unsupported, unresolved
    )


def add_candidate(option_set: SolutionOptionSet, candidate: SolutionApproach) -> SolutionOptionSet:
    """Return an experimental option set without mutating the canonical scenario."""
    return replace(option_set, approaches=(*option_set.approaches, candidate))
