"""Deterministic Markdown presentation for Chapter 14."""

# ruff: noqa: E501

from sales_lab.diagrams.decisions import render_decision_mermaid
from sales_lab.domain.decisions import DecisionPackage


def render_comparison_matrix(package: DecisionPackage) -> str:
    """Render qualitative findings without totals, weights, ranking, or a winner."""
    headers = ("Criterion", *(name for _, name in package.approaches))
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    evaluations = {item.approach_id: item for item in package.evaluations}
    for criterion in package.criteria:
        cells = [criterion.criterion_type.value]
        for approach_id, _ in package.approaches:
            finding = next(
                (
                    item
                    for item in evaluations[approach_id].findings
                    if item.criterion_id == criterion.identifier
                ),
                None,
            )
            cells.append(finding.state.value if finding else "Not Evaluated")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _bullets(values: tuple[str, ...]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- None recorded."


def render_decision_report(package: DecisionPackage) -> str:
    """Render all twenty required sections in stable authored order."""
    recommendation = package.recommendation
    approach_names = dict(package.approaches)
    evaluation_lines = tuple(
        f"**{approach_names[evaluation.approach_id]}** — "
        + (
            "; ".join(
                f"{finding.criterion_id}: {finding.state.value} ({finding.reason})"
                for finding in evaluation.findings
            )
            or "Not evaluated."
        )
        for evaluation in package.evaluations
    )
    return f"""# Decision Analysis and Recommendation

## 1. Engagement
{package.engagement}

## 2. Decision Context
{package.context}

## 3. Candidate Approaches
{_bullets(tuple(f"{identifier} — {name}" for identifier, name in package.approaches))}

## 4. Decision Criteria
These criteria are educational and engagement-specific; they need not apply equally elsewhere.
{_bullets(tuple(f"{item.identifier} — {item.criterion_type.value}: {item.description}" for item in package.criteria))}

## 5. Mandatory Conditions
{_bullets(tuple(f"{item.identifier} — {item.status.value}: {item.description}" for item in package.mandatory_conditions if item.kind.value == "Mandatory"))}

## 6. Approach Evaluations
{_bullets(evaluation_lines)}

## 7. Comparison Matrix
{render_comparison_matrix(package)}

There is no total, weight, arithmetic winner, or hidden numeric ranking. The matrix informs judgment; it does not make the decision.

## 8. Evidence Strength
{_bullets(tuple(f"{finding.approach_id}/{finding.criterion_id} — {finding.evidence_strength.value}: {finding.reason}" for evaluation in package.evaluations for finding in evaluation.findings))}

## 9. Stakeholder Perspectives
{_bullets(tuple(f"{item.role_name}: {item.perspective}" for item in package.perspectives))}

## 10. Tradeoffs
{_bullets(tuple(f"Choosing {item.approach_id} accepts {item.accepts} in exchange for {item.in_exchange_for}." for item in package.tradeoffs))}

## 11. Risks and Unknowns
{_bullets(package.risks_and_unknowns)}

## 12. Professional Judgment
{package.professional_judgment.rationale}

Accepted tradeoffs:
{_bullets(package.professional_judgment.accepted_tradeoffs)}

Evidence limitations:
{_bullets(package.professional_judgment.evidence_limitations)}

## 13. Recommendation
**{recommendation.recommendation_type.value}:** {recommendation.statement}

Need addressed: {recommendation.need_addressed}

## 14. Recommendation Conditions
{_bullets(tuple(f"{item.identifier} — {item.description}" for item in recommendation.conditions))}

## 15. Recommendation Confidence
**{recommendation.confidence.level.value}.** {recommendation.confidence.basis}

## 16. Alternatives and Contingencies
{_bullets(tuple(f"{item.role} — {approach_names[item.approach_id]}: {item.description}" for item in recommendation.alternatives))}

## 17. Change Triggers
{_bullets(tuple(f"{item.identifier} — If {item.condition} {item.response}" for item in recommendation.change_triggers))}

## 18. Traceability
{_bullets(tuple(" → ".join(path) for path in package.traceability))}

```mermaid
{render_decision_mermaid(package)}```

## 19. Decision Authority
The laboratory produces a recommendation. It does not approve the recommendation on behalf of the fictional customer. Evidence, analysis, judgment, recommendation, decision, and approval are distinct.

## 20. Educational Limitations
This qualitative, deterministic exercise is not an objective mathematical truth, a customer decision, financial advice, product selection, demonstration, or proof of concept. Professional judgment remains conditional and open to revision.
"""
