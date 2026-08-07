"""Chapter 10 integration strategy tests."""

from dataclasses import FrozenInstanceError, replace

import pytest

from sales_lab.diagrams.integrations import (
    render_api_pattern_mermaid,
    render_event_pattern_mermaid,
    render_integration_boundary_mermaid,
)
from sales_lab.domain.integrations import (
    DataOwnership,
    IntegrationDirection,
    IntegrationPattern,
    IntegrationTiming,
)
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_architectures,
    harbor_street_music_capability_map,
    harbor_street_music_current_capability_inventory,
    harbor_street_music_requirements,
    harbor_street_music_solution_options,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.integrations import render_integration_report
from sales_lab.services.approaches import analyze_solution_approaches
from sales_lab.services.architecture import ArchitectureAnalysis, analyze_architectures
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.gaps import analyze_gaps
from sales_lab.services.integrations import (
    analyze_integrations,
    harbor_street_integration_strategies,
    integration_questions,
    simulate_destination_failure,
    simulate_duplicate_delivery,
    simulate_manual_handoff,
    validate_integration,
)


def architecture_analysis() -> ArchitectureAnalysis:
    """Build the canonical cross-chapter analysis."""
    required = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    gaps = analyze_gaps(required, harbor_street_music_current_capability_inventory())
    approaches = analyze_solution_approaches(gaps, harbor_street_music_solution_options())
    return analyze_architectures(approaches, harbor_street_music_architectures())


def test_strategy_is_immutable_and_models_patterns_direction_timing_and_ownership() -> None:
    """The small model is frozen and explicit rather than API-centric."""
    strategies = harbor_street_integration_strategies()
    with pytest.raises(FrozenInstanceError):
        strategies[0].information = "changed"  # type: ignore[misc]
    assert tuple(item.pattern for item in strategies) == (
        IntegrationPattern.MANUAL_HANDOFF,
        IntegrationPattern.FILE_BATCH,
        IntegrationPattern.REQUEST_RESPONSE_API,
        IntegrationPattern.WEBHOOK,
        IntegrationPattern.EVENT_DRIVEN,
    )
    assert all(item.direction is IntegrationDirection.ONE_WAY for item in strategies)
    assert {item.timing for item in strategies} == {
        IntegrationTiming.MANUAL,
        IntegrationTiming.SCHEDULED,
        IntegrationTiming.ON_DEMAND,
        IntegrationTiming.NEAR_REAL_TIME,
        IntegrationTiming.EVENT_DRIVEN,
    }
    assert strategies[0].data_ownership is DataOwnership.NOT_ESTABLISHED


def test_analysis_preserves_order_unknowns_assumptions_failures_and_traceability() -> None:
    """Unknown interfaces remain findings rather than invented feasibility."""
    strategies = harbor_street_integration_strategies()
    analysis = analyze_integrations(architecture_analysis(), strategies, integration_questions())
    assert tuple(item.identifier for item in analysis.strategies) == tuple(
        item.identifier for item in strategies
    )
    expected_unknown_interfaces = 4
    assert len(analysis.findings) == expected_unknown_interfaces
    assert all(item.kind == "Unverified External Interface" for item in analysis.findings)
    assert strategies[2].assumptions[0].status.value == "Unverified"
    assert strategies[2].feasibility.value == "Requires validation"
    assert strategies[2].failure_modes
    assert strategies[0].traceability == (
        "E4",
        "REQ-002",
        "CAP-002",
        "CAP-002",
        "APP-003",
        "ARCH-001",
        "FLOW-004",
    )
    assert {item.category for item in analysis.questions} >= {"Authentication", "Authorization"}


def test_validation_detects_each_required_structural_problem() -> None:
    """Malformed candidates produce stable, specific findings."""
    base = harbor_street_integration_strategies()[0]
    analysis = architecture_analysis()
    unsupported = replace(base, architecture_id="ARCH-MISSING")
    assert (
        validate_integration(analysis, unsupported)[0].kind == "Unsupported Architecture Reference"
    )
    malformed = replace(
        base,
        source_id="CMP-MISSING",
        destination_id="CMP-ALSO-MISSING",
        information_flow_id="FLOW-MISSING",
        information=" ",
        traceability=(),
    )
    kinds = {item.kind for item in validate_integration(analysis, malformed)}
    assert kinds == {
        "Missing Source Component",
        "Missing Destination Component",
        "Unjustified Integration",
        "Missing Exchanged Information",
        "Missing Traceability",
    }
    reversed_strategy = replace(base, source_id=base.destination_id, destination_id=base.source_id)
    assert validate_integration(analysis, reversed_strategy)[0].kind == "Contradictory Direction"


def test_duplicate_strategy_identifiers_are_rejected() -> None:
    """Stable identity is required for deterministic output."""
    strategy = harbor_street_integration_strategies()[0]
    with pytest.raises(ValueError, match="identifiers must be unique"):
        analyze_integrations(architecture_analysis(), (strategy, strategy), ())


def test_diagrams_and_report_are_structured_and_neutral() -> None:
    """Generated artifacts use scenario data and do not choose a winner or score."""
    strategies = harbor_street_integration_strategies()
    assert "Confirmed Appointment" in render_integration_boundary_mermaid(strategies[0])
    assert "sequenceDiagram" in render_api_pattern_mermaid(strategies[2])
    assert "Confirmed Lesson Event" in render_event_pattern_mermaid(strategies[4])
    report = render_integration_report(
        analyze_integrations(architecture_analysis(), strategies, integration_questions())
    )
    assert report.startswith("# Integration Strategy Analysis")
    assert "## 18. Educational Limitations" in report
    assert "Existing calendar programmatic interface availability" in report
    assert "Authentication Questions" in report
    assert "Authorization Questions" in report
    assert "recommended pattern" not in report.lower()
    assert "score" in report.lower()  # only the explicit no-scores limitation
    assert "100 ms" not in report


def test_manual_duplicate_and_failure_simulations_are_deterministic() -> None:
    """Tiny simulations expose handoff, idempotency, and recovery questions."""
    assert simulate_manual_handoff() == simulate_manual_handoff()
    assert simulate_manual_handoff()[-1].outcome == "One calendar entry is recorded"
    non_idempotent = simulate_duplicate_delivery(idempotent=False)
    idempotent = simulate_duplicate_delivery(idempotent=True)
    assert non_idempotent[-1].outcome == "Second appointment created"
    assert idempotent[-1].outcome == "Duplicate recognized; no second business effect"
    failure = simulate_destination_failure()
    assert failure[2].outcome == "DESTINATION_UNAVAILABLE"
    assert failure[-1].outcome == "What should happen next?"
