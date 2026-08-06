"""Immutable, evidence-bounded stakeholder concepts for Chapter 4."""

from dataclasses import dataclass
from enum import StrEnum


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        message = f"{field_name} must not be blank"
        raise ValueError(message)


class ResponsibilityCategory(StrEnum):
    """Observable organizational responsibilities, without ranking people."""

    PERFORMS_WORK = "Performs Work"
    OWNS_OUTCOME = "Owns Outcome"
    APPROVES_CHANGE = "Approves Change"
    PROVIDES_INFORMATION = "Provides Information"
    USES_SYSTEM = "Uses System"
    RECEIVES_OUTPUT = "Receives Output"
    AFFECTED_BY_CHANGE = "Affected by Change"
    TECHNICAL_SUPPORT = "Technical Support"


class AuthorityState(StrEnum):
    """Three-valued authority knowledge; unknown is not a negative assertion."""

    KNOWN = "Known"
    NO = "No"
    UNKNOWN = "Unknown"
    NOT_APPLICABLE = "Not Applicable"


@dataclass(frozen=True, slots=True)
class StakeholderRole:
    """A stable organizational role, rather than a person occupying it."""

    identifier: str
    name: str

    def __post_init__(self) -> None:
        """Require a usable identifier and name."""
        _require_text(self.identifier, "role identifier")
        _require_text(self.name, "role name")


@dataclass(frozen=True, slots=True)
class StakeholderEvidence:
    """A traceable source for one or more stakeholder assertions."""

    identifier: str
    statement: str
    source: str

    def __post_init__(self) -> None:
        """Require traceable, readable evidence."""
        _require_text(self.identifier, "evidence identifier")
        _require_text(self.statement, "evidence statement")
        _require_text(self.source, "evidence source")


@dataclass(frozen=True, slots=True)
class StakeholderResponsibility:
    """An established role responsibility supported by evidence."""

    role_id: str
    category: ResponsibilityCategory
    evidence_id: str


@dataclass(frozen=True, slots=True)
class ProcessParticipation:
    """Connect a stakeholder role to a Chapter 3 process-step identifier."""

    role_id: str
    step_id: str
    evidence_id: str


@dataclass(frozen=True, slots=True)
class DecisionAuthority:
    """State what is and is not known about a role's decision authority."""

    role_id: str
    decision: str
    state: AuthorityState
    evidence_id: str

    def __post_init__(self) -> None:
        """Require a described decision."""
        _require_text(self.decision, "authority decision")


@dataclass(frozen=True, slots=True)
class StakeholderRelationship:
    """An evidenced connection between two roles or an explicit unknown endpoint."""

    source_role_id: str
    target_role_id: str
    description: str
    evidence_id: str
    is_unknown: bool = False

    def __post_init__(self) -> None:
        """Require a readable relationship."""
        _require_text(self.description, "relationship description")


@dataclass(frozen=True, slots=True)
class PerspectiveGap:
    """A missing perspective paired with the question that can investigate it."""

    identifier: str
    description: str
    follow_up_question: str

    def __post_init__(self) -> None:
        """Require a described gap and its investigative question."""
        _require_text(self.identifier, "gap identifier")
        _require_text(self.description, "gap description")
        _require_text(self.follow_up_question, "gap follow-up question")


@dataclass(frozen=True, slots=True)
class StakeholderMap:
    """The complete ordered input to deterministic stakeholder analysis."""

    engagement: str
    roles: tuple[StakeholderRole, ...]
    responsibilities: tuple[StakeholderResponsibility, ...]
    participations: tuple[ProcessParticipation, ...]
    authority: tuple[DecisionAuthority, ...]
    relationships: tuple[StakeholderRelationship, ...]
    evidence: tuple[StakeholderEvidence, ...]
    perspective_gaps: tuple[PerspectiveGap, ...]

    def __post_init__(self) -> None:
        """Require the engagement being analyzed."""
        _require_text(self.engagement, "engagement")
