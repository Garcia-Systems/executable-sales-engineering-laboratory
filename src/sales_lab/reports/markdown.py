"""Markdown presentation for structured reports."""

from sales_lab.services.situation_summary import SituationSummary


def render_situation_summary(summary: SituationSummary) -> str:
    """Render a situation summary with stable heading and item ordering."""
    lines = [f"# {summary.title}"]
    for section in summary.sections:
        lines.extend(("", f"## {section.heading}"))
        lines.extend(f"- {item}" for item in section.items)
    return "\n".join(lines) + "\n"
