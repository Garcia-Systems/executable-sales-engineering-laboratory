"""Chapter 6 capability mapping behavior and educational guardrails."""

from dataclasses import FrozenInstanceError

import pytest

from sales_lab.domain.capabilities import (
    Capability,
    CapabilityCategory,
    CapabilityMap,
    CapabilityRequirementLink,
    CoverageStatus,
)
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_capability_map,
    harbor_street_music_requirements,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.capabilities import (
    render_capability_matrix,
    render_capability_report,
    render_requirement_coverage,
)
from sales_lab.services.capabilities import CapabilityAnalysis, add_capability, analyze_capabilities


def analysis_for(capability_map: CapabilityMap | None = None) -> CapabilityAnalysis:
    """Build the fixed analysis or a controlled experimental variant."""
    return analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        capability_map or harbor_street_music_capability_map(),
    )


def test_capabilities_are_immutable_and_categories_are_transparent() -> None:
    """Frozen records use the documented educational category enumeration."""
    capability = harbor_street_music_capability_map().capabilities[0]
    assert capability.category is CapabilityCategory.INFORMATION
    assert tuple(CapabilityCategory) == (
        CapabilityCategory.PROCESS,
        CapabilityCategory.INFORMATION,
        CapabilityCategory.COLLABORATION,
        CapabilityCategory.INTEGRATION,
        CapabilityCategory.CONTROL,
        CapabilityCategory.REPORTING,
    )
    with pytest.raises(FrozenInstanceError):
        capability.name = "Changed"  # type: ignore[misc]


def test_many_to_many_mapping_and_order_are_preserved() -> None:
    """Requirements and capabilities can each participate in multiple ordered links."""
    analysis = analysis_for()
    assert analysis.coverage[0].capability_ids == ("CAP-001", "CAP-003")
    assert analysis.coverage[1].capability_ids == ("CAP-002", "CAP-003")
    assert tuple(item.requirement.identifier for item in analysis.coverage) == (
        "REQ-001",
        "REQ-002",
        "REQ-003",
    )
    assert all(item.status is CoverageStatus.COVERED for item in analysis.coverage)


def test_requirement_gap_partial_and_not_evaluated_coverage() -> None:
    """Missing and incomplete qualitative coverage remain explicit."""
    original = harbor_street_music_capability_map()
    modified = CapabilityMap(
        original.engagement,
        original.capabilities,
        (
            CapabilityRequirementLink("CAP-001", "REQ-001", CoverageStatus.PARTIALLY_COVERED),
            CapabilityRequirementLink("CAP-002", "REQ-002", CoverageStatus.NOT_EVALUATED),
        ),
    )
    analysis = analysis_for(modified)
    assert tuple(item.status for item in analysis.coverage) == (
        CoverageStatus.PARTIALLY_COVERED,
        CoverageStatus.NOT_EVALUATED,
        CoverageStatus.NOT_COVERED,
    )
    assert analysis.gaps[0].subject_id == "REQ-003"
    assert {item.subject_id for item in analysis.unsupported_capabilities} == {"CAP-003", "CAP-004"}


def test_explicit_not_covered_link_remains_qualitative() -> None:
    """A reviewed non-supporting link does not become a positive mapping or a score."""
    original = harbor_street_music_capability_map()
    modified = CapabilityMap(
        original.engagement,
        original.capabilities,
        (CapabilityRequirementLink("CAP-001", "REQ-001", CoverageStatus.NOT_COVERED),),
    )
    assert analysis_for(modified).coverage[0].status is CoverageStatus.NOT_COVERED


def test_unknown_links_are_incomplete_and_do_not_create_coverage() -> None:
    """Dangling references are reported rather than silently accepted."""
    original = harbor_street_music_capability_map()
    modified = CapabilityMap(
        original.engagement,
        original.capabilities,
        (*original.links, CapabilityRequirementLink("CAP-404", "REQ-404")),
    )
    finding = analysis_for(modified).incomplete_mappings[0]
    assert finding.kind == "Incomplete Mapping"
    assert finding.subject_id == "REQ-404 → CAP-404"


def test_solution_first_experiment_is_immutable_and_flagged() -> None:
    """An interesting technology needs justification and leaves the base fixture unchanged."""
    original = harbor_street_music_capability_map()
    experiment = add_capability(
        original,
        Capability(
            "CAP-999",
            "AI Chatbot",
            "Explore conversational assistance only if future discovery justifies it.",
            CapabilityCategory.COLLABORATION,
        ),
    )
    assert len(original.capabilities) + 1 == len(experiment.capabilities)
    unsupported = analysis_for(experiment).unsupported_capabilities
    assert unsupported[-1].subject_id == "CAP-999"
    assert "No established requirement" in unsupported[-1].message


def test_matrices_report_and_traceability_are_deterministic_and_score_free() -> None:
    """Presentation reuses IDs and evidence while avoiding pseudo-precision."""
    analysis = analysis_for()
    matrix = render_capability_matrix(analysis)
    coverage = render_requirement_coverage(analysis)
    report = render_capability_report(analysis)
    assert matrix.startswith("| Capability | REQ-001 | REQ-002 | REQ-003 |")
    assert "| Inquiry Information Sharing | Supports | Supports | — |" in matrix
    assert "| REQ-002 | CAP-002, CAP-003 | Covered |" in coverage
    assert report.startswith("# Capability Mapping Analysis")
    assert "CAP-001 ← REQ-001 ← Front Desk Staff ← E2" in report
    assert "Capabilities ≠ Products" in report
    assert render_capability_report(analysis) == report
    assert "%" not in report
    assert "fit score" not in report.lower()
