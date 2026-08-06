"""Learner-owned Chapter 4 stakeholder debugging laboratory."""

from sales_lab.examples.harbor_street_music import (
    harbor_street_music_business_process,
    harbor_street_music_stakeholder_map,
)
from sales_lab.reports.stakeholders import render_stakeholder_report
from sales_lab.services.stakeholders import analyze_stakeholders


def main() -> None:
    """Trace current-process evidence into an immutable stakeholder report."""
    process = harbor_street_music_business_process()  # Breakpoint 1: Chapter 3 input.
    stakeholder_map = harbor_street_music_stakeholder_map()
    stakeholders = stakeholder_map.roles  # Breakpoint 2: roles are not named people.
    responsibilities = stakeholder_map.responsibilities
    authority = stakeholder_map.authority
    evidence = stakeholder_map.evidence
    perspective_gaps = stakeholder_map.perspective_gaps
    analysis = analyze_stakeholders(process, stakeholder_map)  # Breakpoint 3: validate links.
    report = render_stakeholder_report(analysis)  # Breakpoint 4: inspect stable output.
    immutable_inputs = (stakeholders, responsibilities, authority, evidence, perspective_gaps)
    print(f"Immutable input groups: {len(immutable_inputs)}\n\n{report}", end="")  # noqa: T201


if __name__ == "__main__":
    main()
