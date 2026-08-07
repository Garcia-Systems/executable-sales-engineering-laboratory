"""Deterministic Chapter 14 analysis; professional judgment selects the recommendation."""

# ruff: noqa: C901, E501, PLR0913

from dataclasses import replace

from sales_lab.domain.decisions import (
    ApproachEvaluation,
    ChangeTrigger,
    ConditionKind,
    ConditionStatus,
    ConfidenceLevel,
    CriterionFinding,
    CriterionType,
    DecisionCondition,
    DecisionCriterion,
    DecisionExperiment,
    DecisionPackage,
    EvidenceStrength,
    FindingState,
    ProfessionalJudgment,
    Recommendation,
    RecommendationAlternative,
    RecommendationCondition,
    RecommendationConfidence,
    RecommendationType,
    StakeholderPerspective,
    TradeoffStatement,
    numeric_decision_fields,
)
from sales_lab.examples.harbor_street_music import harbor_street_music_solution_options
from sales_lab.services.risks import analyze_harbor_street_risks


def validate_decision(package: DecisionPackage) -> DecisionPackage:
    """Reject incoherent or falsely authoritative recommendations without choosing one."""
    recommendation = package.recommendation
    approach_ids = {identifier for identifier, _ in package.approaches}
    evidence_ids = {
        evidence_id
        for evaluation in package.evaluations
        for finding in evaluation.findings
        for evidence_id in finding.evidence_ids
    }
    errors: list[str] = []
    if not recommendation.approach_ids or not set(recommendation.approach_ids) <= approach_ids:
        errors.append("recommendation has no supporting approach")
    if not recommendation.evidence_ids or not set(recommendation.evidence_ids) <= evidence_ids:
        errors.append("recommendation has no traceable evidence")
    selected = tuple(
        evaluation
        for evaluation in package.evaluations
        if evaluation.approach_id in recommendation.approach_ids
    )
    unresolved_mandatory = {
        condition.identifier
        for condition in package.mandatory_conditions
        if condition.kind is ConditionKind.MANDATORY
        and condition.status is not ConditionStatus.SATISFIED
        and set(condition.approach_ids) & set(recommendation.approach_ids)
    }
    recommendation_trace = {
        trace_id for condition in recommendation.conditions for trace_id in condition.trace_ids
    }
    if not unresolved_mandatory <= recommendation_trace:
        errors.append("recommendation ignores an unmet mandatory condition")
    if recommendation.recommendation_type is RecommendationType.PROCEED and any(
        evaluation.disqualified for evaluation in selected
    ):
        errors.append("disqualified approach cannot proceed")
    if (
        recommendation.recommendation_type is RecommendationType.PROCEED_CONDITIONALLY
        and not recommendation.conditions
    ):
        errors.append("conditional recommendation requires conditions")
    if not recommendation.confidence.basis.strip():
        errors.append("recommendation confidence requires a written basis")
    if not package.professional_judgment.rationale.strip():
        errors.append("professional judgment requires a rationale")
    if any(item.claims_agreement and not item.evidence_ids for item in package.perspectives):
        errors.append("stakeholder agreement requires evidence")
    if not recommendation.change_triggers:
        errors.append("recommendation requires change triggers")
    if recommendation.approved:
        errors.append("the laboratory cannot approve a customer decision")
    if numeric_decision_fields():
        errors.append("hidden numeric decision field detected")
    if errors:
        raise ValueError("; ".join(errors))
    return package


def _finding(
    approach_id: str,
    criterion_id: str,
    state: FindingState,
    strength: EvidenceStrength,
    reason: str,
    evidence_ids: tuple[str, ...],
) -> CriterionFinding:
    return CriterionFinding(approach_id, criterion_id, state, strength, reason, evidence_ids)


def harbor_street_decision_package() -> DecisionPackage:
    """Construct the authored recommendation from Chapters 0-13 evidence and alternatives."""
    options = harbor_street_music_solution_options()
    risks = analyze_harbor_street_risks().register
    approaches = tuple((item.identifier, item.name) for item in options.approaches)
    criteria = (
        DecisionCriterion(
            "CRIT-001",
            CriterionType.REQUIREMENT_COVERAGE,
            "Coverage of documented inquiry visibility and scheduling requirements.",
            ("REQ-001", "REQ-002", "REQ-003"),
        ),
        DecisionCriterion(
            "CRIT-002",
            CriterionType.IMPLEMENTATION_FEASIBILITY,
            "Feasibility supported by current-tool and technical evidence.",
            ("APP-001", "APP-002", "INT-UNKNOWN"),
        ),
        DecisionCriterion(
            "CRIT-003",
            CriterionType.COST_READINESS,
            "Cost evidence and approval readiness for the proposed scope.",
            ("E7", "VAL-BASELINE"),
        ),
        DecisionCriterion(
            "CRIT-004",
            CriterionType.REVERSIBILITY,
            "Ability to learn without an irreversible commitment.",
            ("APP-001", "APP-002"),
        ),
        DecisionCriterion(
            "CRIT-005",
            CriterionType.MAINTENANCE_OWNERSHIP,
            "Established ownership for operation and maintenance.",
            ("E5", "DEP-003"),
        ),
    )
    conditions = (
        DecisionCondition(
            "COND-001",
            "Preserve authorized access to lesson inquiry and schedule records.",
            ConditionKind.MANDATORY,
            ConditionStatus.REQUIRES_VALIDATION,
            ("APP-001", "APP-002", "APP-003", "APP-004", "APP-005", "APP-006"),
            ("E4",),
        ),
        DecisionCondition(
            "COND-002",
            "Define lesson-inquiry states and responsible editors.",
            ConditionKind.MANDATORY,
            ConditionStatus.UNMET,
            ("APP-001", "APP-002", "APP-003", "APP-006"),
            ("AUT-DATA", "DEP-002"),
        ),
        DecisionCondition(
            "COND-003",
            "Minimize disruption to current staff workflows.",
            ConditionKind.PREFERENCE,
            ConditionStatus.SATISFIED,
            ("APP-001", "APP-002"),
            ("E2",),
        ),
    )
    findings = (
        _finding(
            "APP-001",
            "CRIT-001",
            FindingState.PARTIAL,
            EvidenceStrength.PARTIALLY_ESTABLISHED,
            "A standardized process addresses status consistency but does not establish instructor schedule visibility.",
            ("E2", "REQ-001"),
        ),
        _finding(
            "APP-001",
            "CRIT-002",
            FindingState.REQUIRES_VALIDATION,
            EvidenceStrength.ASSUMPTION_DEPENDENT,
            "Staff adoption and editing responsibilities require validation.",
            ("DEP-002",),
        ),
        _finding(
            "APP-002",
            "CRIT-001",
            FindingState.PARTIAL,
            EvidenceStrength.PARTIALLY_ESTABLISHED,
            "The existing spreadsheet may support status visibility; scheduling remains a separate handoff.",
            ("E2", "REQ-001", "CAP-001", "GAP-001"),
        ),
        _finding(
            "APP-002",
            "CRIT-002",
            FindingState.REQUIRES_VALIDATION,
            EvidenceStrength.ASSUMPTION_DEPENDENT,
            "Controlled status tracking and access have not yet been verified in the spreadsheet.",
            ("E2", "AUT-DATA"),
        ),
        _finding(
            "APP-002",
            "CRIT-004",
            FindingState.ESTABLISHED,
            EvidenceStrength.ESTABLISHED,
            "It uses an existing resource and limits immediate change scope.",
            ("E2", "APP-002"),
        ),
        _finding(
            "APP-002",
            "CRIT-003",
            FindingState.REQUIRES_VALIDATION,
            EvidenceStrength.UNKNOWN,
            "No software budget is approved and baseline value measurements are incomplete.",
            ("E7", "VAL-BASELINE"),
        ),
        _finding(
            "APP-003",
            "CRIT-002",
            FindingState.UNKNOWN,
            EvidenceStrength.UNKNOWN,
            "Calendar interface, access, authentication, and duplicate behavior remain unverified.",
            ("INT-UNKNOWN", "RISK-001"),
        ),
        _finding(
            "APP-004",
            "CRIT-003",
            FindingState.CONSTRAINT_CONFLICT,
            EvidenceStrength.ESTABLISHED,
            "No software budget has been approved and product costs are not established.",
            ("E7", "DEP-001"),
        ),
        _finding(
            "APP-005",
            "CRIT-005",
            FindingState.REQUIRES_VALIDATION,
            EvidenceStrength.UNKNOWN,
            "Development and maintenance ownership are not established.",
            ("E5", "RISK-003"),
        ),
        _finding(
            "APP-006",
            "CRIT-002",
            FindingState.REQUIRES_VALIDATION,
            EvidenceStrength.ASSUMPTION_DEPENDENT,
            "Each combined element and its interactions require evidence.",
            ("INT-UNKNOWN", "DEP-003"),
        ),
        _finding(
            "APP-007",
            "CRIT-001",
            FindingState.PARTIAL,
            EvidenceStrength.ESTABLISHED,
            "The current process retains known manual copying and incomplete status consistency.",
            ("E2", "ISS-001"),
        ),
    )
    evaluations = tuple(
        ApproachEvaluation(
            approach_id,
            tuple(item for item in findings if item.approach_id == approach_id),
            tuple(item.identifier for item in conditions if approach_id in item.approach_ids),
        )
        for approach_id, _ in approaches
    )
    tradeoffs = (
        TradeoffStatement(
            "APP-002",
            "continued dependence on separate spreadsheet and calendar resources",
            "lower immediate change scope, existing-resource use, and greater reversibility",
        ),
        TradeoffStatement(
            "APP-003",
            "technical and operational integration dependencies",
            "less duplicate handling if feasibility and value are established",
        ),
        TradeoffStatement(
            "APP-005",
            "unresolved development, cost, and maintenance ownership",
            "greater implementation control",
        ),
    )
    perspectives = (
        StakeholderPerspective(
            "staff",
            "Front Desk Staff",
            "May value shared visibility and reduced duplicate handling; perspective not yet collected.",
        ),
        StakeholderPerspective(
            "manager",
            "Store Manager",
            "May value operational continuity and controlled cost; perspective not yet collected.",
        ),
        StakeholderPerspective(
            "instructor",
            "Music Instructor",
            "May value reliable confirmed-schedule information; perspective not yet collected.",
        ),
        StakeholderPerspective(
            "technology-owner", "Technology Owner", "Role and perspective not established."
        ),
    )
    judgment = ProfessionalJudgment(
        "At the current evidence level, standardizing the process and configuring the existing spreadsheet is a reversible way to address part of the established visibility need while creating evidence before a larger investment.",
        (
            "Continue the separate calendar handoff during validation.",
            "Do not promise a measured benefit before collecting a baseline.",
        ),
        (
            "Calendar integration feasibility and technology ownership remain unresolved.",
            "No software budget is approved.",
        ),
        (
            "Spreadsheet access behavior, baseline handling time, and stakeholder perspectives remain incomplete.",
        ),
    )
    recommendation_conditions = (
        RecommendationCondition(
            "RC-001",
            "Define inquiry statuses and the confirmed-lesson handoff.",
            ("COND-002", "DEP-002"),
        ),
        RecommendationCondition(
            "RC-002",
            "Assign process ownership and confirm staff editing responsibilities.",
            ("COND-002", "E5"),
        ),
        RecommendationCondition(
            "RC-003", "Verify authorized spreadsheet and calendar access.", ("COND-001", "E4")
        ),
        RecommendationCondition(
            "RC-004",
            "Collect baseline handling-time and outcome measurements and define success measures.",
            ("VAL-BASELINE", "RISK-004"),
        ),
        RecommendationCondition(
            "RC-005",
            "Investigate calendar integration separately before automating the handoff.",
            ("INT-UNKNOWN", "RISK-001"),
        ),
    )
    recommendation = Recommendation(
        RecommendationType.PROCEED_CONDITIONALLY,
        ("APP-001", "APP-002"),
        "Standardize the lesson-inquiry process and configure the existing shared spreadsheet while retaining the manual calendar handoff during an initial validation period.",
        "Improve consistent inquiry-status visibility without assuming that larger technology investment is justified.",
        ("E2", "REQ-001", "CAP-001", "GAP-001", "E7", "VAL-BASELINE"),
        recommendation_conditions,
        RecommendationConfidence(
            ConfidenceLevel.MODERATE,
            "The process inconsistency and immediate visibility gap are documented, but spreadsheet controls, baseline value, integration feasibility, and technical ownership remain unresolved.",
        ),
        (
            RecommendationAlternative(
                "APP-007",
                "Contingency",
                "Use a documented manual handoff if configuration validation fails.",
            ),
            RecommendationAlternative(
                "APP-003",
                "Future alternative",
                "Re-evaluate existing-tool integration if interface, access, duplicate handling, ownership, and value are established.",
            ),
            RecommendationAlternative(
                "APP-004",
                "Future alternative",
                "Evaluate commercial software only if current tools prove insufficient and approval and cost evidence become available.",
            ),
        ),
        (
            ChangeTrigger(
                "TRIG-001",
                "The spreadsheet cannot support controlled status tracking or authorized access.",
                "Reconsider the configuration approach.",
            ),
            ChangeTrigger(
                "TRIG-002",
                "Calendar integration becomes feasible, owned, and sufficiently valuable.",
                "Evaluate integration or a hybrid approach.",
            ),
            ChangeTrigger(
                "TRIG-003",
                "Inquiry volume or manual burden materially exceeds current evidence.",
                "Reassess existing-tool scalability and architecture tradeoffs.",
            ),
            ChangeTrigger(
                "TRIG-004",
                "Maintenance ownership cannot be established.",
                "Do not proceed with custom development.",
            ),
        ),
    )
    package = DecisionPackage(
        options.engagement,
        "Select a responsible next step for lesson-inquiry visibility without treating qualitative findings as a formula.",
        approaches,
        criteria,
        conditions,
        evaluations,
        tradeoffs,
        perspectives,
        judgment,
        recommendation,
        (
            *(risk.title for risk in risks.risks),
            "Calendar interface feasibility is unknown.",
            "Baseline measurements are incomplete.",
        ),
        (
            (
                "E2",
                "NEED-001",
                "REQ-001",
                "CAP-001",
                "GAP-001",
                "APP-002",
                "ARCH-001",
                "INT-003",
                "BEN-001",
                "RISK-004",
                "CRIT-001",
                "JUDGMENT-001",
                "REC-001",
            ),
        ),
    )
    return validate_decision(package)


def integration_evidence_experiment(original: DecisionPackage | None = None) -> DecisionExperiment:
    """Add fictional interface evidence while retaining the authored recommendation."""
    base = original or harbor_street_decision_package()
    updated_evaluations = tuple(
        replace(
            evaluation,
            findings=tuple(
                replace(
                    finding,
                    state=FindingState.ESTABLISHED,
                    evidence_strength=EvidenceStrength.EXPERIMENTAL,
                    reason="Fictional experiment establishes interface, access, duplicate handling, and technical ownership.",
                    evidence_ids=("EXP-INT-001",),
                )
                if finding.approach_id == "APP-003" and finding.criterion_id == "CRIT-002"
                else finding
                for finding in evaluation.findings
            ),
        )
        for evaluation in base.evaluations
    )
    updated = replace(base, evaluations=updated_evaluations)
    return DecisionExperiment(
        "New integration evidence",
        base,
        updated,
        (
            "Calendar supports an appropriate interface.",
            "Access is available.",
            "Duplicate handling can be implemented.",
            "Technical ownership is assigned.",
        ),
        ("APP-003 implementation feasibility: Unknown → Established (experimental).",),
        (
            "Budget, baseline value, process readiness, and the authored recommendation did not change.",
        ),
        "Integration or a hybrid approach is now more viable, but professional judgment is not automatically replaced by one changed finding.",
    )


def scale_evidence_experiment(original: DecisionPackage | None = None) -> DecisionExperiment:
    """Add fictional scale evidence without inventing a final conclusion."""
    base = original or harbor_street_decision_package()
    updated = replace(
        base,
        risks_and_unknowns=(
            *base.risks_and_unknowns,
            "Experimental evidence shows substantially higher inquiry volume and manual handling burden.",
        ),
    )
    return DecisionExperiment(
        "New scale evidence",
        base,
        updated,
        (
            "Inquiry volume is substantially higher than the current evidence baseline.",
            "Manual handling burden is materially greater.",
        ),
        (
            "Value hypotheses gain a stronger measurement basis; existing-tool scalability and architecture tradeoffs require reassessment.",
        ),
        (
            "Integration feasibility, budget, ownership, and the authored recommendation did not change.",
        ),
        "Higher scale makes value and scalability concerns more salient, but does not by itself establish which alternative should proceed.",
    )
