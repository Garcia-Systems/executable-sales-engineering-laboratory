"""Chapter 17 implementation handoff tests."""

# ruff: noqa: D103, PLR2004, PT018

from dataclasses import FrozenInstanceError, replace

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.handoffs import render_handoff_mermaid, render_lifecycle_mermaid
from sales_lab.domain.handoffs import (
    AcceptanceStatus,
    ConditionStatus,
    ConditionType,
    DeliveryReadiness,
    DeliveryScopeItem,
    DiscoveryStage,
    HandoffType,
    LifecycleStatus,
    ResponsibilityCategory,
    ScopeStatus,
)
from sales_lab.reports.handoffs import render_handoff_checklist, render_handoff_report
from sales_lab.services.handoffs import (
    approval_experiment,
    assess_delivery_readiness,
    build_harbor_street_handoff,
    failed_integration_experiment,
    owner_assignment_experiment,
    unsupported_scope_experiment,
)


def test_handoff_domain_is_immutable_and_states_are_distinct() -> None:
    handoff = build_harbor_street_handoff()
    with pytest.raises(FrozenInstanceError):
        handoff.engagement = "changed"  # type: ignore[misc]
    assert set(HandoffType) == {
        HandoffType.DISCOVERY_HANDOFF,
        HandoffType.TECHNICAL_HANDOFF,
        HandoffType.IMPLEMENTATION_HANDOFF,
        HandoffType.VALIDATION_HANDOFF,
        HandoffType.SUPPORT_HANDOFF,
    }
    lifecycle_boundaries = {
        LifecycleStatus.RECOMMENDED,
        LifecycleStatus.APPROVED,
        LifecycleStatus.READY_FOR_DELIVERY,
        LifecycleStatus.IMPLEMENTED,
        LifecycleStatus.VALIDATED,
    }
    assert len(lifecycle_boundaries) == 5
    demonstration_and_acceptance = {"DEMONSTRATED", AcceptanceStatus.NOT_ACCEPTED.value}
    assert len(demonstration_and_acceptance) == 2
    assert set(DeliveryReadiness) == {
        DeliveryReadiness.READY,
        DeliveryReadiness.CONDITIONALLY_READY,
        DeliveryReadiness.NOT_READY,
        DeliveryReadiness.ON_HOLD,
        DeliveryReadiness.NOT_EVALUATED,
    }


def test_canonical_handoff_reuses_baselines_without_approval() -> None:
    handoff = build_harbor_street_handoff()
    package = assess_delivery_readiness(handoff)
    assert handoff.handoff_type is HandoffType.IMPLEMENTATION_HANDOFF
    assert handoff.lifecycle_status is LifecycleStatus.PROPOSED
    assert all(item.status is ScopeStatus.PROPOSED for item in handoff.scope_items)
    assert handoff.requirements_baseline.identifier == "HSM-REQ-BASELINE-v1"
    assert "REQ-001" in handoff.requirements_baseline.included_ids
    assert handoff.requirements_baseline.unresolved
    assert handoff.architecture_baseline.candidate_id == "ARCH-001"
    assert not handoff.architecture_baseline.final
    assert handoff.integration_readiness[0].feasibility == "Requires validation"
    assert handoff.automation_readiness and handoff.acceptance_baseline
    assert all(item.status is AcceptanceStatus.NOT_ACCEPTED for item in handoff.acceptance_baseline)
    assert handoff.demonstration_findings
    assert package.readiness is DeliveryReadiness.NOT_READY
    assert package.blocking_findings and package.non_blocking_follow_up
    assert not package.unsupported_scope and not package.unsupported_commitments
    assert any(
        item.condition is ConditionType.SCOPE_APPROVED
        and item.status is ConditionStatus.UNSATISFIED
        for item in package.readiness_conditions
    )


def test_decisions_discovery_responsibility_and_change_control_are_explicit() -> None:
    handoff = build_harbor_street_handoff()
    assert all(item.owner == "OWNER_NOT_ESTABLISHED" for item in handoff.unresolved_decisions)
    assert {item.stage for item in handoff.technical_discovery} == {
        DiscoveryStage.PRE_IMPLEMENTATION_DISCOVERY,
        DiscoveryStage.IMPLEMENTATION_DISCOVERY,
    }
    assert any(item.blocking for item in handoff.technical_discovery)
    assert all(
        item.category is ResponsibilityCategory.NOT_ESTABLISHED for item in handoff.responsibilities
    )
    assert {item.area for item in handoff.responsibilities} >= {
        "business process",
        "technical delivery",
        "acceptance",
        "maintenance",
        "support",
    }
    assert "New behavior" in handoff.change_control.scope_change
    assert "Wording" in handoff.change_control.clarification
    assert handoff.artifacts and all(item.limitation for item in handoff.artifacts)


def test_approval_does_not_resolve_technical_or_ownership_blockers() -> None:
    original = build_harbor_street_handoff()
    changed = approval_experiment(original)
    assert changed.handoff.lifecycle_status is LifecycleStatus.APPROVED
    assert any(item.status is ScopeStatus.APPROVED for item in changed.handoff.scope_items)
    assert any(item.status is ScopeStatus.PROPOSED for item in changed.handoff.scope_items)
    assert changed.readiness is DeliveryReadiness.CONDITIONALLY_READY
    assert any("calendar" in item.statement.casefold() for item in changed.blocking_findings)
    assert any("Assign" in item.statement for item in changed.blocking_findings)
    assert original.lifecycle_status is LifecycleStatus.PROPOSED
    assert all(item.status is ScopeStatus.PROPOSED for item in original.scope_items)


def test_owner_assignment_resolves_only_owner_findings() -> None:
    original = build_harbor_street_handoff()
    changed = owner_assignment_experiment(original)
    condition = next(
        item
        for item in changed.readiness_conditions
        if item.condition is ConditionType.OWNERS_ASSIGNED
    )
    validation = next(
        item
        for item in changed.readiness_conditions
        if item.condition is ConditionType.VALIDATION_PLAN_DEFINED
    )
    assert condition.status is ConditionStatus.SATISFIED
    assert validation.status is ConditionStatus.SATISFIED
    assert changed.readiness is DeliveryReadiness.NOT_READY
    assert original.responsibilities[0].role == "OWNER_NOT_ESTABLISHED"


def test_scope_and_commitment_guardrails() -> None:
    original = build_harbor_street_handoff()
    changed = unsupported_scope_experiment(original)
    assert (
        changed.unsupported_scope[0].statement
        == "Unsupported delivery scope: Native mobile application"
    )
    assert original.delivery_items == ()
    commitment = replace(
        original,
        commitments=(
            "The integration will be completed in two weeks.",
            "Documentation will be clear.",
        ),
    )
    assessed = assess_delivery_readiness(commitment)
    assert len(assessed.unsupported_commitments) == 1
    assert "Unsupported presales commitment" in assessed.unsupported_commitments[0].statement
    traced = replace(
        original,
        delivery_items=(
            DeliveryScopeItem(
                "SCOPE-001", "Clarification", ScopeStatus.UNDER_REVIEW, ("SCOPE-001",)
            ),
        ),
    )
    assert not assess_delivery_readiness(traced).unsupported_scope


def test_failed_integration_is_localized() -> None:
    original = build_harbor_street_handoff()
    changed = failed_integration_experiment(original)
    assert changed.handoff.integration_readiness[0].feasibility == "Not feasible"
    statuses = {item.identifier: item.status for item in changed.handoff.scope_items}
    assert statuses["SCOPE-006"] is ScopeStatus.DEFERRED
    assert statuses["SCOPE-001"] is ScopeStatus.PROPOSED
    assert original.integration_readiness[0].feasibility == "Requires validation"


def test_ready_boundary_requires_every_condition() -> None:
    base = build_harbor_street_handoff()
    roles = tuple(
        replace(item, role="Established role", category=ResponsibilityCategory.RESPONSIBLE)
        for item in base.responsibilities
    )
    ready = replace(
        base,
        scope_items=tuple(replace(item, status=ScopeStatus.APPROVED) for item in base.scope_items),
        architecture_baseline=replace(base.architecture_baseline, final=True),
        integration_readiness=tuple(
            replace(item, feasibility="Established") for item in base.integration_readiness
        ),
        responsibilities=roles,
        acceptance_baseline=tuple(
            replace(item, validating_role="Acceptance role") for item in base.acceptance_baseline
        ),
        change_control=replace(base.change_control, approval_authority="Decision authority"),
    )
    package = assess_delivery_readiness(ready)
    assert package.readiness is DeliveryReadiness.READY
    assert not package.blocking_findings
    assert package.next_actions == ("Begin delivery within the approved baseline.",)


def test_reports_checklist_diagrams_and_cli() -> None:
    package = assess_delivery_readiness(build_harbor_street_handoff())
    report = render_handoff_report(package)
    for heading in (
        "Lifecycle Status",
        "Proposed Scope",
        "Approved Scope",
        "Requirements Baseline",
        "Architecture Baseline",
        "Acceptance Baseline",
        "Blocking Conditions",
        "Traceability",
        "Next Decision",
        "Educational Limitations",
    ):
        assert f"## {heading}" in report
    assert "No numeric readiness score is calculated" in report
    assert "% ready" not in report.casefold()
    checklist = render_handoff_checklist(package)
    assert "| Readiness Condition | Status | Evidence | Blocking? | Next Action |" in checklist
    assert "82%" not in checklist
    assert "Decision -->|Approved Scope| Baseline" in render_handoff_mermaid()
    assert "Implemented --> Validated" in render_lifecycle_mermaid()
    result = CliRunner().invoke(app, ["handoff"])
    assert result.exit_code == 0
    assert "Lifecycle Status" in result.stdout
    assert "NOT_READY" in result.stdout
    assert "OWNER_NOT_ESTABLISHED" in result.stdout
    assert "Acceptance Baseline" in result.stdout
    chapters = CliRunner().invoke(app, ["chapters"])
    assert "17. Implementation Handoff and Delivery Readiness" in chapters.stdout
