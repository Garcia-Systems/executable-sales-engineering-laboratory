"""End-to-end tests for the Volume I capstone."""

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest
from typer.testing import CliRunner

from sales_lab.cli import app
from sales_lab.diagrams.engagements import (
    render_engagement_mermaid,
    render_traceability_mermaid,
)
from sales_lab.domain.engagements import EngagementStage, StageStatus, TraceLink
from sales_lab.reports.engagements import (
    build_engagement_package,
    export_engagement_package,
    render_engagement_summary,
    render_scenario_comparison,
)
from sales_lab.services.engagements import (
    apply_scenario,
    compare_scenarios,
    diff_scenario,
    integration_feasible_scenario,
    no_budget_scenario,
    premature_custom_build_scenario,
    run_engagement,
    validate_traceability,
)

PACKAGE_DOCUMENT_COUNT = 23
UNSUPPORTED_LAYER_COUNT = 5


def test_canonical_engagement_is_deterministic_and_immutable() -> None:
    """All stages retain explicit lifecycle status and immutable outputs."""
    first = run_engagement()
    second = run_engagement()
    assert first == second
    assert tuple(item.stage for item in first.stage_results) == tuple(EngagementStage)
    assert first.validation_findings == ()
    assert first.result(EngagementStage.HANDOFF).status is StageStatus.COMPLETE_WITH_FINDINGS
    with pytest.raises(FrozenInstanceError):
        first.customer = "changed"  # type: ignore[misc]


def test_dependencies_block_gracefully() -> None:
    """A removed discovery stage blocks its dependents instead of inventing placeholders."""
    engagement = run_engagement(omit_stage=EngagementStage.DISCOVERY)
    assert engagement.result(EngagementStage.DISCOVERY).status is StageStatus.BLOCKED
    assert engagement.result(EngagementStage.PROCESS).status is StageStatus.BLOCKED
    assert engagement.result(EngagementStage.REQUIREMENTS).status is StageStatus.BLOCKED


def test_trace_and_package(tmp_path: Path) -> None:
    """A canonical requirement crosses the full chain and all reports export."""
    engagement = run_engagement()
    identifiers = {link.source_id for link in engagement.trace_links} | {
        link.target_id for link in engagement.trace_links
    }
    assert {"E2", "REQ-001", "CAP-001", "APP-001", "ARCH-001", "REC-001"} <= identifiers
    assert "flowchart TD" in render_engagement_mermaid()
    assert "flowchart LR" in render_traceability_mermaid(engagement)
    assert "Recommendation is not approval" in render_engagement_summary(engagement)
    package = build_engagement_package(engagement)
    paths = export_engagement_package(package, tmp_path)
    assert len(paths) == PACKAGE_DOCUMENT_COUNT
    assert all(path.is_file() for path in paths)


def test_summary_rejects_a_blocked_stage_without_output() -> None:
    """Report composition never substitutes an empty placeholder for a blocked stage."""
    engagement = run_engagement()
    recommendation = engagement.result(EngagementStage.RECOMMENDATION)
    blocked = replace(recommendation, status=StageStatus.BLOCKED, output=None)
    changed_results = tuple(
        blocked if result.stage is EngagementStage.RECOMMENDATION else result
        for result in engagement.stage_results
    )
    with pytest.raises(ValueError, match="Recommendation has no output"):
        render_engagement_summary(replace(engagement, stage_results=changed_results))


def test_trace_validation_detects_empty_and_duplicate_links() -> None:
    """Broken graph construction is reported in learner-friendly terms."""
    assert validate_traceability(())[0].blocking
    link = TraceLink("Evidence", "E2", "supports", "Requirement", "REQ-001")
    assert validate_traceability((link, link))[0].code == "DUPLICATE_LINK"


def test_scenarios_are_isolated_structured_diffs() -> None:
    """Experiments never mutate the canonical engagement or choose a winner."""
    canonical = run_engagement()
    scenario = integration_feasible_scenario()
    changed = apply_scenario(canonical, scenario)
    assert canonical.identifier == "ENG-HSM-001"
    assert changed.identifier.endswith("integration-feasible")
    assert diff_scenario(scenario).added_evidence
    assert "unknown, not zero" in no_budget_scenario().changed_assumptions[0]
    assert len(premature_custom_build_scenario().findings) == UNSUPPORTED_LAYER_COUNT
    report = render_scenario_comparison(compare_scenarios())
    assert "No overall winner" in report
    assert "win probability" not in report.casefold()


def test_engagement_cli_summary_export_and_comparison(tmp_path: Path) -> None:
    """The CLI supports concise output, deterministic export, full output, and comparison."""
    runner = CliRunner()
    summary = runner.invoke(app, ["engagement"])
    assert summary.exit_code == 0
    assert "Traceability validation: PASS" in summary.stdout
    exported = runner.invoke(app, ["engagement", "--output-dir", str(tmp_path)])
    assert exported.exit_code == 0
    assert "Exported 23 reports" in exported.stdout
    full = runner.invoke(app, ["engagement", "--full"])
    assert full.exit_code == 0
    assert "<!-- 00-situation.md -->" in full.stdout
    comparison = runner.invoke(app, ["engagement", "--scenario", "comparison"])
    assert comparison.exit_code == 0
    invalid = runner.invoke(app, ["engagement", "--scenario", "invalid"])
    assert invalid.exit_code != 0
