"""Chapter 9 debugger path from requirement to architecture coverage."""

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

requirements = harbor_street_music_requirements()  # Breakpoint: requirement and evidence.
capabilities = analyze_capabilities(
    requirements, harbor_street_music_stakeholder_map(), harbor_street_music_capability_map()
)  # Breakpoint: capability links.
gaps = analyze_gaps(capabilities, harbor_street_music_current_capability_inventory())
approaches = analyze_solution_approaches(gaps, harbor_street_music_solution_options())
architectures = harbor_street_music_architectures()  # Breakpoint: components and connections.
analysis = analyze_architectures(approaches, architectures)  # Breakpoint: coverage validation.
validation = analysis.validations[0]
components = validation.architecture.components
connections = validation.architecture.connections
information_flows = validation.architecture.information_flows
capability_links = capabilities.capability_map.links
uncovered_capabilities = validation.uncovered_capabilities
unjustified_components = validation.unjustified_components
unknown_dependencies = validation.unknown_dependencies

print(validation.architecture.name)
print(f"Coverage findings: {len(uncovered_capabilities)}")
print(f"Unknown dependencies: {len(unknown_dependencies)}")
