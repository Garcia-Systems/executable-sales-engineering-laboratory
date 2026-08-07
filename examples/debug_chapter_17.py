"""Chapter 17 debugging laboratory: inspect proposal-to-delivery governance."""

# ruff: noqa: T201

from sales_lab.reports.handoffs import render_handoff_report
from sales_lab.services.handoffs import assess_delivery_readiness, build_harbor_street_handoff

handoff = build_harbor_street_handoff()  # Breakpoint: proposal scope and approval status.
lifecycle_status = handoff.lifecycle_status
scope_items = handoff.scope_items
approval_status = tuple((item.identifier, item.status) for item in scope_items)
requirements_baseline = handoff.requirements_baseline  # Breakpoint: delivery baselines.
architecture_baseline = handoff.architecture_baseline
integration_readiness = handoff.integration_readiness
responsibilities = handoff.responsibilities
package = assess_delivery_readiness(handoff)  # Breakpoint: conditions become findings.
readiness_conditions = package.readiness_conditions
blocking_findings = package.blocking_findings
next_actions = package.next_actions
report = render_handoff_report(package)  # Breakpoint: immutable delivery package.

print(report)
