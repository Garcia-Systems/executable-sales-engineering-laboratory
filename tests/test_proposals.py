"""Chapter 16 proposal package tests."""

# ruff: noqa: D103, PLR2004, PT018, RUF005

from dataclasses import FrozenInstanceError, replace

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.proposals import render_proposal_mermaid
from sales_lab.domain.proposals import (
    CommercialPlaceholder,
    CommercialStatus,
    ProposalLifecycle,
    ProposalType,
    ProposedDeliverable,
    ScopeItem,
)
from sales_lab.reports.proposals import (
    render_customer_proposal,
    render_executive_view,
    render_technical_view,
    render_traceability,
)
from sales_lab.services.proposals import (
    build_harbor_street_proposal,
    pricing_experiment,
    scope_expansion_experiment,
    unsupported_promise_experiment,
    validate_proposal,
)


def test_canonical_package_reuses_evidence_and_is_immutable() -> None:
    proposal = build_harbor_street_proposal()
    assert proposal.proposal_type is ProposalType.RECOMMENDATION_PACKAGE
    assert proposal.lifecycle is ProposalLifecycle.DRAFT
    assert not proposal.recommendation.approved
    assert proposal.validation_findings == ()
    assert len(proposal.scope) == 6
    assert proposal.exclusions and proposal.deliverables
    assert proposal.assumptions and proposal.dependencies and proposal.risks
    assert proposal.demonstration_findings
    assert proposal.value_summary.calculation_readiness.startswith("Not ready")
    assert all(item.value is None for item in proposal.commercial_placeholders)
    assert all(
        item.status is CommercialStatus.NOT_ESTABLISHED for item in proposal.commercial_placeholders
    )
    assert "limited validation" in proposal.decision_request.statement
    assert "production implementation" in proposal.decision_request.statement
    with pytest.raises(FrozenInstanceError):
        proposal.engagement = "changed"  # type: ignore[misc]


def test_types_and_lifecycle_teach_non_equivalence() -> None:
    assert "Contract" not in {item.value for item in ProposalType}
    assert "Approval" not in {item.value for item in ProposalType}
    assert len({ProposalLifecycle.PRESENTED, ProposalLifecycle.ACCEPTED}) == 2
    assert set(ProposalType) == {
        ProposalType.DISCOVERY_SUMMARY,
        ProposalType.RECOMMENDATION_PACKAGE,
        ProposalType.VALIDATION_PROPOSAL,
        ProposalType.IMPLEMENTATION_PROPOSAL,
        ProposalType.DECISION_PACKAGE,
    }
    assert len(ProposalLifecycle) == 7


def test_reports_share_conclusion_and_traceability() -> None:
    proposal = build_harbor_street_proposal()
    customer = render_customer_proposal(proposal)
    executive = render_executive_view(proposal)
    technical = render_technical_view(proposal)
    traceability = render_traceability(proposal)
    assert customer == executive
    for heading in (
        "Executive Summary",
        "Scope",
        "Exclusions",
        "Commercial Information",
        "Decision Requested",
        "Limitations",
    ):
        assert heading in customer
    assert proposal.recommendation.statement in customer
    assert "Internal Decision Package" in technical
    assert "No validation findings" in technical
    assert "| SCOPE-001 | REQ-001, REQ-002 | CAP-001 | RC-001 |" in traceability
    assert "Package --> Decision" in render_proposal_mermaid()


def test_experiments_preserve_original() -> None:
    original = build_harbor_street_proposal()
    pricing = pricing_experiment(original)
    assert pricing.original is original
    assert pricing.name == "EXPERIMENTAL COMMERCIAL SCENARIO"
    assert pricing.changed.commercial_placeholders[0].value == "USD 1,000 fictional"
    assert original.commercial_placeholders[0].value is None
    expansion = scope_expansion_experiment(original)
    assert any(
        "Deliverable outside scope" in item for item in expansion.changed.validation_findings
    )
    promise = unsupported_promise_experiment(original)
    assert any(
        "Unsupported outcome promise" in item for item in promise.changed.validation_findings
    )
    assert original.validation_findings == ()


def test_validator_detects_all_inconsistencies() -> None:
    base = build_harbor_street_proposal()
    broken_recommendation = replace(
        base.recommendation, statement="", evidence_ids=(), approved=True
    )
    bad_scope = ScopeItem("BAD", "Unsupported", (), (), (), ())
    bad_deliverable = ProposedDeliverable("BAD-DEL", "Outside", ())
    bad_commercial = CommercialPlaceholder("Pricing", CommercialStatus.NOT_ESTABLISHED, "$0")
    bad_request = replace(
        base.decision_request, statement="Approve production implementation", scope_ids=("MISSING",)
    )
    broken = replace(
        base,
        recommendation=broken_recommendation,
        scope=(bad_scope,),
        exclusions=(),
        deliverables=(bad_deliverable,),
        established_situation=base.established_situation + (base.assumptions[0].statement,),
        commercial_placeholders=(bad_commercial,),
        decision_request=bad_request,
    )
    findings = validate_proposal(broken)
    expected = (
        "no recommendation",
        "no evidence",
        "without traceability",
        "outside scope",
        "Missing exclusions",
        "Invented commercial",
        "without customer authority",
        "inconsistent with scope",
        "production-readiness",
        "presented as fact",
    )
    for phrase in expected:
        assert any(phrase in finding for finding in findings)


def test_empty_report_collections_and_cli() -> None:
    base = build_harbor_street_proposal()
    sparse = replace(base, established_situation=(), validation_findings=("Review",))
    assert "- None" in render_customer_proposal(sparse)
    assert "- Review" in render_technical_view(sparse)
    result = CliRunner().invoke(app, ["proposal"])
    assert result.exit_code == 0
    assert "Harbor Street Music — Sales Engineering Recommendation Package" in result.stdout
    assert "Pricing: NOT ESTABLISHED" in result.stdout
    assert "Proposal Traceability" in result.stdout
    chapters = CliRunner().invoke(app, ["chapters"])
    assert "16. Proposal and Decision Package" in chapters.stdout
