"""Markdown presentation for Chapter 15 evidence."""

# ruff: noqa: E501

from sales_lab.diagrams.demonstrations import (
    render_demonstration_lifecycle,
    render_demonstration_sequence,
)
from sales_lab.domain.demonstrations import DemonstrationReport


def _bullets(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None."


def render_demonstration_report(report: DemonstrationReport) -> str:
    """Render all evidence in stable authored order and preserve epistemic boundaries."""
    plan = report.plan
    audience = tuple(f"**{item.role_name}:** {item.participation_reason}" for item in plan.audience)
    scenario = (
        f"- Inquiry: {plan.scenario.inquiry_id}",
        f"- Prospective student: {plan.scenario.prospective_student}",
        f"- Instrument: {plan.scenario.instrument}",
        f"- Initial status: {plan.scenario.initial_status}",
        f"- Requested availability: {plan.scenario.requested_availability}",
    )
    steps = tuple(f"{step.order}. **{step.identifier}:** {step.action}" for step in plan.steps)
    successes = tuple(
        f"**{item.identifier}:** {item.description}" for item in plan.success_conditions
    )
    failures = tuple(
        f"**{item.identifier}:** {item.description}" for item in plan.failure_conditions
    )
    evidence = tuple(
        f"**{item.identifier} ({item.artifact_type}):** {item.content}"
        for item in report.evidence_artifacts
    )
    observed = tuple(f"**{item.step_id}:** {item.observation}" for item in report.observed_results)
    findings = tuple(
        f"**{item.identifier} — {item.state}:** {item.description}" for item in report.findings
    )
    conditions_yes = tuple(
        f"{item.source_id}: {item.coverage} — {item.finding}"
        for item in report.condition_coverage
        if item.finding != "Not Demonstrated"
    )
    conditions_no = tuple(
        f"{item.source_id}: {item.coverage} — {item.finding}"
        for item in report.condition_coverage
        if item.finding == "Not Demonstrated"
    )
    pocs = tuple(
        f"**{item.identifier} — {item.status}:** {item.question} Evidence needed: {item.evidence_needed}"
        for item in report.poc_questions
    )
    limitations = tuple(item.description for item in plan.limitations)
    traces = tuple(
        f"{item.source_id} → {item.step_id} → {item.evidence_id} → {item.finding}"
        for item in (*report.requirement_coverage, *report.condition_coverage)
    )
    return f"""# Technical Demonstration and Proof-of-Concept Report

## 1. Engagement
{plan.engagement}

## 2. Demonstration Type
{plan.demonstration_type}

## 3. Question Being Answered
{plan.objective.question}

## 4. Objective
{plan.objective.statement}

## 5. Audience
{_bullets(audience)}

## 6. Scope
{_bullets(plan.scope)}

## 7. Exclusions
{_bullets(plan.exclusions)}

## 8. Requirements and Conditions Tested
{_bullets(plan.objective.trace_ids)}

## 9. Scenario Data
{chr(10).join(scenario)}

All data is fictional, educational, and deterministic.

## 10. Demonstration Steps
{chr(10).join(steps)}

## 11. Success Conditions
{_bullets(successes)}

## 12. Failure Conditions
{_bullets(failures)}

## 13. Evidence Artifacts
{_bullets(evidence)}

## 14. Observed Results
{_bullets(observed)}

## 15. Findings
{_bullets(findings)}

Passing means only: demonstration objective satisfied for the defined deterministic scenario.
Production readiness requires broader evidence. Production ready: **{str(report.production_ready).lower()}**.

## 16. Conditions Demonstrated
{_bullets(conditions_yes)}

## 17. Conditions Not Demonstrated
{_bullets(conditions_no)}

## 18. Proof-of-Concept Questions
{_bullets(pocs)}

## 19. Limitations
{_bullets(limitations)}

## 20. Unsupported Claims
{_bullets(report.unsupported_claims)}

## 21. Traceability
{_bullets(traces)}

## 22. Recommended Follow-Up
- Execute POC-001 only with a supported test interface and authorization.
- Collect stakeholder workflow feedback and Chapter 14 baseline success measures.
- Preserve failed and inconclusive findings for the later decision.

## 23. Educational Limitations
This in-memory model performs no external action. It is not a pilot or production implementation,
and scripted success is not independent validation.

### Sequence Diagram
```mermaid
{render_demonstration_sequence(plan)}```

### Demonstration Lifecycle
```mermaid
{render_demonstration_lifecycle()}```
"""
