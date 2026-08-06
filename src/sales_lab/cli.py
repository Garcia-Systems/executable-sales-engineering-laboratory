"""Command-line interface for the laboratory."""

from typing import Annotated

import typer

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
        "Foundation status: ready for future chapters and simulations."
    )


@app.command()
def chapters() -> None:
    """List the educational chapters available in the laboratory."""
    typer.echo(
        "Chapters\n"
        "No chapters have been published yet. The textbook foundation is ready for future lessons."
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
    message = "Examples\nNo executable examples have been published yet."
    if verbose:
        message += " Future examples will use fixed inputs and reproducible outputs."
    typer.echo(message)


if __name__ == "__main__":  # pragma: no cover - exercised by the installed entry point.
    app()
