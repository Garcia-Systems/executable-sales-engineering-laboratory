"""Learner-owned debugger entry point for Chapter 0."""

from typer import echo

from sales_lab.examples.harbor_street_music import harbor_street_music_situation
from sales_lab.reports.markdown import render_situation_summary
from sales_lab.services.situation_summary import build_situation_summary


def main() -> None:
    """Build and display the example while exposing useful debugger variables."""
    situation = harbor_street_music_situation()
    summary = build_situation_summary(situation)  # Place a breakpoint on this assignment.
    report = render_situation_summary(summary)
    echo(report, nl=False)


if __name__ == "__main__":
    main()
