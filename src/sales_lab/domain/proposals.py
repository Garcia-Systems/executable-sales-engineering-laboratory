"""Immutable concepts for Chapter 16 proposal and decision packages."""

# ruff: noqa: D101

from dataclasses import dataclass
from enum import StrEnum

from sales_lab.domain.decisions import Recommendation
from sales_lab.domain.demonstrations import DemonstrationFinding, DemonstrationLimitation
from sales_lab.domain.risks import (
    AssumptionRecord,
    DependencyRecord,
    ResidualRisk,
    Risk,
    RiskResponse,
)


class ProposalType(StrEnum):
    DISCOVERY_SUMMARY = "Discovery Summary"
    RECOMMENDATION_PACKAGE = "Recommendation Package"
    VALIDATION_PROPOSAL = "Validation Proposal"
    IMPLEMENTATION_PROPOSAL = "Implementation Proposal"
    DECISION_PACKAGE = "Decision Package"


class ProposalLifecycle(StrEnum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    PRESENTED = "Presented"
    REVISED = "Revised"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class CommercialStatus(StrEnum):
    NOT_ESTABLISHED = "NOT ESTABLISHED"
    EXPERIMENTAL = "EXPERIMENTAL COMMERCIAL SCENARIO"


@dataclass(frozen=True, slots=True)
class ExecutiveSummary:
    customer_situation: str
    problem: str
    recommended_direction: str
    rationale: str
    major_conditions: str
    requested_decision: str


@dataclass(frozen=True, slots=True)
class ScopeItem:
    identifier: str
    statement: str
    requirement_ids: tuple[str, ...]
    capability_ids: tuple[str, ...]
    recommendation_finding_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProposedDeliverable:
    identifier: str
    statement: str
    scope_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CommercialPlaceholder:
    label: str
    status: CommercialStatus
    value: str | None = None


@dataclass(frozen=True, slots=True)
class DecisionRequest:
    statement: str
    authority: str
    scope_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NextStep:
    order: int
    statement: str


@dataclass(frozen=True, slots=True)
class ValueSummary:
    established_cost_information: tuple[str, ...]
    unresolved_cost_information: tuple[str, ...]
    benefit_hypotheses: tuple[str, ...]
    calculation_readiness: str
    intangible_value: tuple[str, ...]
    sensitivity_note: str


@dataclass(frozen=True, slots=True)
class ProposalPackage:
    engagement: str
    proposal_type: ProposalType
    lifecycle: ProposalLifecycle
    executive_summary: ExecutiveSummary
    established_situation: tuple[str, ...]
    assumed_situation: tuple[str, ...]
    unknown_situation: tuple[str, ...]
    recommendation: Recommendation
    scope: tuple[ScopeItem, ...]
    exclusions: tuple[str, ...]
    deliverables: tuple[ProposedDeliverable, ...]
    assumptions: tuple[AssumptionRecord, ...]
    dependencies: tuple[DependencyRecord, ...]
    risks: tuple[Risk, ...]
    risk_responses: tuple[RiskResponse, ...]
    residual_risks: tuple[ResidualRisk, ...]
    value_summary: ValueSummary
    demonstration_findings: tuple[DemonstrationFinding, ...]
    demonstration_limitations: tuple[DemonstrationLimitation, ...]
    commercial_placeholders: tuple[CommercialPlaceholder, ...]
    decision_request: DecisionRequest
    next_steps: tuple[NextStep, ...]
    limitations: tuple[str, ...]
    validation_findings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProposalExperiment:
    name: str
    original: ProposalPackage
    changed: ProposalPackage
    finding: str
