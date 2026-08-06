"""Deterministic situation-summary use case."""

from dataclasses import dataclass

from sales_lab.domain.customer_situation import CustomerSituation

UNANSWERED_QUESTIONS = (
    "What is the inquiry volume?",
    "Which staff roles participate in the process?",
    "How often, if ever, does duplicate entry occur?",
    "Do scheduling errors occur?",
    "What capabilities does existing software provide?",
    "Has a budget been approved?",
    "How would the organization define success?",
)

EDUCATIONAL_LIMITATIONS = (
    "This summary records supplied facts for education and comparison; it does not predict "
    "sales outcomes, score or rank people, replace professional judgment, or identify a "
    "universally correct solution.",
    "It uses no machine learning, generative AI, external APIs, or randomness.",
    "It contains no recommendation, diagnosis, ROI calculation, or assumed fact.",
)


@dataclass(frozen=True, slots=True)
class SummarySection:
    """One ordered report section."""

    heading: str
    items: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SituationSummary:
    """Stable structured output ready for presentation."""

    title: str
    sections: tuple[SummarySection, ...]


def build_situation_summary(situation: CustomerSituation) -> SituationSummary:
    """Transform only supplied facts into a stable, structured summary."""
    return SituationSummary(
        title="Customer Situation Summary",
        sections=(
            SummarySection("Organization", (situation.organization_name,)),
            SummarySection("Industry", (situation.industry,)),
            SummarySection("Stated Concern", (situation.stated_concern,)),
            SummarySection("Current Process", situation.current_process),
            SummarySection("Known Constraints", situation.known_constraints),
            SummarySection(
                "Evidence Available",
                (
                    *(f"Customer supplied: {note}" for note in situation.source_notes),
                    "Sales engineer observations: none recorded.",
                    "Other facts established: none.",
                ),
            ),
            SummarySection("Questions Not Yet Answered", UNANSWERED_QUESTIONS),
            SummarySection("Educational Limitations", EDUCATIONAL_LIMITATIONS),
        ),
    )
