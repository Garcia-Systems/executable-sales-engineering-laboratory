"""Immutable delivery-handoff concepts for Chapter 17."""

# ruff: noqa: D101

from dataclasses import dataclass
from enum import StrEnum


class HandoffType(StrEnum):
    DISCOVERY_HANDOFF = "DISCOVERY_HANDOFF"
    TECHNICAL_HANDOFF = "TECHNICAL_HANDOFF"
    IMPLEMENTATION_HANDOFF = "IMPLEMENTATION_HANDOFF"
    VALIDATION_HANDOFF = "VALIDATION_HANDOFF"
    SUPPORT_HANDOFF = "SUPPORT_HANDOFF"


class LifecycleStatus(StrEnum):
    RECOMMENDED = "RECOMMENDED"
    PROPOSED = "PROPOSED"
    PRESENTED = "PRESENTED"
    APPROVED = "APPROVED"
    READY_FOR_DELIVERY = "READY_FOR_DELIVERY"
    IN_IMPLEMENTATION = "IN_IMPLEMENTATION"
    IMPLEMENTED = "IMPLEMENTED"
    VALIDATED = "VALIDATED"


class DeliveryReadiness(StrEnum):
    READY = "READY"
    CONDITIONALLY_READY = "CONDITIONALLY_READY"
    NOT_READY = "NOT_READY"
    ON_HOLD = "ON_HOLD"
    NOT_EVALUATED = "NOT_EVALUATED"


class ScopeStatus(StrEnum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"
    UNDER_REVIEW = "UNDER_REVIEW"


class ConditionType(StrEnum):
    SCOPE_APPROVED = "SCOPE_APPROVED"
    REQUIREMENTS_BASELINED = "REQUIREMENTS_BASELINED"
    ACCEPTANCE_CRITERIA_DEFINED = "ACCEPTANCE_CRITERIA_DEFINED"
    ARCHITECTURE_REVIEWED = "ARCHITECTURE_REVIEWED"
    DEPENDENCIES_IDENTIFIED = "DEPENDENCIES_IDENTIFIED"
    OWNERS_ASSIGNED = "OWNERS_ASSIGNED"
    RISKS_ACKNOWLEDGED = "RISKS_ACKNOWLEDGED"
    DATA_AVAILABLE = "DATA_AVAILABLE"
    ENVIRONMENT_AVAILABLE = "ENVIRONMENT_AVAILABLE"
    INTEGRATION_FEASIBILITY_ESTABLISHED = "INTEGRATION_FEASIBILITY_ESTABLISHED"
    CHANGE_CONTROL_DEFINED = "CHANGE_CONTROL_DEFINED"
    VALIDATION_PLAN_DEFINED = "VALIDATION_PLAN_DEFINED"


class ConditionStatus(StrEnum):
    SATISFIED = "SATISFIED"
    UNSATISFIED = "UNSATISFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ResponsibilityCategory(StrEnum):
    ACCOUNTABLE = "ACCOUNTABLE"
    RESPONSIBLE = "RESPONSIBLE"
    CONSULTED = "CONSULTED"
    INFORMED = "INFORMED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


class DiscoveryStage(StrEnum):
    PRE_IMPLEMENTATION_DISCOVERY = "PRE_IMPLEMENTATION_DISCOVERY"
    IMPLEMENTATION_DISCOVERY = "IMPLEMENTATION_DISCOVERY"


class AcceptanceStatus(StrEnum):
    NOT_ACCEPTED = "NOT_ACCEPTED"
    ACCEPTED = "ACCEPTED"


@dataclass(frozen=True, slots=True)
class DeliveryScopeItem:
    identifier: str
    statement: str
    status: ScopeStatus
    trace_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RequirementsBaseline:
    identifier: str
    included_ids: tuple[str, ...]
    excluded_ids: tuple[str, ...]
    unresolved: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ArchitectureBaseline:
    candidate_id: str
    known_components: tuple[str, ...]
    external_systems: tuple[str, ...]
    information_flows: tuple[str, ...]
    unresolved_choices: tuple[str, ...]
    final: bool = False


@dataclass(frozen=True, slots=True)
class IntegrationReadinessItem:
    identifier: str
    scope_ids: tuple[str, ...]
    source: str
    destination: str
    information: str
    pattern: str
    feasibility: str
    interface_evidence: str
    duplicate_expectation: str
    failure_expectation: str
    unresolved_questions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AutomationReadinessItem:
    identifier: str
    mode: str
    human_responsibility: str
    approval_boundary: str
    decision_rule: str
    exception_path: str
    data_dependency: str
    readiness: str


@dataclass(frozen=True, slots=True)
class AcceptanceBaselineItem:
    requirement_id: str
    criterion: str
    validation_method: str
    validating_role: str
    evidence_artifact: str
    status: AcceptanceStatus = AcceptanceStatus.NOT_ACCEPTED


@dataclass(frozen=True, slots=True)
class UnresolvedDecision:
    identifier: str
    question: str
    affected_scope: tuple[str, ...]
    owner: str
    due_point: str
    consequence: str


@dataclass(frozen=True, slots=True)
class TechnicalDiscoveryItem:
    identifier: str
    question: str
    stage: DiscoveryStage
    scope_ids: tuple[str, ...]
    blocking: bool


@dataclass(frozen=True, slots=True)
class ResponsibilityAssignment:
    area: str
    role: str
    category: ResponsibilityCategory


@dataclass(frozen=True, slots=True)
class ReadinessCondition:
    condition: ConditionType
    status: ConditionStatus
    evidence: str
    blocking: bool
    next_action: str


@dataclass(frozen=True, slots=True)
class HandoffArtifact:
    name: str
    source_chapter: int
    status: str
    consumer: str
    limitation: str


@dataclass(frozen=True, slots=True)
class ChangeControlBoundary:
    baseline: str
    clarification: str
    scope_change: str
    approval_authority: str
    traceability_update: str
    acceptance_effect: str


@dataclass(frozen=True, slots=True)
class Finding:
    identifier: str
    statement: str
    affected_scope: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImplementationHandoff:
    engagement: str
    handoff_type: HandoffType
    lifecycle_status: LifecycleStatus
    scope_items: tuple[DeliveryScopeItem, ...]
    exclusions: tuple[str, ...]
    requirements_baseline: RequirementsBaseline
    architecture_baseline: ArchitectureBaseline
    integration_readiness: tuple[IntegrationReadinessItem, ...]
    automation_readiness: tuple[AutomationReadinessItem, ...]
    acceptance_baseline: tuple[AcceptanceBaselineItem, ...]
    unresolved_decisions: tuple[UnresolvedDecision, ...]
    technical_discovery: tuple[TechnicalDiscoveryItem, ...]
    responsibilities: tuple[ResponsibilityAssignment, ...]
    change_control: ChangeControlBoundary
    artifacts: tuple[HandoffArtifact, ...]
    risks: tuple[str, ...]
    assumptions: tuple[str, ...]
    dependencies: tuple[str, ...]
    demonstration_findings: tuple[str, ...]
    delivery_items: tuple[DeliveryScopeItem, ...] = ()
    commitments: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DeliveryPackage:
    handoff: ImplementationHandoff
    readiness: DeliveryReadiness
    readiness_conditions: tuple[ReadinessCondition, ...]
    blocking_findings: tuple[Finding, ...]
    non_blocking_follow_up: tuple[Finding, ...]
    unsupported_scope: tuple[Finding, ...]
    unsupported_commitments: tuple[Finding, ...]
    next_actions: tuple[str, ...]
