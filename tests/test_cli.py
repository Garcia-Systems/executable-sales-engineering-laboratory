"""Tests for the command-line interface."""

from typer.testing import CliRunner

from sales_lab.cli import app

runner = CliRunner()


def test_info_describes_the_laboratory() -> None:
    """The info command identifies the current deterministic status."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "deterministic" in result.stdout
    assert "Chapter 0 status" in result.stdout


def test_chapters_lists_chapter_zero() -> None:
    """The chapter catalog includes Chapter 0."""
    result = runner.invoke(app, ["chapters"])
    assert result.exit_code == 0
    assert "0. Setting Up the Sales Engineering Laboratory" in result.stdout


def test_examples_lists_harbor_street_music() -> None:
    """The example catalog includes the first fictional customer."""
    result = runner.invoke(app, ["examples"])
    assert result.exit_code == 0
    assert "Harbor Street Music" in result.stdout


def test_examples_verbose_explains_reproducibility() -> None:
    """Verbose output describes fixed inputs."""
    result = runner.invoke(app, ["examples", "--verbose"])
    assert result.exit_code == 0
    assert "fixed customer-supplied inputs and reproducible output" in result.stdout


def test_situation_prints_report_without_recommendation() -> None:
    """The situation command prints the bounded report."""
    result = runner.invoke(app, ["situation"])
    assert result.exit_code == 0
    assert result.stdout.startswith("# Customer Situation Summary")
    assert "Harbor Street Music" in result.stdout
    assert "CRM" not in result.stdout


def test_root_command_displays_help() -> None:
    """Root help exposes the scenario command."""
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "situation" in result.stdout
