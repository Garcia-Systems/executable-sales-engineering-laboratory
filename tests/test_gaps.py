"""Chapter 7 evidence-based gap analysis behavior and educational boundaries."""

from dataclasses import FrozenInstanceError, replace

import pytest

from sales_lab.domain.gaps import CapabilityAssessment, CapabilityState, EvidenceReference, GapType
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_capability_map,
    harbor_street_music_current_capability_inventory,
    harbor_street_music_requirements,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.gaps import render_current_capability_matrix, render_gap_report
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.gaps import GapAnalysis, add_assessment_evidence, analyze_gaps


def canonical_analysis() -> GapAnalysis:
    """Build the canonical analysis from Chapters 4-7 inputs."""
    required = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    return analyze_gaps(required, harbor_street_music_current_capability_inventory())


def test_resources_are_immutable_and_states_are_distinct() -> None:
    """Current resources cannot be rewritten and unknown is not absence."""
    resource = harbor_street_music_current_capability_inventory().resources[0]
    with pytest.raises(FrozenInstanceError):
        resource.name = "Replacement"  # type: ignore[misc]
    distinct_states = {CapabilityState.UNKNOWN, CapabilityState.NOT_AVAILABLE}
    assert len(distinct_states) == len((CapabilityState.UNKNOWN, CapabilityState.NOT_AVAILABLE))


def test_analysis_preserves_capability_order_and_classifies_distinct_gaps() -> None:
    """Derived views follow Chapter 6 order without collapsing gap meanings."""
    analysis = canonical_analysis()
    assert tuple(item.capability_id for item in analysis.assessments) == (
        "CAP-001",
        "CAP-002",
        "CAP-003",
        "CAP-004",
    )
    assert tuple(item.capability_id for item in analysis.partial_capabilities) == (
        "CAP-001",
        "CAP-003",
    )
    assert analysis.unknown_capabilities[0].capability_id == "CAP-002"
    assert tuple(item.gap_type for item in analysis.gaps) == (
        GapType.INFORMATION_GAP,
        GapType.EVIDENCE_GAP,
        GapType.PROCESS_GAP,
    )


def test_provenance_questions_and_traceability_are_explicit() -> None:
    """Questions arise from recorded missing evidence and reports retain prior IDs."""
    analysis = canonical_analysis()
    assessment = analysis.assessments[0]
    assert assessment.evidence_ids == ("E2",)
    assert assessment.missing_evidence is not None
    assert analysis.follow_up_questions[0].startswith("Does the spreadsheet")
    report = render_gap_report(analysis)
    assert "E2 (Harbor Street Music discovery meeting and Chapter 3 process)" in report
    assert "Front Desk Staff → REQ-001 → CAP-001" in report


def test_matrix_and_report_are_deterministic_and_complete() -> None:
    """The stable presentations expose all required educational sections."""
    analysis = canonical_analysis()
    matrix = render_current_capability_matrix(analysis)
    assert matrix.startswith("| Required Capability | Current Resource | Current State | Gap |")
    assert "Inquiry Status Tracking (CAP-001)" in matrix
    assert "Partially Available | Information Gap" in matrix
    report = render_gap_report(analysis)
    for heading in (
        "Required Capabilities",
        "Current Resources",
        "Current Capability Assessments",
        "Capability Matrix",
        "Established Gaps",
        "Partial Capabilities",
        "Unknown Capabilities",
        "Evidence Gaps",
        "Existing Resources Requiring Further Investigation",
        "Follow-Up Questions",
        "Traceability",
        "Educational Limitations",
    ):
        assert f"## {heading}" in report
    assert render_gap_report(analysis) == report
    assert "Gap ≠ Purchase" in report


def test_partial_never_generates_replacement_or_product_recommendation() -> None:
    """A partial capability triggers investigation, not solution selection."""
    report = render_gap_report(canonical_analysis())
    assert "Further investigation required." in report
    assert "REPLACE_EXISTING_SYSTEM" not in report
    assert "Replace spreadsheet" not in report
    assert "Buy CRM" not in report


def test_additional_evidence_creates_new_analysis_without_rewriting_history() -> None:
    """A fictional experiment changes the assessment while preserving the canonical record."""
    original_inventory = harbor_street_music_current_capability_inventory()
    fictional = EvidenceReference(
        "EXP-001",
        "For this experiment only, staff consistently maintain a defined status field.",
        "Chapter 7 fictional evidence experiment",
    )
    revised = CapabilityAssessment(
        "CAP-001",
        ("RES-001", "RES-003"),
        CapabilityState.AVAILABLE,
        ("E2", "EXP-001"),
        "Experimental evidence establishes consistently maintained status tracking.",
    )
    experimental_inventory = add_assessment_evidence(original_inventory, fictional, revised)
    required = canonical_analysis().required
    before = analyze_gaps(required, original_inventory)
    after = analyze_gaps(required, experimental_inventory)
    assert before.assessments[0].state is CapabilityState.PARTIALLY_AVAILABLE
    assert after.assessments[0].state is CapabilityState.AVAILABLE
    assert original_inventory.evidence[-1].identifier == "E7"
    assert experimental_inventory.evidence[-1].identifier == "EXP-001"


def test_invalid_references_and_incomplete_nonavailable_assessments_are_rejected() -> None:
    """Validation prevents untraceable assessments and unexplained negative states."""
    base = harbor_street_music_current_capability_inventory()
    required = canonical_analysis().required
    bad = CapabilityAssessment(
        "CAP-001", ("RES-404",), CapabilityState.AVAILABLE, ("E2",), "Bad reference."
    )
    inventory = type(base)(
        base.engagement, base.resources, base.evidence, (bad, *base.assessments[1:])
    )
    with pytest.raises(ValueError, match="unknown resource"):
        analyze_gaps(required, inventory)
    unexplained = CapabilityAssessment(
        "CAP-001", ("RES-001",), CapabilityState.NOT_AVAILABLE, ("E2",), "Absent."
    )
    inventory = type(base)(
        base.engagement, base.resources, base.evidence, (unexplained, *base.assessments[1:])
    )
    with pytest.raises(ValueError, match="needs a gap and question"):
        analyze_gaps(required, inventory)


def test_inventory_identity_validation() -> None:
    """Engagement and authored identifiers must remain unambiguous."""
    base = harbor_street_music_current_capability_inventory()
    required = canonical_analysis().required
    cases = (
        (replace(base, engagement="Other"), "same engagement"),
        (replace(base, resources=(base.resources[0], base.resources[0])), "resource identifiers"),
        (replace(base, evidence=(base.evidence[0], base.evidence[0])), "evidence identifiers"),
        (
            replace(base, assessments=(base.assessments[0], base.assessments[0])),
            "assessment.*unique",
        ),
    )
    for inventory, message in cases:
        with pytest.raises(ValueError, match=message):
            analyze_gaps(required, inventory)


def test_inventory_rejects_unknown_evidence_capabilities_and_missing_assessments() -> None:
    """Every resource and assessment remains traceable to authored evidence and capabilities."""
    base = harbor_street_music_current_capability_inventory()
    required = canonical_analysis().required
    bad_resource = replace(base.resources[0], evidence_ids=("E-404",))
    with pytest.raises(ValueError, match="resource references unknown evidence"):
        analyze_gaps(required, replace(base, resources=(bad_resource, *base.resources[1:])))
    unknown_capability = replace(base.assessments[0], capability_id="CAP-404")
    with pytest.raises(ValueError, match="unknown capability"):
        analyze_gaps(
            required, replace(base, assessments=(unknown_capability, *base.assessments[1:]))
        )
    with pytest.raises(ValueError, match="lacks an assessment"):
        analyze_gaps(required, replace(base, assessments=base.assessments[:-1]))
    bad_evidence = replace(base.assessments[0], evidence_ids=("E-404",))
    with pytest.raises(ValueError, match="assessment references unknown evidence"):
        analyze_gaps(required, replace(base, assessments=(bad_evidence, *base.assessments[1:])))
