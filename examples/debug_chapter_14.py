"""Learner-owned Chapter 14 debugging entry point."""

# ruff: noqa: S101, T201

from sales_lab.reports.decisions import render_decision_report
from sales_lab.services.decisions import harbor_street_decision_package


def main() -> None:
    """Step through evidence-bounded analysis into an explicit recommendation."""
    package = harbor_street_decision_package()  # Breakpoint: approaches and criteria.
    approaches = package.approaches
    criteria = package.criteria
    findings = package.evaluations  # Breakpoint: findings and mandatory_conditions.
    mandatory_conditions = package.mandatory_conditions
    tradeoffs = package.tradeoffs
    evidence_strength = tuple(
        finding.evidence_strength for evaluation in findings for finding in evaluation.findings
    )
    professional_judgment = package.professional_judgment  # Breakpoint: explicit judgment.
    recommendation = package.recommendation
    conditions = recommendation.conditions
    alternatives = recommendation.alternatives
    change_triggers = recommendation.change_triggers
    report = render_decision_report(package)  # Breakpoint: conditional recommendation.
    assert all((approaches, criteria, mandatory_conditions, tradeoffs, evidence_strength))
    assert all((professional_judgment, recommendation, conditions, alternatives, change_triggers))
    print(report)


if __name__ == "__main__":
    main()
