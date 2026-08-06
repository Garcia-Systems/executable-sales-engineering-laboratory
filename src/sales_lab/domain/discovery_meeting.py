"""Immutable objects for a structured discovery meeting."""

from dataclasses import dataclass
from enum import StrEnum


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        msg = f"{field_name} must not be blank"
        raise ValueError(msg)


class QuestionCategory(StrEnum):
    """Educational categories used to prepare neutral questions."""

    BUSINESS_GOALS = "Business Goals"
    CURRENT_PROCESS = "Current Process"
    PEOPLE = "People"
    TECHNOLOGY = "Technology"
    DATA = "Data"
    CONSTRAINTS = "Constraints"
    SUCCESS_MEASURES = "Success Measures"


class QuestionKind(StrEnum):
    """Whether a question invites explanation or a bounded answer."""

    OPEN = "Open-ended"
    CLOSED = "Closed"


@dataclass(frozen=True, slots=True)
class MeetingParticipant:
    """A person attending the discovery meeting."""

    name: str
    role: str

    def __post_init__(self) -> None:
        """Validate participant fields."""
        _require_text(self.name, "name")
        _require_text(self.role, "role")


@dataclass(frozen=True, slots=True)
class DiscoveryQuestion:
    """One categorized, neutrally worded discovery prompt."""

    identifier: str
    category: QuestionCategory
    text: str
    kind: QuestionKind

    def __post_init__(self) -> None:
        """Validate question fields."""
        _require_text(self.identifier, "identifier")
        _require_text(self.text, "text")


@dataclass(frozen=True, slots=True)
class DiscoveryResponse:
    """A customer's answer linked to the question that prompted it."""

    question_id: str
    respondent: str
    text: str

    def __post_init__(self) -> None:
        """Validate response fields."""
        _require_text(self.question_id, "question_id")
        _require_text(self.respondent, "respondent")
        _require_text(self.text, "text")


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """A factual meeting record with its customer-provided source."""

    fact: str
    source: str

    def __post_init__(self) -> None:
        """Validate evidence fields."""
        _require_text(self.fact, "fact")
        _require_text(self.source, "source")


@dataclass(frozen=True, slots=True)
class FollowUpItem:
    """An explicit action for an evidence gap, not a recommendation."""

    question_id: str
    action: str

    def __post_init__(self) -> None:
        """Validate follow-up fields."""
        _require_text(self.question_id, "question_id")
        _require_text(self.action, "action")


@dataclass(frozen=True, slots=True)
class DiscoveryMeeting:
    """Ordered questions, answers, and evidence from one meeting."""

    title: str
    participants: tuple[MeetingParticipant, ...]
    questions: tuple[DiscoveryQuestion, ...] = ()
    responses: tuple[DiscoveryResponse, ...] = ()
    evidence: tuple[EvidenceRecord, ...] = ()

    def __post_init__(self) -> None:
        """Validate meeting relationships and identifiers."""
        _require_text(self.title, "title")
        if not self.participants:
            msg = "participants must not be empty"
            raise ValueError(msg)
        question_ids = tuple(question.identifier for question in self.questions)
        if len(question_ids) != len(set(question_ids)):
            msg = "question identifiers must be unique"
            raise ValueError(msg)
        if any(response.question_id not in question_ids for response in self.responses):
            msg = "every response must reference a recorded question"
            raise ValueError(msg)
