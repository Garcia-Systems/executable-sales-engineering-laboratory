"""Command-line interface for the laboratory."""

from typing import Annotated

import typer

from sales_lab.examples.harbor_street_music import (
    harbor_street_music_discovery,
    harbor_street_music_discovery_meeting,
    harbor_street_music_situation,
)
from sales_lab.reports.markdown import (
    render_discovery_meeting_summary,
    render_initial_discovery_assessment,
    render_situation_summary,
)
from sales_lab.services.discovery_meeting import build_discovery_meeting_summary
from sales_lab.services.investigation import build_initial_discovery_assessment
from sales_lab.services.situation_summary import build_situation_summary

app = typer.Typer(
    help="Explore the executable Sales Engineering laboratory.",
    no_args_is_help=True,
)


@app.command()
def info() -> None:
    """Describe the purpose and current status of the laboratory."""
    typer.echo(
        "Executable Sales Engineering Laboratory\n"
        "A deterministic, code-first environment for learning Sales Engineering.\n"
        "Chapter 0 status: ready; customer facts remain separate from assumptions."
    )


@app.command()
def chapters() -> None:
    """List the educational chapters available in the laboratory."""
    typer.echo(
        "Chapters\n"
        "0. Setting Up the Sales Engineering Laboratory\n"
        "1. Customer Problems vs. Customer Symptoms\n"
        "2. Discovery Meetings"
    )


@app.command()
def examples(
    *,
    verbose: Annotated[
        bool,
        typer.Option(help="Show additional guidance about future examples."),
    ] = False,
) -> None:
    """List deterministic examples available in the laboratory."""
    message = "Examples\nHarbor Street Music — customer situation setup check"
    if verbose:
        message += " Uses fixed customer-supplied inputs and reproducible output."
    typer.echo(message)


@app.command()
def situation() -> None:
    """Print the deterministic Chapter 0 customer situation."""
    summary = build_situation_summary(harbor_street_music_situation())
    typer.echo(render_situation_summary(summary), nl=False)


@app.command()
def investigate() -> None:
    """Print the deterministic Chapter 1 initial discovery assessment."""
    assessment = build_initial_discovery_assessment(harbor_street_music_discovery())
    typer.echo(render_initial_discovery_assessment(assessment), nl=False)


@app.command()
def discovery() -> None:
    """Print the deterministic Chapter 2 discovery meeting summary."""
    meeting = harbor_street_music_discovery_meeting()
    summary = build_discovery_meeting_summary(meeting)
    typer.echo(render_discovery_meeting_summary(summary), nl=False)


if __name__ == "__main__":  # pragma: no cover - exercised by the installed entry point.
    app()
