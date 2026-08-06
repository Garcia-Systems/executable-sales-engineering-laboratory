"""Immutable, evidence-traceable requirements concepts for Chapter 5."""

from dataclasses import dataclass
from enum import StrEnum


class RequirementType(StrEnum):
    """The distinct kinds of statements taught by the laboratory."""

    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-Functional"
    BUSINESS_RULE = "Business Rule"
    CONSTRAINT = "Constraint"
    SUCCESS_CRITERION = "Success Criterion"


class RequirementStatus(StrEnum):
    """Evidence states; unknown deliberately differs from a negative assertion."""

    ESTABLISHED = "Established"
    UNKNOWN = "Not Established"
    NOT_REQUIRED = "Not Required"


@dataclass(frozen=True, slots=True)
class AcceptanceCriterion:
    """Observable behavior associated with one requirement."""

    identifier: str
    given: str
    when: str
    then: str


@dataclass(frozen=True, slots=True)
class Requirement:
    """A supplied requirement candidate and its explicit traceability links."""

    identifier: str
    statement: str
    requirement_type: RequirementType
    stakeholder_id: str
    source_evidence_ids: tuple[str, ...]
    acceptance_criteria: tuple[AcceptanceCriterion, ...] = ()
    status: RequirementStatus = RequirementStatus.ESTABLISHED
    conflicts_with: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class UnresolvedRequirement:
    """A named requirement area for which discovery has not established an answer."""

    area: str
    status: RequirementStatus = RequirementStatus.UNKNOWN


@dataclass(frozen=True, slots=True)
class RequirementSet:
    """Ordered author-supplied candidates and explicitly unresolved areas."""

    engagement: str
    requirements: tuple[Requirement, ...]
    unresolved: tuple[UnresolvedRequirement, ...]
