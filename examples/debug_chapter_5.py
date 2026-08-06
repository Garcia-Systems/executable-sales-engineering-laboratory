"""Learner-owned Chapter 5 requirements debugging entry point."""
# ruff: noqa: S101, T201

from sales_lab.examples.harbor_street_music import (
    harbor_street_music_requirements,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.requirements import render_requirements_report, render_traceability_matrix
from sales_lab.services.requirements import analyze_requirements


def main() -> None:
    """Trace evidence through validation, criteria, and the matrix."""
    requirement_set = harbor_street_music_requirements()
    stakeholder_map = harbor_street_music_stakeholder_map()
    requirement = requirement_set.requirements[0]
    requirement_type = requirement.requirement_type
    source_evidence = requirement.source_evidence_ids
    stakeholder = requirement.stakeholder_id
    acceptance_criteria = requirement.acceptance_criteria
    analysis = analyze_requirements(requirement_set, stakeholder_map)  # Breakpoint: validation.
    validation_findings = analysis.findings
    matrix = render_traceability_matrix(analysis)  # Breakpoint: traceability matrix.
    report = render_requirements_report(analysis)
    inspect = (
        requirement,
        requirement_type,
        source_evidence,
        stakeholder,
        acceptance_criteria,
        validation_findings,
        matrix,
    )
    assert inspect
    print(report, end="")


if __name__ == "__main__":
    main()
