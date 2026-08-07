"""Immutable Chapter 15 demonstration and proof-of-concept concepts."""

# ruff: noqa: D101

from dataclasses import dataclass
from enum import StrEnum


class DemonstrationType(StrEnum):
    PRODUCT_DEMONSTRATION = "Product Demonstration"
    SOLUTION_DEMONSTRATION = "Solution Demonstration"
    PROTOTYPE = "Prototype"
    PROOF_OF_CONCEPT = "Proof of Concept"
    PILOT = "Pilot"
    PRODUCTION_IMPLEMENTATION = "Production Implementation"


class DemonstrationFindingState(StrEnum):
    PASSED = "Passed"
    FAILED = "Failed"
    PARTIALLY_DEMONSTRATED = "Partially Demonstrated"
    NOT_DEMONSTRATED = "Not Demonstrated"
    INCONCLUSIVE = "Inconclusive"


class ProofOfConceptStatus(StrEnum):
    NOT_EXECUTED = "Not Executed"
    PASSED = "Passed"
    FAILED = "Failed"
    INCONCLUSIVE = "Inconclusive"


@dataclass(frozen=True, slots=True)
class DemonstrationObjective:
    question: str
    statement: str
    trace_ids: tuple[str, ...]
    expected_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DemonstrationAudience:
    role_id: str
    role_name: str
    participation_reason: str


@dataclass(frozen=True, slots=True)
class DemonstrationScenario:
    inquiry_id: str
    prospective_student: str
    instrument: str
    initial_status: str
    requested_availability: str
    selected_time: str | None
    responsible_instructor: str | None


@dataclass(frozen=True, slots=True)
class DemonstrationStep:
    order: int
    identifier: str
    actor_role_id: str
    action: str
    trace_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Condition:
    identifier: str
    description: str
    evidence_id: str


@dataclass(frozen=True, slots=True)
class EvidenceArtifact:
    identifier: str
    artifact_type: str
    content: str
    trace_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ObservedResult:
    step_id: str
    observation: str
    interpretation: str
    limitation: str
    evidence_id: str


@dataclass(frozen=True, slots=True)
class DemonstrationFinding:
    identifier: str
    state: DemonstrationFindingState
    description: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DemonstrationLimitation:
    identifier: str
    description: str


@dataclass(frozen=True, slots=True)
class ProofOfConceptQuestion:
    identifier: str
    question: str
    proposed_test: str
    evidence_needed: str
    success_condition: str
    failure_condition: str
    consequence: str
    status: ProofOfConceptStatus


@dataclass(frozen=True, slots=True)
class CoverageRecord:
    source_id: str
    coverage: str
    step_id: str
    evidence_id: str
    finding: str


@dataclass(frozen=True, slots=True)
class DemonstrationPlan:
    engagement: str
    demonstration_type: DemonstrationType
    objective: DemonstrationObjective
    audience: tuple[DemonstrationAudience, ...]
    scenario: DemonstrationScenario
    scope: tuple[str, ...]
    exclusions: tuple[str, ...]
    steps: tuple[DemonstrationStep, ...]
    success_conditions: tuple[Condition, ...]
    failure_conditions: tuple[Condition, ...]
    limitations: tuple[DemonstrationLimitation, ...]
    claims: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DemonstrationReport:
    plan: DemonstrationPlan
    evidence_artifacts: tuple[EvidenceArtifact, ...]
    observed_results: tuple[ObservedResult, ...]
    findings: tuple[DemonstrationFinding, ...]
    requirement_coverage: tuple[CoverageRecord, ...]
    condition_coverage: tuple[CoverageRecord, ...]
    poc_questions: tuple[ProofOfConceptQuestion, ...]
    unsupported_claims: tuple[str, ...]
    guardrail_findings: tuple[str, ...]
    production_ready: bool = False


@dataclass(frozen=True, slots=True)
class DemonstrationExperiment:
    name: str
    original_scenario: DemonstrationScenario
    observations: tuple[str, ...]
    scheduling_effects: int
    finding: DemonstrationFindingState
