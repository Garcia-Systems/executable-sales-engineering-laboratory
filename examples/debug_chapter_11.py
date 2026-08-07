"""Learner-owned Chapter 11 automation debugging laboratory."""

# ruff: noqa: PT018, S101, T201 - assertions and printing make debugger state observable.

from sales_lab.reports.automation import render_automation_report
from sales_lab.services.automation import analyze_harbor_street_automation


def main() -> None:
    """Step through activity, classification, readiness, and human responsibility."""
    analysis = analyze_harbor_street_automation()  # Breakpoint: prior-chapter evidence chain.
    activity = analysis.plan.assessments[0]  # Breakpoint: inspect activity and characteristics.
    automation_mode = activity.automation_mode  # Breakpoint: authored candidate, not inference.
    readiness = activity.readiness  # Breakpoint: inspect unresolved rule and findings.
    human_responsibility = activity.human_responsibility  # Breakpoint: accountability.
    approval_boundary = analysis.plan.assessments[2].approval_boundary
    exception_paths = analysis.plan.assessments[3].exception_paths
    risks = activity.risks
    validation_findings = analysis.findings
    report = render_automation_report(analysis)
    assert all((automation_mode, readiness, human_responsibility, risks))
    assert approval_boundary is not None and exception_paths and validation_findings
    print(report, end="")


if __name__ == "__main__":
    main()
