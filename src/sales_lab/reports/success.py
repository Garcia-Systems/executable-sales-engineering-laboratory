"""Stable Chapter 18 Markdown reports and matrices."""

# ruff: noqa: E501 - Markdown table rows and learner-facing prose are intentionally readable.

from sales_lab.diagrams.success import render_success_lifecycle, render_success_loop
from sales_lab.domain.success import CustomerSuccessReview, MeasureType, SuccessMeasurementPlan


def render_measurement_matrix(plan: SuccessMeasurementPlan) -> str:
    """Render transparent qualitative readiness without a score or ranking."""
    lines = [
        "| Measure | Type | Requirement | Baseline | Evidence Source | Owner | Readiness |",
        "|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {m.identifier} {m.name} | {m.measure_type.value} | {', '.join(m.requirement_ids)} | {m.baseline.status.value} | {m.evidence_source.name} | {m.owner.role} | {m.readiness.value} |"
        for m in plan.measures
    )
    return "\n".join(lines) + "\n"


def render_benefit_matrix(plan: SuccessMeasurementPlan) -> str:
    """Render readiness of reused Chapter 12 hypotheses."""
    lines = [
        "| Benefit Hypothesis | Baseline Ready? | Follow-Up Measure Ready? | Current Status | Limitations |",
        "|---|---|---|---|---|",
    ]
    for item in plan.benefit_validations:
        baseline_ready = "No" if "not" in item.required_baseline.casefold() else "Partial"
        followup = "No" if item.follow_up_measure_id == "OWNER_NOT_ESTABLISHED" else "Yes"
        lines.append(
            f"| {item.benefit_id}: {item.hypothesis} | {baseline_ready} | {followup} | {item.validation_status.value} | {'; '.join(item.limitations)} |"
        )
    return "\n".join(lines) + "\n"


def render_success_plan(plan: SuccessMeasurementPlan) -> str:
    """Render the canonical planned review, never post-implementation results."""
    groups = {
        kind: tuple(m for m in plan.measures if m.measure_type is kind) for kind in MeasureType
    }
    lines = [
        "# Customer Success and Outcome Measurement Plan",
        "",
        "## 1. Engagement",
        f"- {plan.engagement}",
        "",
        "## 2. Measurement Purpose",
        f"- {plan.purpose}",
        "",
        "## 3. Lifecycle Status",
        f"- {plan.lifecycle_status}: no approval, implementation, adoption, or operational result is claimed.",
        "- DELIVERED != IMPLEMENTED != AVAILABLE != ADOPTED != USED_CORRECTLY != OPERATIONALLY_EFFECTIVE != OUTCOME_OBSERVED != VALUE_VALIDATED.",
        "",
        "## 4. Intended Outcomes",
        *(f"- {key}: {value}" for key, value in plan.intended_outcomes),
        "",
        "## 5. Success Measures",
        *(f"- {m.identifier}: {m.name} ({m.measure_type.value})" for m in plan.measures),
        "",
        "## 6. Measure Definitions",
    ]
    for measure in plan.measures:
        lines.extend(
            (
                f"### {measure.identifier} — {measure.name}",
                f"- Purpose: {measure.purpose}",
                f"- Definition: {measure.definition}",
                f"- Unit: {measure.unit}",
                f"- Indicator: {measure.indicator_timing.value}",
                f"- Limitations: {'; '.join(measure.limitations)}",
            )
        )
    lines.extend(
        (
            "",
            "## 7. Baselines",
            "- Missing baseline != zero.",
            *(
                f"- {m.identifier}: {m.baseline.status.value} — {m.baseline.description}"
                for m in plan.measures
            ),
            "",
            "## 8. Target Conditions",
            *(
                f"- {m.identifier}: {m.target_condition.statement} Population: {m.target_condition.population}; exclusions: {m.target_condition.exclusions}; sample: {m.target_condition.sampling_method}; exceptions: {m.target_condition.exception_treatment}."
                for m in plan.measures
            ),
            "",
            "## 9. Evidence Sources",
            *(
                f"- {m.identifier}: {m.evidence_source.name} — limitation: {m.evidence_source.limitation}"
                for m in plan.measures
            ),
            "",
            "## 10. Observation Periods",
            *(
                f"- {m.identifier}: {m.observation_period.period_type.value} / {m.observation_period.identifier}"
                for m in plan.measures
            ),
            "",
            "## 11. Measurement Ownership",
            *(f"- {m.identifier}: {m.owner.role}" for m in plan.measures),
        )
    )
    for number, title, kind in (
        (12, "Adoption Measures", MeasureType.ADOPTION),
        (13, "Process Measures", MeasureType.PROCESS),
        (14, "Outcome Measures", MeasureType.OUTCOME),
        (15, "Value Measures", MeasureType.VALUE),
    ):
        lines.extend(
            ("", f"## {number}. {title}", *(f"- {m.identifier}: {m.name}" for m in groups[kind]))
        )
        if not groups[kind]:
            lines.append("- None proposed.")
    lines.extend(
        (
            "",
            "## 16. Benefit Hypotheses",
            render_benefit_matrix(plan).rstrip(),
            "",
            "## 17. Measurement Readiness",
            render_measurement_matrix(plan).rstrip(),
            "",
            "## 18. Unintended Consequences to Monitor",
            *(
                f"- {x.identifier}: {x.effect_to_monitor} (not observed in the canonical scenario)"
                for x in plan.unintended_consequences
            ),
            "",
            "## 19. Corrective Actions",
            *(
                f"- {x.identifier}: IF {x.trigger}, THEN {x.action} Decision owner: {x.decision_owner.role}; executed: {x.executed}."
                for x in plan.corrective_actions
            ),
            "",
            "## 20. Traceability",
            "| Evidence | Requirement | Success Criterion | Recommendation | Scope | Measure | Baseline | Observed Evidence | Outcome | Value | Corrective Action |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
            *(
                f"| {x.evidence_id} | {x.requirement_id} | {x.success_criterion_id} | {x.recommendation_id} | {x.scope_id} | {x.measure_id} | {x.baseline_status.value} | {x.observed_evidence} | {x.outcome_finding} | {x.value_validation} | {x.corrective_action_id} |"
                for x in plan.traceability
            ),
            "",
            "## 21. Review Plan",
            *(f"- {x}" for x in plan.next_review_actions),
            "",
            "## 22. Open Questions",
            *(f"- {x}" for x in plan.open_questions),
            "",
            "## 23. Educational Limitations",
            "- Categories are educational, not universal. Leading indicators do not guarantee outcomes. Acceptance is necessary but not sufficient for success.",
            "- Login and update counts are activity evidence, not customer success by themselves. No health score, hidden ranking, telemetry, or causal claim is generated.",
            "",
            "## Customer-Success Learning Loop",
            "```mermaid",
            render_success_loop().rstrip(),
            "```",
            "The loop supports learning and adjustment; it does not guarantee progression.",
            "",
            "## Measurement Lifecycle",
            "```mermaid",
            render_success_lifecycle().rstrip(),
            "```",
        )
    )
    return "\n".join(lines) + "\n"


def render_success_review(review: CustomerSuccessReview) -> str:
    """Render one explicitly fictional review package."""
    lines = [
        "# Customer Success Review Report",
        "",
        f"- Classification: {review.classification}",
        f"- Scenario: {review.scenario}",
        "",
        "## Observations",
        *(
            f"- {x.measure_id} / {x.period_id}: {x.numerator} of {x.denominator} {x.unit}"
            for x in review.observations
        ),
        "",
        "## Outcome Findings",
        *(
            f"- {x.measure_id}: {x.statement} State: {x.state.value}; causality: {x.causality.value}."
            for x in review.outcome_findings
        ),
        "",
        "## Benefit Validation",
        *(
            f"- {x.benefit_id}: {x.validation_status.value}; observed: {x.observed_result or 'None'}"
            for x in review.benefit_validation
        ),
        "",
        "## Unintended Effects",
        *(
            f"- {x.identifier}: observed={x.observed}; {x.effect_to_monitor}"
            for x in review.unintended_effects
        ),
        "",
        "## Corrective Actions",
        *(
            f"- {x.identifier}: {x.action}; executed={x.executed}"
            for x in review.corrective_actions
        ),
        "",
        "## Limitations",
        *(f"- {x}" for x in review.limitations),
        "",
        "## Next Review Decision",
        f"- {review.next_review_decision}",
    ]
    for heading in ("## Benefit Validation", "## Unintended Effects", "## Corrective Actions"):
        index = lines.index(heading)
        if index + 1 == len(lines) or lines[index + 1].startswith("##"):
            lines.insert(index + 1, "- None in this experiment.")
    return "\n".join(lines) + "\n"
