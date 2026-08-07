"""Chapter 18 debugging laboratory: inspect evidence-to-value reasoning."""

# ruff: noqa: T201 - this learner entry point intentionally prints its report.

from sales_lab.reports.success import render_success_plan
from sales_lab.services.success import build_harbor_street_success_plan, experimental_reviews


def main() -> None:
    """Expose stable semantic inspection points rather than fragile line numbers."""
    measurement_plan = build_harbor_street_success_plan()
    measures = measurement_plan.measures
    baseline = measures[0].baseline
    target_condition = measures[0].target_condition
    evidence_source = measures[0].evidence_source
    owner = measures[0].owner
    reviews = experimental_reviews(measurement_plan)
    observations = reviews[0].observations
    outcome_findings = reviews[0].outcome_findings
    benefit_validation = reviews[0].benefit_validation
    unintended_consequences = measurement_plan.unintended_consequences
    corrective_actions = measurement_plan.corrective_actions
    report = render_success_plan(measurement_plan)
    print(report, end="")
    _ = (
        baseline,
        target_condition,
        evidence_source,
        owner,
        observations,
        outcome_findings,
        benefit_validation,
        unintended_consequences,
        corrective_actions,
    )


if __name__ == "__main__":
    main()
