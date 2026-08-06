"""Deterministic classification and initial-discovery investigation services."""

from dataclasses import dataclass

from sales_lab.domain.discovery import (
    Assumption,
    CustomerStatement,
    InvestigationQuestion,
    Observation,
    ProblemHypothesis,
    UnknownInformation,
    VerifiedFact,
)
from sales_lab.services.situation_summary import SummarySection

GENERIC_INVESTIGATION_QUESTIONS = (
    InvestigationQuestion("How many inquiries arrive each week?"),
    InvestigationQuestion("Who contacts prospective students?"),
    InvestigationQuestion("How is follow-up tracked?"),
    InvestigationQuestion("When does information become unavailable?"),
    InvestigationQuestion("Which systems currently contain student information?"),
    InvestigationQuestion("What counts as a missed inquiry?"),
)

EDUCATIONAL_LIMITATIONS = (
    "This assessment organizes supplied evidence; it does not identify the customer's "
    "real problem.",
    "Hypotheses are unverified possibilities, not facts or predictions.",
    "No product, solution, outcome, score, or recommendation is generated.",
    "The assessment does not replace professional judgment.",
)


def _require_instances(values: tuple[object, ...], expected: type[object], name: str) -> None:
    if any(type(value) is not expected for value in values):
        msg = f"{name} accepts only {expected.__name__} objects"
        raise TypeError(msg)


@dataclass(frozen=True, slots=True)
class DiscoveryEvidence:
    """Collected discovery information held in separate, ordered categories."""

    customer_statements: tuple[CustomerStatement, ...] = ()
    observations: tuple[Observation, ...] = ()
    verified_facts: tuple[VerifiedFact, ...] = ()
    assumptions: tuple[Assumption, ...] = ()
    questions: tuple[InvestigationQuestion, ...] = ()
    hypotheses: tuple[ProblemHypothesis, ...] = ()
    unknown_information: tuple[UnknownInformation, ...] = ()

    def __post_init__(self) -> None:
        """Prevent category errors even when callers bypass static type checking."""
        categories = (
            (self.customer_statements, CustomerStatement, "customer_statements"),
            (self.observations, Observation, "observations"),
            (self.verified_facts, VerifiedFact, "verified_facts"),
            (self.assumptions, Assumption, "assumptions"),
            (self.questions, InvestigationQuestion, "questions"),
            (self.hypotheses, ProblemHypothesis, "hypotheses"),
            (self.unknown_information, UnknownInformation, "unknown_information"),
        )
        for values, expected, name in categories:
            _require_instances(values, expected, name)


@dataclass(frozen=True, slots=True)
class ClassifiedInformation:
    """Ordered classification output for the evidence collected so far."""

    customer_statements: tuple[str, ...]
    observations: tuple[str, ...]
    verified_facts: tuple[str, ...]
    open_questions: tuple[str, ...]
    hypotheses: tuple[str, ...]
    unknown_information: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class InitialDiscoveryAssessment:
    """Stable structured assessment ready for Markdown presentation."""

    title: str
    sections: tuple[SummarySection, ...]


InformationItem = (
    CustomerStatement
    | Observation
    | VerifiedFact
    | Assumption
    | InvestigationQuestion
    | ProblemHypothesis
    | UnknownInformation
)


def _item_text(items: tuple[InformationItem, ...]) -> tuple[str, ...]:
    """Extract display text, explicitly representing an empty category."""
    return tuple(item.text for item in items) or ("None recorded.",)


def classify_information(evidence: DiscoveryEvidence) -> ClassifiedInformation:
    """Classify evidence without scoring, inference, reordering, or recommendation."""
    return ClassifiedInformation(
        customer_statements=tuple(item.text for item in evidence.customer_statements),
        observations=tuple(item.text for item in evidence.observations),
        verified_facts=tuple(item.text for item in evidence.verified_facts),
        open_questions=tuple(item.text for item in evidence.questions),
        hypotheses=tuple(item.text for item in evidence.hypotheses),
        unknown_information=tuple(item.text for item in evidence.unknown_information),
    )


def investigation_questions(evidence: DiscoveryEvidence) -> tuple[InvestigationQuestion, ...]:
    """Return fixed educational prompts after any questions already recorded."""
    return (*evidence.questions, *GENERIC_INVESTIGATION_QUESTIONS)


def build_initial_discovery_assessment(
    evidence: DiscoveryEvidence,
) -> InitialDiscoveryAssessment:
    """Build a bounded assessment that keeps facts and hypotheses visibly separate."""
    questions = investigation_questions(evidence)
    return InitialDiscoveryAssessment(
        title="Initial Discovery Assessment",
        sections=(
            SummarySection("Customer Statement", _item_text(evidence.customer_statements)),
            SummarySection("Known Facts", _item_text(evidence.verified_facts)),
            SummarySection("Observations", _item_text(evidence.observations)),
            SummarySection("Assumptions to Avoid", _item_text(evidence.assumptions)),
            SummarySection("Questions Requiring Investigation", _item_text(questions)),
            SummarySection("Possible Problem Hypotheses", _item_text(evidence.hypotheses)),
            SummarySection("Educational Limitations", EDUCATIONAL_LIMITATIONS),
        ),
    )
