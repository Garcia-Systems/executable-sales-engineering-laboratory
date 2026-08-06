"""Debugger entry point for Chapter 10 integration strategies."""

# Debug scripts intentionally expose values in a terminal.
# ruff: noqa: T201

from sales_lab.examples.harbor_street_music import (
    harbor_street_music_architectures,
    harbor_street_music_capability_map,
    harbor_street_music_current_capability_inventory,
    harbor_street_music_requirements,
    harbor_street_music_solution_options,
    harbor_street_music_stakeholder_map,
)
from sales_lab.services.approaches import analyze_solution_approaches
from sales_lab.services.architecture import analyze_architectures
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.gaps import analyze_gaps
from sales_lab.services.integrations import (
    analyze_integrations,
    harbor_street_integration_strategies,
    integration_questions,
    simulate_duplicate_delivery,
)

required = analyze_capabilities(
    harbor_street_music_requirements(),
    harbor_street_music_stakeholder_map(),
    harbor_street_music_capability_map(),
)
gaps = analyze_gaps(required, harbor_street_music_current_capability_inventory())
approaches = analyze_solution_approaches(gaps, harbor_street_music_solution_options())
architectures = analyze_architectures(approaches, harbor_street_music_architectures())
strategies = harbor_street_integration_strategies()  # breakpoint: inspect source/destination/flow
analysis = analyze_integrations(architectures, strategies, integration_questions())  # breakpoint
duplicate_delivery = simulate_duplicate_delivery(idempotent=True)  # breakpoint: compare False

for strategy in analysis.strategies:
    print(strategy.identifier, strategy.pattern.value, strategy.feasibility.value)
for step in duplicate_delivery:
    print(step.action, "->", step.outcome)
