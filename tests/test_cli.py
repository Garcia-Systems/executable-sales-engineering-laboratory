"""Tests for the command-line interface."""

from typer.testing import CliRunner

from sales_lab.cli import app

runner = CliRunner()


def test_info_describes_the_laboratory() -> None:
    """The info command explains the laboratory's deterministic purpose."""
    result = runner.invoke(app, ["info"])

    assert result.exit_code == 0
    assert "deterministic" in result.stdout
    assert "Foundation status" in result.stdout


def test_chapters_explains_that_content_is_forthcoming() -> None:
    """The chapters command is honest about the foundation-only release."""
    result = runner.invoke(app, ["chapters"])

    assert result.exit_code == 0
    assert "No chapters have been published yet" in result.stdout


def test_examples_explains_that_content_is_forthcoming() -> None:
    """The examples command is honest about the foundation-only release."""
    result = runner.invoke(app, ["examples"])

    assert result.exit_code == 0
    assert "No executable examples have been published yet" in result.stdout


def test_examples_verbose_explains_reproducibility() -> None:
    """The verbose examples output reinforces the deterministic design."""
    result = runner.invoke(app, ["examples", "--verbose"])

    assert result.exit_code == 0
    assert "fixed inputs and reproducible outputs" in result.stdout


def test_root_command_displays_help() -> None:
    """Invoking the CLI without a command displays useful help."""
    result = runner.invoke(app)

    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "info" in result.stdout
