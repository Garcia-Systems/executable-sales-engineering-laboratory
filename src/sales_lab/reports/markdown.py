"""Markdown presentation for structured reports."""

from sales_lab.services.discovery_meeting import DiscoveryMeetingSummary
from sales_lab.services.investigation import InitialDiscoveryAssessment
from sales_lab.services.situation_summary import SituationSummary


def render_situation_summary(summary: SituationSummary) -> str:
    """Render a situation summary with stable heading and item ordering."""
    lines = [f"# {summary.title}"]
    for section in summary.sections:
        lines.extend(("", f"## {section.heading}"))
        lines.extend(f"- {item}" for item in section.items)
    return "\n".join(lines) + "\n"


def render_initial_discovery_assessment(assessment: InitialDiscoveryAssessment) -> str:
    """Render an initial discovery assessment in stable section order."""
    lines = [f"# {assessment.title}"]
    for section in assessment.sections:
        lines.extend(("", f"## {section.heading}"))
        lines.extend(f"- {item}" for item in section.items)
    return "\n".join(lines) + "\n"


def render_discovery_meeting_summary(summary: DiscoveryMeetingSummary) -> str:
    """Render a discovery meeting summary in its stable section order."""
    lines = [f"# {summary.title}"]
    for section in summary.sections:
        lines.extend(("", f"## {section.heading}"))
        lines.extend(f"- {item}" for item in section.items)
    return "\n".join(lines) + "\n"
