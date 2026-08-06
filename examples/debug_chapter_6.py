"""Chapter 6 debugger path from requirements through capability gaps."""

from sales_lab.domain.capabilities import Capability, CapabilityCategory
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_capability_map,
    harbor_street_music_requirements,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.capabilities import render_capability_report
from sales_lab.services.capabilities import add_capability, analyze_capabilities

requirements = harbor_street_music_requirements()  # Breakpoint 1: established requirements
capability_map = harbor_street_music_capability_map()  # Breakpoint 2: capabilities and mappings
analysis = analyze_capabilities(  # Breakpoint 3: traceability validation
    requirements, harbor_street_music_stakeholder_map(), capability_map
)
coverage = analysis.coverage  # Breakpoint 4: inspect qualitative coverage
gaps = analysis.gaps
unsupported_capabilities = analysis.unsupported_capabilities  # Breakpoint 5: base gap detection

experiment = add_capability(
    capability_map,
    Capability(
        "CAP-999",
        "AI Chatbot",
        "A technology idea requiring discovery and requirement justification.",
        CapabilityCategory.COLLABORATION,
    ),
)
experiment_analysis = analyze_capabilities(
    requirements, harbor_street_music_stakeholder_map(), experiment
)
unsupported_capabilities = experiment_analysis.unsupported_capabilities  # Breakpoint 6
print(render_capability_report(experiment_analysis))  # noqa: T201 - learner-facing script
