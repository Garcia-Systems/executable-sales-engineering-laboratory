"""Chapter 11 automation boundary tests."""

# ruff: noqa: FBT003, PLR2004, PT018 - literal scenarios and compound outcomes stay readable.

from dataclasses import FrozenInstanceError, replace

import pytest

from sales_lab.diagrams.automation import render_approval_mermaid, render_human_loop_mermaid
from sales_lab.domain.automation import (
    ActivityCharacteristic,
    ApprovalState,
    AutomationMode,
    AutomationReadiness,
    WorkflowActivity,
)
from sales_lab.reports.automation import render_automation_report
from sales_lab.services.automation import (
    ReminderState,
    analyze_harbor_street_automation,
    excessive_automation_experiment,
    harbor_street_automation_plan,
    new_rule_evidence_experiment,
    simulate_approval,
    simulate_exception_routing,
    simulate_reminder,
    validate_automation_plan,
)


def test_model_is_immutable_and_taxonomy_is_explicit() -> None:
    """Objects are frozen and NOT_EVALUATED remains distinct from MANUAL."""
    activity = WorkflowActivity("a", "A", ("inquiry",))
    with pytest.raises(FrozenInstanceError):
        activity.name = "changed"  # type: ignore[misc]
    assert {AutomationMode.NOT_EVALUATED, AutomationMode.MANUAL} <= set(AutomationMode)
    assert len(AutomationMode) == 6
    assert ActivityCharacteristic.REQUIRES_JUDGMENT.value == "Requires judgment"
    assert AutomationReadiness.READY_FOR_DESIGN.value == "Ready for design"


def test_analysis_preserves_authored_order_traceability_and_readiness() -> None:
    """The service validates rather than scoring, ranking, or selecting modes."""
    analysis = analyze_harbor_street_automation()
    assert tuple(a.identifier for a in analysis.plan.assessments) == (
        "AUT-001",
        "AUT-002",
        "AUT-003",
        "AUT-004",
        "AUT-005",
        "AUT-006",
    )
    assert analysis.plan.assessments[0].automation_mode is AutomationMode.RULE_BASED_AUTOMATION
    assert analysis.plan.assessments[4].automation_mode is AutomationMode.HUMAN_DECISION_REQUIRED
    assert analysis.plan.assessments[5].automation_mode is AutomationMode.NOT_EVALUATED
    assert analysis.process.steps[0].identifier == "inquiry"
    assert analysis.architecture_analysis.validations
    assert analysis.integration_analysis.strategies[0].information_flow_id == "FLOW-004"
    assert any(f.kind == "NOT_READY_FOR_AUTOMATION" for f in analysis.findings)
    unsupported = next(f for f in analysis.findings if f.kind == "Unsupported automation proposal")
    assert "ranking of people" in unsupported.message


def test_structural_validation_findings_are_deterministic() -> None:
    """Missing prior evidence, process IDs, roles, and approvers are exposed."""
    base = analyze_harbor_street_automation()
    assessment = base.plan.assessments[2]
    bad = replace(
        assessment,
        activity=replace(assessment.activity, process_step_ids=("missing",)),
        evidence_ids=(),
        human_responsibility=replace(assessment.human_responsibility, role_id="missing"),
        approval_boundary=replace(assessment.approval_boundary, approver_role_id="missing")
        if assessment.approval_boundary
        else None,
    )
    plan = replace(base.plan, assessments=(bad,), unsupported_proposals=())
    result = validate_automation_plan(
        plan, base.process, base.stakeholders, base.architecture_analysis, base.integration_analysis
    )
    assert tuple(f.kind for f in result.findings) == (
        "Missing traceability",
        "Unknown process activity",
        "Unknown accountable role",
        "NOT_READY_FOR_AUTOMATION",
        "Unknown approver",
    )


def test_reminder_is_deterministic_and_idempotent() -> None:
    """The explicit rule creates one reminder business effect and no duplicate."""
    waiting = ReminderState(True, True)
    created = simulate_reminder(waiting)
    assert created.reminder_created
    assert simulate_reminder(created) is created
    assert simulate_reminder(ReminderState(False, True)).reminder_created is False
    assert simulate_reminder(ReminderState(True, False)).reminder_created is False


def test_approval_never_performs_external_action() -> None:
    """Approval permits continuation; rejection and cancellation stop it."""
    approved = simulate_approval(ApprovalState.APPROVED)
    rejected = simulate_approval(ApprovalState.REJECTED)
    cancelled = simulate_approval(ApprovalState.CANCELLED)
    assert approved.eligible_to_continue and not approved.external_action_performed
    assert not rejected.eligible_to_continue and not rejected.external_action_performed
    assert not cancelled.eligible_to_continue
    with pytest.raises(ValueError, match="terminal staff decision"):
        simulate_approval(ApprovalState.AWAITING_APPROVAL)


def test_exception_routing_stops_completion() -> None:
    """A known conflict creates human review instead of forcing an appointment."""
    conflict = simulate_exception_routing(known_conflict=True)
    normal = simulate_exception_routing(known_conflict=False)
    assert conflict == replace(conflict, automatically_completed=False, human_review_created=True)
    assert conflict.review_owner_role_id == "staff"
    assert normal.automatically_completed and not normal.human_review_created


def test_matrices_diagrams_and_report_come_from_structured_data() -> None:
    """Artifacts expose responsibility, approval, exceptions, and limitations."""
    analysis = analyze_harbor_street_automation()
    reminder, approval = analysis.plan.assessments[0], analysis.plan.assessments[2]
    assert "Create follow-up reminder" in render_human_loop_mermaid(reminder)
    assert "AwaitingApproval --> Approved" in render_approval_mermaid(approval)
    with pytest.raises(ValueError, match="no approval boundary"):
        render_approval_mermaid(reminder)
    report = render_automation_report(analysis)
    assert "# Automation Opportunity Analysis" in report
    assert "## 14. Responsibility Matrix" in report
    assert "## Automation Matrix" in report
    assert "E2 → review → REQ-001 → CAP-001" in report
    assert "does not rank people, predict conversion" in report
    assert "score" in report and "recommended mode" not in report.lower()


def test_immutable_experiments_change_evidence_not_desirability() -> None:
    """Experiments produce new plans and preserve the canonical source plan."""
    original = harbor_street_automation_plan()
    excessive = excessive_automation_experiment(original)
    evidenced = new_rule_evidence_experiment(original)
    assert len(original.unsupported_proposals) == 1
    assert len(excessive.unsupported_proposals) == 2
    assert excessive.unsupported_proposals[-1].decision_rule is None
    assert evidenced.unsupported_proposals[-1].decision_rule is not None
    base = analyze_harbor_street_automation()
    excessive_result = validate_automation_plan(
        excessive,
        base.process,
        base.stakeholders,
        base.architecture_analysis,
        base.integration_analysis,
    )
    evidenced_result = validate_automation_plan(
        evidenced,
        base.process,
        base.stakeholders,
        base.architecture_analysis,
        base.integration_analysis,
    )
    assert (
        len([f for f in excessive_result.findings if f.kind == "Unsupported automation proposal"])
        == 2
    )
    assert (
        len([f for f in evidenced_result.findings if f.kind == "Unsupported automation proposal"])
        == 1
    )
