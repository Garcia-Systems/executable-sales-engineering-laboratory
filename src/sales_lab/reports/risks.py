"""Deterministic Markdown rendering for Chapter 13."""

# ruff: noqa: E501

from sales_lab.diagrams.risks import render_risk_lifecycle_mermaid, render_risk_relationship_mermaid
from sales_lab.domain.risks import ResponseType, RiskAnalysis


def _items(values: tuple[str, ...]) -> str:
    return "\n".join(f"- {value}" for value in values) or "- None"


def render_risk_report(analysis: RiskAnalysis) -> str:
    """Render the complete analysis without scoring, ranking, or recommending."""
    register = analysis.register
    risks = "\n\n".join(
        f"### {risk.identifier}: {risk.title}\n- Cause: {risk.cause}\n- Risk event: {risk.event}\n- Consequence: {risk.consequence}\n- Categories: {', '.join(item.value for item in risk.categories)}\n- Status: {risk.status.value}\n- Likelihood: {risk.likelihood.value}\n- Impact: {risk.impact.value}\n- Reason: {risk.evaluation_reason}\n- Risk owner: {risk.owner_role or 'NOT ESTABLISHED'}\n- Evidence: {', '.join(risk.evidence_ids)}"
        for risk in register.risks
    )
    assumptions = "\n".join(
        f"- {item.identifier} — {item.statement} | {item.validation_status.value} | Validation: {item.validation_action.action if item.validation_action else 'NOT PLANNED'} | If false: {item.consequence_if_false}"
        for item in register.assumptions
    )
    dependencies = "\n".join(
        f"- {item.identifier} — {item.statement} | {item.category.value} | {item.status.value} | Owner: {item.owner_role or 'NOT ESTABLISHED'} | Action: {item.resolution_action.action if item.resolution_action else 'NOT PLANNED'}"
        for item in register.dependencies
    )
    constraints = "\n".join(
        f"- {item.identifier} [{item.scope.value}] — {item.statement}"
        for item in register.constraints
    )
    issues = "\n".join(f"- {item.identifier} — {item.statement}" for item in register.issues)
    profiles = "\n".join(
        f"- {profile.approach_name}: "
        + "; ".join(f"{risk_id}={state.value}" for risk_id, state in profile.entries)
        for profile in register.profiles
    )
    responses = "\n".join(
        f"- {item.identifier} / {item.risk_id} / {item.response_type.value}: {item.action} | Role: {item.responsible_role or 'NOT ESTABLISHED'} | Trigger: {item.triggering_condition} | Expected effect: {item.expected_effect} | Remaining uncertainty: {item.remaining_uncertainty}"
        for item in register.responses
    )
    mitigations = (
        "\n".join(
            f"- {item.identifier}: {item.action}"
            for item in register.responses
            if item.response_type is not ResponseType.CONTINGENCY
        )
        or "- None"
    )
    contingencies = (
        "\n".join(
            f"- {item.identifier}: {item.action}"
            for item in register.responses
            if item.response_type is ResponseType.CONTINGENCY
        )
        or "- None"
    )
    residual = "\n".join(
        f"- {item.identifier} / {item.risk_id}: {item.statement} ({item.likelihood.value} likelihood; {item.impact.value} impact)"
        for item in register.residual_risks
    )
    findings = "\n".join(
        f"- {item.finding}: {item.subject} — {item.explanation}"
        for item in analysis.classification_findings
    )
    matrix_header = (
        "| Risk | "
        + " | ".join(profile.approach_name for profile in register.profiles)
        + " |\n|---|"
        + "---|" * len(register.profiles)
    )
    matrix_rows = "\n".join(
        "| "
        + risk.identifier
        + " | "
        + " | ".join(dict(profile.entries)[risk.identifier].value for profile in register.profiles)
        + " |"
        for risk in register.risks
    )
    traces = "\n".join("- " + " → ".join(path) for path in register.traceability)
    value = "\n".join(
        f"- {item.value_id} → {item.risk_id}: {item.value_effect}" for item in register.value_links
    )
    return f"""# Risk, Assumption, Dependency, and Constraint Analysis

## 1. Engagement
{register.engagement}

## 2. Analysis Scope
{register.scope}

## 3. Risks
{risks}

## 4. Assumptions Register
{assumptions}

## 5. Dependencies Register
{dependencies}

## 6. Constraints Register
{constraints}

## 7. Current Issues
{issues}

## 8. Approach-Specific Risk Profiles
{profiles}

{matrix_header}
{matrix_rows}

No aggregate risk score or hidden ranking is generated; rows retain authored identifier order.

## 9. Risk Causes and Consequences
{_items(tuple(f"{risk.identifier}: {risk.cause} → {risk.event} → {risk.consequence}" for risk in register.risks))}

## 10. Likelihood and Impact
LOW means limited plausible occurrence/effect; MODERATE means meaningful but bounded; HIGH means material effect; UNKNOWN means evidence cannot support an evaluation; NOT EVALUATED means analysis has not occurred. These dimensions remain separate.

## 11. Risk Responses
{responses}

## 12. Mitigations
{mitigations}

## 13. Contingencies
{contingencies}

## 14. Residual Risks
{residual}

## 15. Unvalidated Assumptions
{_items(tuple(item.identifier for item in analysis.unvalidated_assumptions))}

## 16. Unresolved Dependencies
{_items(tuple(item.identifier for item in analysis.unresolved_dependencies))}

## 17. Risks Without Responses
{_items(tuple(item.identifier for item in analysis.risks_without_responses))}

## 18. Classification Findings
{findings}

Unknown != Risk. UNKNOWN != NOT FEASIBLE. UNKNOWN != ABSENT. Constraint != Risk. Issues describe existing conditions.

## 19. Risk-to-Value Relationships
{value}

## 20. Traceability
{traces}

```mermaid
{render_risk_relationship_mermaid(analysis)}```

```mermaid
{render_risk_lifecycle_mermaid()}```

## 21. Open Questions
{_items(register.open_questions)}

## 22. Educational Limitations
Categories are organizational aids rather than universal standards. Qualitative labels require contextual judgment. This deterministic exercise does not invent risks, rank alternatives, provide production risk advice, estimate probabilities, or recommend a solution.
"""
