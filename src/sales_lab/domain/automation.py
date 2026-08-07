"""Immutable concepts for transparent Chapter 11 automation analysis."""

from dataclasses import dataclass
from enum import StrEnum


class AutomationMode(StrEnum):
    """An explicitly proposed division of work, never an inferred recommendation."""

    MANUAL = "Manual"
    ASSISTED = "Assisted"
    RULE_BASED_AUTOMATION = "Rule-based automation"
    HUMAN_APPROVAL_REQUIRED = "Human approval required"
    HUMAN_DECISION_REQUIRED = "Human decision required"
    NOT_EVALUATED = "Not evaluated"


class ActivityCharacteristic(StrEnum):
    """Observable considerations which are not converted into a score."""

    REPETITIVE = "Repetitive"
    RULE_BASED = "Rule based"
    HIGH_VARIATION = "High variation"
    REQUIRES_JUDGMENT = "Requires judgment"
    REQUIRES_EMPATHY = "Requires empathy"
    REQUIRES_APPROVAL = "Requires approval"
    SENSITIVE = "Sensitive"
    REVERSIBLE = "Reversible"
    EXCEPTION_PRONE = "Exception prone"
    DATA_DEPENDENT = "Data dependent"


class AutomationReadiness(StrEnum):
    """Transparent implementation-readiness states without numeric scoring."""

    READY_FOR_DESIGN = "Ready for design"
    REQUIRES_RULE_DEFINITION = "Requires rule definition"
    REQUIRES_DATA_VALIDATION = "Requires data validation"
    REQUIRES_AUTHORITY_CLARIFICATION = "Requires authority clarification"
    NOT_READY = "Not ready for automation"
    NOT_EVALUATED = "Not evaluated"


class ApprovalState(StrEnum):
    """States that prevent silent external action."""

    DRAFTED = "Drafted"
    AWAITING_APPROVAL = "Awaiting approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


class AutomationRiskCategory(StrEnum):
    """Activity-specific automation risks."""

    INCORRECT_ACTION = "Incorrect action"
    MISSED_EXCEPTION = "Missed exception"
    DUPLICATE_ACTION = "Duplicate action"
    UNAUTHORIZED_ACTION = "Unauthorized action"
    POOR_DATA_QUALITY = "Poor data quality"
    LOSS_OF_HUMAN_CONTEXT = "Loss of human context"
    UNCLEAR_ACCOUNTABILITY = "Unclear accountability"


@dataclass(frozen=True, slots=True)
class WorkflowActivity:
    """A workflow activity linked to an established process step or information flow."""

    identifier: str
    name: str
    process_step_ids: tuple[str, ...]
    information_flow_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HumanResponsibility:
    """The review and accountability retained by a named established role."""

    role_id: str
    reviews: str
    accountable_for: str
    after_no_action: str


@dataclass(frozen=True, slots=True)
class ApprovalBoundary:
    """An explicit boundary around completion or external action."""

    approver_role_id: str
    prepared_state: ApprovalState
    approval_result: str
    rejection_result: str


@dataclass(frozen=True, slots=True)
class ExceptionPath:
    """A known exception and its accountable route."""

    condition: str
    result: str
    owner_role_id: str


@dataclass(frozen=True, slots=True)
class AutomationAssessment:
    """An authored candidate assessment with evidence and unresolved concerns."""

    identifier: str
    activity: WorkflowActivity
    characteristics: tuple[ActivityCharacteristic, ...]
    automation_mode: AutomationMode
    readiness: AutomationReadiness
    system_responsibility: str
    human_responsibility: HumanResponsibility
    evidence_ids: tuple[str, ...]
    requirement_ids: tuple[str, ...]
    capability_ids: tuple[str, ...]
    architecture_ids: tuple[str, ...]
    required_rules: tuple[str, ...]
    unresolved_rules: tuple[str, ...]
    data_dependencies: tuple[str, ...]
    approval_boundary: ApprovalBoundary | None
    exception_paths: tuple[ExceptionPath, ...]
    risks: tuple[AutomationRiskCategory, ...]
    open_questions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class UnsupportedAutomationProposal:
    """A rejected proposal that lacks safe evidentiary support."""

    description: str
    supporting_requirement_id: str | None
    decision_rule: str | None
    accountable_role_id: str | None
    ranks_people: bool = False


@dataclass(frozen=True, slots=True)
class AutomationPlan:
    """An immutable authored plan; order is scenario order rather than a ranking."""

    engagement: str
    assessments: tuple[AutomationAssessment, ...]
    unsupported_proposals: tuple[UnsupportedAutomationProposal, ...]
