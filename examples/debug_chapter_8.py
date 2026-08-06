"""Chapter 8 debugging laboratory: inspect alternatives without selecting one."""

from sales_lab.domain.approaches import (
    ApproachAssumption,
    FeasibilityState,
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
from sales_lab.reports.approaches import render_approach_comparison_matrix
from sales_lab.services.approaches import add_candidate, analyze_solution_approaches
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.gaps import analyze_gaps

required = analyze_capabilities(
    harbor_street_music_requirements(),
    harbor_street_music_stakeholder_map(),
    harbor_street_music_capability_map(),
)
gap_analysis = analyze_gaps(required, harbor_street_music_current_capability_inventory())
gap = gap_analysis.gaps[0]  # Breakpoint 1: capability gap.
options = harbor_street_music_solution_options()
approaches = options.approaches  # Breakpoint 2: candidate approaches.
assumptions = approaches[0].assumptions
constraints = approaches[0].constraint_requirement_ids
evidence_needs = approaches[0].evidence_needs
feasibility = approaches[0].feasibility
tradeoffs = approaches[0].tradeoffs  # Breakpoint 3: bounded analysis inputs.
analysis = analyze_solution_approaches(gap_analysis, options)  # Breakpoint 4: traceability.
matrix = render_approach_comparison_matrix(analysis)  # Breakpoint 5: comparison, not ranking.

mobile = SolutionApproach(
    "EXP-MOBILE",
    "Build a Native Mobile App",
    SolutionApproachType.BUILD,
    "Experimental technology idea.",
    (),
    (
        ApproachAssumption(
            "Mobile access is needed.", "Not established", FeasibilityState.REQUIRES_VALIDATION
        ),
    ),
    (),
    ("Evidence of a mobile-access requirement and capability gap",),
    FeasibilityState.REQUIRES_VALIDATION,
    (),
    "Maybe",
    "No",
    "Yes",
)
experimental = analyze_solution_approaches(gap_analysis, add_candidate(options, mobile))
unsupported = experimental.unsupported_approaches  # Breakpoint 6: original options unchanged.
