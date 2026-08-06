"""Tests for deterministic structured and Markdown summaries."""

from sales_lab.examples.harbor_street_music import harbor_street_music_situation
from sales_lab.reports.markdown import render_situation_summary
from sales_lab.services.situation_summary import build_situation_summary


def test_summary_is_deterministic_and_ordered() -> None:
    """Equal inputs yield equal, ordered structured output."""
    situation = harbor_street_music_situation()
    first = build_situation_summary(situation)
    second = build_situation_summary(situation)
    assert first == second
    assert tuple(section.heading for section in first.sections) == (
        "Organization",
        "Industry",
        "Stated Concern",
        "Current Process",
        "Known Constraints",
        "Evidence Available",
        "Questions Not Yet Answered",
        "Educational Limitations",
    )


def test_report_preserves_facts_without_invention_or_recommendations() -> None:
    """The report contains evidence and explicit gaps only."""
    situation = harbor_street_music_situation()
    report = render_situation_summary(build_situation_summary(situation))
    for fact in (
        situation.organization_name,
        situation.industry,
        situation.stated_concern,
        *situation.current_process,
        *situation.known_constraints,
        *situation.source_notes,
    ):
        assert fact in report
    assert "Sales engineer observations: none recorded." in report
    assert "Other facts established: none." in report
    assert "scheduling errors occur?" in report
    for forbidden in ("CRM", "scheduling platform", "custom application", "$", "% ROI"):
        assert forbidden not in report


def test_markdown_section_order_matches_structured_output() -> None:
    """Presentation follows service-layer ordering."""
    summary = build_situation_summary(harbor_street_music_situation())
    report = render_situation_summary(summary)
    positions = [report.index(f"## {section.heading}") for section in summary.sections]
    assert positions == sorted(positions)
    assert report.endswith("\n")
