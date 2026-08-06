"""Command-line interface for the laboratory."""

from typing import Annotated

import typer

from sales_lab.examples.harbor_street_music import harbor_street_music_situation
from sales_lab.reports.markdown import render_situation_summary
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
    typer.echo("Chapters\n0. Setting Up the Sales Engineering Laboratory")


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


if __name__ == "__main__":  # pragma: no cover - exercised by the installed entry point.
    app()
