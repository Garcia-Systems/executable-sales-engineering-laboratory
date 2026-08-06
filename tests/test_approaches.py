"""Chapter 8 neutral solution-approach analysis and guardrails."""

from dataclasses import FrozenInstanceError, replace

import pytest

from sales_lab.domain.approaches import (
    ApproachAssumption,
    FeasibilityState,
    QualitativeState,
    SolutionApproach,
    SolutionApproachType,
)
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_capability_map,
    harbor_street_music_current_capability_inventory,
    harbor_street_music_requirements,
    harbor_street_music_solution_options,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.approaches import (
    render_approach_comparison_matrix,
    render_solution_approach_report,
)
from sales_lab.services.approaches import (
    SolutionApproachAnalysis,
    add_candidate,
    analyze_solution_approaches,
)
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.gaps import analyze_gaps

OPTION_COUNT = 7
DISTINCT_STATE_COUNT = 2


OPTION_COUNT = 7
DISTINCT_STATE_COUNT = 2


def canonical_analysis() -> SolutionApproachAnalysis:
    """Compose Chapters 4-8 rather than recreating traceability as strings."""
    required = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    gaps = analyze_gaps(required, harbor_street_music_current_capability_inventory())
    return analyze_solution_approaches(gaps, harbor_street_music_solution_options())


def mobile_candidate(gaps: tuple[str, ...] = ()) -> SolutionApproach:
    """Create the controlled premature-selection experiment candidate."""
    return SolutionApproach(
        "EXP-MOBILE",
        "Build a Native Mobile App",
        SolutionApproachType.BUILD,
        "A technology idea whose merit is not being judged.",
        gaps,
        (
            ApproachAssumption(
                "Mobile access is required.",
                "Not established",
                FeasibilityState.REQUIRES_VALIDATION,
            ),
        ),
        (),
        ("Validated mobile-access requirement and capability gap",),
        FeasibilityState.REQUIRES_VALIDATION,
        (),
        "Maybe",
        "No",
        "Yes",
    )


def test_models_are_immutable_and_categories_and_states_are_distinct() -> None:
    """Frozen candidates preserve all transparent educational classifications."""
    candidate = canonical_analysis().approaches[0]
    with pytest.raises(FrozenInstanceError):
        candidate.name = "Winner"  # type: ignore[misc]
    assert set(SolutionApproachType) == {
        SolutionApproachType.PROCESS_CHANGE,
        SolutionApproachType.CONFIGURE_EXISTING,
        SolutionApproachType.INTEGRATE_EXISTING,
        SolutionApproachType.BUY,
        SolutionApproachType.BUILD,
        SolutionApproachType.HYBRID,
        SolutionApproachType.STATUS_QUO,
    }
    assert (
        len({FeasibilityState.REQUIRES_VALIDATION, FeasibilityState.NOT_FEASIBLE})
        == DISTINCT_STATE_COUNT
    )
    assert len({QualitativeState.UNKNOWN, QualitativeState.NOT_EVALUATED}) == DISTINCT_STATE_COUNT


def test_traceability_order_assumptions_constraints_and_feasibility_are_preserved() -> None:
    """The service preserves authored alternatives and Chapter 5/7 references."""
    analysis = canonical_analysis()
    assert tuple(item.identifier for item in analysis.approaches) == tuple(
        f"APP-{number:03}" for number in range(1, 8)
    )
    assert all(item.gap_capability_ids == ("CAP-001",) for item in analysis.approaches)
    assert all(item.constraint_requirement_ids == ("REQ-003",) for item in analysis.approaches)
    assert all(item.assumptions and item.evidence_needs for item in analysis.approaches)
    assert analysis.unsupported_approaches == ()
    assert len(analysis.unresolved_feasibility) == OPTION_COUNT


def test_premature_mobile_idea_is_unsupported_without_mutating_original() -> None:
    """Adding an unlinked technology flags provenance, not the idea as bad."""
    analysis = canonical_analysis()
    experimental_set = add_candidate(analysis.option_set, mobile_candidate())
    result = analyze_solution_approaches(analysis.gap_analysis, experimental_set)
    assert result.unsupported_approaches == (experimental_set.approaches[-1],)
    assert len(analysis.option_set.approaches) == OPTION_COUNT
    linked = replace(mobile_candidate(), gap_capability_ids=("CAP-001",))
    linked_result = analyze_solution_approaches(
        analysis.gap_analysis, add_candidate(analysis.option_set, linked)
    )
    assert linked_result.unsupported_approaches == ()


def test_matrix_and_report_are_deterministic_complete_and_product_neutral() -> None:
    """Presentation compares qualitative inputs but never ranks or selects."""
    analysis = canonical_analysis()
    matrix = render_approach_comparison_matrix(analysis)
    assert matrix.startswith("| Approach | Existing Tools | New Software")
    assert "Configure the Existing Spreadsheet | Yes | No | No | Requires Validation" in matrix
    report = render_solution_approach_report(analysis)
    for heading in (
        "Engagement",
        "Established Capability Gaps",
        "Candidate Solution Approaches",
        "Gap-to-Approach Traceability",
        "Assumptions",
        "Constraints",
        "Tradeoffs",
        "Feasibility",
        "Evidence Still Required",
        "Unsupported Approaches",
        "Comparison Matrix",
        "Status Quo",
        "Open Questions",
        "Educational Limitations",
    ):
        assert f"## {heading}" in report
    assert render_solution_approach_report(analysis) == report
    for forbidden in (
        "approach score =",
        "preferred approach:",
        "declared winner:",
        "salesforce",
        "hubspot",
    ):
        assert forbidden not in report.lower()
    assert "Future Evaluation" in report


def test_validation_rejects_bad_engagement_duplicates_constraints_and_impossibility() -> None:
    """Malformed authored inputs fail explicitly while unsupported ideas remain reportable."""
    analysis = canonical_analysis()
    options = analysis.option_set
    with pytest.raises(ValueError, match="same engagement"):
        analyze_solution_approaches(analysis.gap_analysis, replace(options, engagement="Other"))
    with pytest.raises(ValueError, match="identifiers must be unique"):
        analyze_solution_approaches(
            analysis.gap_analysis, replace(options, approaches=(options.approaches[0],) * 2)
        )
    bad_constraint = replace(options.approaches[0], constraint_requirement_ids=("REQ-404",))
    with pytest.raises(ValueError, match="unknown constraint"):
        analyze_solution_approaches(
            analysis.gap_analysis, replace(options, approaches=(bad_constraint,))
        )
    impossible = replace(
        options.approaches[0], feasibility=FeasibilityState.NOT_FEASIBLE, evidence_needs=()
    )
    with pytest.raises(ValueError, match="explicit evidence"):
        analyze_solution_approaches(
            analysis.gap_analysis, replace(options, approaches=(impossible,))
        )
