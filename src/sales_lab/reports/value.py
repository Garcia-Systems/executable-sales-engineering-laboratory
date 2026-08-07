"""Stable Markdown rendering for Chapter 12."""

# ruff: noqa: E501, RUF001 - educational prose and range typography are intentional.

from sales_lab.diagrams.value import render_value_mermaid
from sales_lab.domain.value import CostTiming, EvidenceStatus, ValueAnalysis, ValueKind
from sales_lab.services.value import total_cost


def _money(value: object) -> str:
    return "Not Established" if value is None else f"USD {value}"


def render_value_report(analysis: ValueAnalysis) -> str:
    """Render canonical unknowns separately from fictional numerical experiments."""
    established_costs = tuple(
        c for c in analysis.costs if c.evidence_status is EvidenceStatus.ESTABLISHED
    )
    estimated_costs = tuple(
        c for c in analysis.costs if c.evidence_status is not EvidenceStatus.ESTABLISHED
    )
    measurable = tuple(b for b in analysis.benefits if b.amount is not None)
    intangible = tuple(b for b in analysis.benefits if b.value_kind is ValueKind.INTANGIBLE)
    lines = [
        "# Cost, Benefit, and Value Analysis",
        "",
        "## 1. Engagement",
        f"- {analysis.engagement}",
        "",
        "## 2. Comparison Baseline",
        f"- Status quo ({analysis.baseline.approach_id}): {analysis.baseline.current_process}",
        "- Unknown costs are not treated as zero.",
        "",
        "## 3. Candidate Approaches",
        *(f"- {identifier}: {name}" for identifier, name in analysis.approach_names),
        "",
        "## 4. Established Costs",
        *(f"- {c.identifier}: {c.description}" for c in established_costs),
    ]
    if not established_costs:
        lines.append("- None established.")
    lines.extend(("", "## 5. Estimated Costs"))
    lines.extend(
        f"- {c.identifier}: {c.description} — {_money(c.amount.expected if c.amount else None)} ({c.evidence_status.value})"
        for c in estimated_costs
    )
    lines.extend(("", "## 6. Recurring Costs"))
    recurring = tuple(c for c in analysis.costs if c.timing is CostTiming.RECURRING)
    lines.extend(
        f"- {c.identifier}: {_money(c.amount)} per {c.period.value if c.period else 'unknown period'}"
        for c in recurring
    )
    lines.extend(("", "## 7. Benefit Hypotheses"))
    lines.extend(
        f"- {b.identifier}: {b.hypothesis} Measurement: {b.measurement_definition}"
        for b in analysis.benefits
    )
    lines.extend(("", "## 8. Measurable Benefits"))
    lines.extend(f"- {b.identifier}: {b.amount} {b.unit.value}" for b in measurable)
    if not measurable:
        lines.append("- None established in the canonical analysis.")
    lines.extend(("", "## 9. Intangible Value"))
    lines.extend(
        f"- {b.identifier}: {b.hypothesis} (not assigned arbitrary money)" for b in intangible
    )
    lines.extend(("", "## 10. Evidence and Assumptions"))
    lines.extend(
        f"- {a.identifier}: {a.statement} — {a.evidence_status.value}; source: {a.source}"
        for a in analysis.assumptions
    )
    lines.extend(("", "## 11. Estimate Ranges"))
    ranged = tuple(c for c in analysis.costs if c.amount is not None)
    for cost in ranged:
        if cost.amount is not None:
            lines.append(  # noqa: PERF401 - condition narrows the optional range for MyPy.
                f"- {cost.identifier}: {cost.amount.minimum}–{cost.amount.maximum} {cost.unit.value}"
            )
    if not ranged:
        lines.append(
            "- Canonical numerical ranges are Not Established; fictional inputs appear only below."
        )
    lines.extend(
        (
            "",
            "## 12. Calculation Readiness",
            f"- {analysis.readiness.value.upper()}",
            f"- Reason: {analysis.readiness_reason}",
            "",
            "## 13. Scenario Analysis",
            "- The following are explicitly fictional experiments, not Harbor Street Music facts or forecasts.",
            "",
            "| Scenario | One-Time Cost | Recurring Cost | Estimated Time Value | Net Value | Simple ROI | Payback Months |",
            "|---|---:|---:|---:|---:|---:|---:|",
        )
    )
    for scenario, metric in analysis.scenarios:
        lines.append(
            f"| {scenario.name} | USD {metric.one_time_cost} | USD {metric.recurring_cost} | USD {metric.estimated_value} | USD {metric.net_value} | {metric.simple_roi if metric.simple_roi is not None else 'Not Calculable'} | {metric.payback_months if metric.payback_months is not None else 'Not Calculable'} |"
        )
    lines.extend(
        (
            "",
            "## 14. Sensitivity Analysis",
            "- Only minutes saved changes. Hours and money use Decimal ROUND_HALF_UP to two decimal places.",
            "",
            "| Minutes Saved | Annual Hours | Estimated Value | Net Value |",
            "|---:|---:|---:|---:|",
        )
    )
    lines.extend(
        f"| {r.minutes_saved} | {r.annual_hours} | USD {r.estimated_value} | USD {r.net_value} |"
        for r in analysis.sensitivity_results
    )
    lines.extend(("", "## 15. Status Quo"))
    lines.extend(f"- Known: {v}" for v in analysis.baseline.known_costs)
    lines.extend(f"- Unknown: {v}" for v in analysis.baseline.unknown_costs)
    lines.extend(f"- Consequence: {v}" for v in analysis.baseline.consequences)
    omitted = tuple(f for f in analysis.findings if f.kind == "Potential omitted cost")
    unsupported = tuple(f for f in analysis.findings if f.kind == "Unsupported benefit claim")
    lines.extend(("", "## 16. Omitted Cost Findings"))
    lines.extend(f"- {f.subject_id}: {f.message}" for f in omitted)
    lines.extend(("", "## 17. Unsupported Benefit Findings"))
    lines.extend(f"- {f.subject_id}: {f.kind}. {f.message}" for f in unsupported)
    lines.extend(
        (
            "",
            "## 18. Financial Metrics",
            f"- Canonical total one-time cost: {_money(total_cost(analysis.costs, CostTiming.ONE_TIME))}",
            f"- Canonical recurring cost: {_money(total_cost(analysis.costs, CostTiming.RECURRING))}",
            "- Canonical net value, payback, and simple ROI: Not Calculable.",
            "- Time made available is not automatically cash savings. New revenue and protected revenue require distinct evidence.",
            "",
            "## 19. Traceability",
        )
    )
    lines.extend(
        f"- {' → '.join((*b.trace_ids, b.identifier, 'Value Analysis'))}" for b in analysis.benefits
    )
    lines.extend(
        ("", "```mermaid", render_value_mermaid().rstrip(), "```", "", "## 20. Open Questions")
    )
    lines.extend(f"- {q}" for q in analysis.open_questions)
    lines.extend(
        (
            "",
            "## 21. Educational Limitations",
            "- The taxonomy is educational, not universal; analysts must avoid double-counting.",
            "- Simple ROI is not a complete investment analysis. No vendor price, recommendation, probability, sales forecast, random distribution, or discounted cash flow is produced.",
            "- Scenario hourly values are labeled opportunity-value assumptions, not employee wages or loaded labor facts.",
            "- This analysis informs a future decision process; it does not select a winning approach.",
            "",
        )
    )
    return "\n".join(lines)
