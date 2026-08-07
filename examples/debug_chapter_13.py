"""Chapter 13 debugger path from design premises to residual risk."""

# ruff: noqa: T201

from sales_lab.services.risks import analyze_harbor_street_risks


def main() -> None:
    """Expose each reasoning link as a local variable for breakpoint inspection."""
    analysis = analyze_harbor_street_risks()
    risk = analysis.register.risks[0]  # Breakpoint: architecture / integration / automation.
    cause = risk.cause
    event = risk.event
    consequence = risk.consequence
    likelihood = risk.likelihood
    impact = risk.impact
    assumptions = analysis.register.assumptions
    dependencies = analysis.register.dependencies
    constraints = analysis.register.constraints
    response = analysis.register.responses[0]
    residual_risk = analysis.register.residual_risks[0]
    validation_findings = analysis.classification_findings
    print(risk.identifier, cause, event, consequence, likelihood, impact)
    print(assumptions, dependencies, constraints, response, residual_risk, validation_findings)


if __name__ == "__main__":
    main()
