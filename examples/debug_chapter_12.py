"""Learner-owned Chapter 12 debugging path."""

# ruff: noqa: T201 - learner entry point intentionally prints its artifact.

from sales_lab.reports.value import render_value_report
from sales_lab.services.value import analyze_harbor_street_value

analysis = analyze_harbor_street_value()  # Breakpoint: solution approaches and baseline.
cost_estimates = analysis.costs  # Breakpoint: cost / benefit inputs.
benefit_estimates = analysis.benefits
assumptions = analysis.assumptions
ranges = tuple(cost.amount for cost in cost_estimates)
evidence_status = tuple(item.evidence_status for item in (*cost_estimates, *benefit_estimates))
calculation_readiness = analysis.readiness  # Breakpoint: missing canonical inputs.
scenario, financial_metrics = analysis.scenarios[1]  # Breakpoint: fictional calculation.
sensitivity_results = analysis.sensitivity_results  # Breakpoint: one-variable results.
report = render_value_report(analysis)

if __name__ == "__main__":
    print(report)
