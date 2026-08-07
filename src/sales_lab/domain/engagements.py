"""Immutable Chapter 19 end-to-end engagement concepts."""

from dataclasses import dataclass
from enum import StrEnum


class EngagementStage(StrEnum):
    """The deterministic Volume I reasoning order."""

    SITUATION = "Situation"
    INVESTIGATION = "Investigation"
    DISCOVERY = "Discovery"
    PROCESS = "Process"
    STAKEHOLDERS = "Stakeholders"
    REQUIREMENTS = "Requirements"
    CAPABILITIES = "Capabilities"
    GAPS = "Gaps"
    APPROACHES = "Approaches"
    ARCHITECTURE = "Architecture"
    INTEGRATIONS = "Integrations"
    AUTOMATION = "Automation"
    VALUE = "Value"
    RISKS = "Risks"
    RECOMMENDATION = "Recommendation"
    DEMONSTRATION = "Demonstration"
    PROPOSAL = "Proposal"
    HANDOFF = "Handoff"
    SUCCESS_MEASUREMENT = "Success Measurement"


class StageStatus(StrEnum):
    """A stage result, deliberately not a percentage or customer score."""

    COMPLETE = "COMPLETE"
    COMPLETE_WITH_FINDINGS = "COMPLETE_WITH_FINDINGS"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass(frozen=True, slots=True)
class EngagementStageResult:
    """One stage's structured output and transparent status."""

    stage: EngagementStage
    status: StageStatus
    output: object | None
    findings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TraceLink:
    """A directed, typed cross-chapter reasoning link."""

    source_type: str
    source_id: str
    relationship: str
    target_type: str
    target_id: str
    evidence_note: str = ""


@dataclass(frozen=True, slots=True)
class EngagementValidationFinding:
    """A learner-friendly cross-stage invariant result."""

    code: str
    message: str
    blocking: bool = False


@dataclass(frozen=True, slots=True)
class SalesEngineeringEngagement:
    """An immutable index over the real Chapter 0-18 outputs."""

    identifier: str
    customer: str
    stage_results: tuple[EngagementStageResult, ...]
    trace_links: tuple[TraceLink, ...]
    validation_findings: tuple[EngagementValidationFinding, ...]
    unresolved_questions: tuple[str, ...]

    def result(self, stage: EngagementStage) -> EngagementStageResult:
        """Return a stage result, failing loudly for a programming error."""
        return next(item for item in self.stage_results if item.stage is stage)


@dataclass(frozen=True, slots=True)
class EngagementPackage:
    """Deterministically named Markdown artifacts."""

    engagement_id: str
    documents: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class EngagementScenario:
    """Immutable evidence change applied to the canonical analysis."""

    identifier: str
    name: str
    added_evidence: tuple[str, ...] = ()
    changed_assumptions: tuple[str, ...] = ()
    affected_stages: tuple[EngagementStage, ...] = ()
    findings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EngagementDiff:
    """Structured scenario delta; report strings are never compared."""

    baseline_id: str
    scenario_id: str
    added_evidence: tuple[str, ...]
    changed_assumptions: tuple[str, ...]
    changed_stages: tuple[EngagementStage, ...]
    changed_findings: tuple[str, ...]
    unchanged_conclusions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EngagementComparison:
    """A neutral qualitative comparison with no winner or ranking."""

    scenario_ids: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
