"""Debugger entry point for Chapter 19's complete evidence chain."""

from sales_lab.services.engagements import (
    apply_scenario,
    integration_feasible_scenario,
    run_engagement,
)

engagement = run_engagement()
stage_results = engagement.stage_results
trace_links = engagement.trace_links
validation_findings = engagement.validation_findings
recommendation = engagement.result(stage_results[14].stage).output
proposal = engagement.result(stage_results[16].stage).output
handoff = engagement.result(stage_results[17].stage).output
measurement_plan = engagement.result(stage_results[18].stage).output
integration_feasible = apply_scenario(engagement, integration_feasible_scenario())

if __name__ == "__main__":
    breakpoint()  # noqa: T100 - this file is intentionally a debugger laboratory.
