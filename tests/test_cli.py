"""Tests for the command-line interface."""

import subprocess
from shutil import which

from typer.testing import CliRunner

from sales_lab.cli import app

runner = CliRunner()


def test_installed_cli_entry_point_runs() -> None:
    """The packaged console script can execute a harmless command."""
    executable = which("sales-lab")
    assert executable is not None
    result = subprocess.run(  # noqa: S603 - path is resolved from the installed environment.
        [executable, "info"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Executable Sales Engineering Laboratory" in result.stdout


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
    assert "1. Customer Problems vs. Customer Symptoms" in result.stdout
    assert "3. Business Process Modeling" in result.stdout
    assert "6. Capability Mapping" in result.stdout


def test_capabilities_prints_vendor_neutral_analysis() -> None:
    """The Chapter 6 command exposes mappings, coverage, gaps, and guardrails."""
    result = runner.invoke(app, ["capabilities"])
    assert result.exit_code == 0
    assert result.stdout.startswith("# Capability Mapping Analysis")
    assert "## Capability Gaps" in result.stdout
    assert "## Unsupported Capabilities" in result.stdout
    assert "Inquiry Status Tracking" in result.stdout
    assert "Salesforce" not in result.stdout


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


def test_root_help_displays_scenario_command() -> None:
    """Root help exposes the scenario command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "situation" in result.stdout


def test_investigate_prints_initial_discovery_assessment() -> None:
    """The Chapter 1 command prints the fixed evidence-bounded report."""
    result = runner.invoke(app, ["investigate"])
    assert result.exit_code == 0
    assert result.stdout.startswith("# Initial Discovery Assessment")
    assert "Students keep slipping through the cracks." in result.stdout
    assert "## Known Facts" in result.stdout
    assert "No product, solution, outcome, score, or recommendation is generated." in result.stdout


def test_process_prints_summary_mermaid_and_current_state_report() -> None:
    """The Chapter 3 command presents all three deterministic outputs."""
    result = runner.invoke(app, ["process"])
    assert result.exit_code == 0
    assert result.stdout.startswith("Workflow Summary")
    assert "flowchart TD" in result.stdout
    assert "# Current-State Business Process" in result.stdout
    assert "Unknown: What happens after the student declines" in result.stdout
    assert "software recommendation" in result.stdout
