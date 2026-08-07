"""Debugger entry point for Chapter 15 demonstration evidence."""

import sys

from sales_lab.reports.demonstrations import render_demonstration_report
from sales_lab.services.demonstrations import (
    execute_harbor_street_demonstration,
    harbor_street_demonstration_plan,
)

demonstration_plan = harbor_street_demonstration_plan()  # Breakpoint: recommendation → objective.
objective = demonstration_plan.objective
scenario = demonstration_plan.scenario  # Breakpoint: inspect fictional inputs.
steps = demonstration_plan.steps
report = execute_harbor_street_demonstration(demonstration_plan)  # Breakpoint: execute.
state = report.evidence_artifacts[0]
evidence_artifacts = report.evidence_artifacts
observed_results = report.observed_results  # Breakpoint: observation != interpretation.
findings = report.findings
limitations = demonstration_plan.limitations
coverage = (report.requirement_coverage, report.condition_coverage)
markdown = render_demonstration_report(report)  # Breakpoint: finding → limitation.

if __name__ == "__main__":
    sys.stdout.write(markdown)
