"""Deterministic Chapter 18 measurement planning and fictional experiments."""

# ruff: noqa: C901, E501, PLR0913 - authored fixtures keep the measurement definition together.

from dataclasses import replace
from decimal import Decimal

from sales_lab.domain.success import (
    Baseline,
    BaselineStatus,
    BenefitValidation,
    CorrectiveAction,
    CustomerSuccessReview,
    EvidenceSource,
    IndicatorTiming,
    MeasurementFinding,
    MeasurementOwner,
    MeasurementReadiness,
    MeasureStatus,
    MeasureType,
    ObservationPeriod,
    ObservationPeriodType,
    ObservedValue,
    OutcomeFinding,
    SuccessMeasure,
    SuccessMeasurementPlan,
    SuccessState,
    TargetCondition,
    TraceabilityRow,
    UnintendedConsequence,
    ValidationStatus,
)
from sales_lab.examples.harbor_street_music import harbor_street_music_requirements
from sales_lab.services.handoffs import OWNER_NOT_ESTABLISHED, build_harbor_street_handoff
from sales_lab.services.value import analyze_harbor_street_value


def _measure(
    identifier: str,
    name: str,
    purpose: str,
    measure_type: MeasureType,
    definition: str,
    unit: str,
    baseline: Baseline,
    target: str,
    evidence: EvidenceSource,
    period: ObservationPeriod,
    requirement_id: str,
    criterion_id: str,
    outcome_id: str,
    benefit_ids: tuple[str, ...] = (),
    *,
    ready: MeasurementReadiness = MeasurementReadiness.PARTIALLY_READY,
    timing: IndicatorTiming = IndicatorTiming.LEADING,
) -> SuccessMeasure:
    return SuccessMeasure(
        identifier,
        name,
        purpose,
        measure_type,
        definition,
        unit,
        baseline,
        TargetCondition(
            target,
            "Defined validation sample",
            "Documented invalid records",
            "Census of supplied sample",
            "Review and explain exceptions",
        ),
        evidence,
        period,
        MeasurementOwner(OWNER_NOT_ESTABLISHED),
        MeasureStatus.PLANNED,
        ready,
        timing,
        (requirement_id,),
        (criterion_id,),
        (outcome_id,),
        benefit_ids,
        ("No operational observation has occurred; implementation is not established.",),
    )


def validate_measurements(measures: tuple[SuccessMeasure, ...]) -> tuple[MeasurementFinding, ...]:
    """Validate explicit measures without inferring customer success."""
    findings: list[MeasurementFinding] = []
    for measure in sorted(measures, key=lambda item: item.identifier):
        if not measure.definition.strip() or not measure.unit.strip():
            findings.append(
                MeasurementFinding(
                    measure.identifier, "Vague measure", "Definition and unit must be explicit."
                )
            )
        if measure.baseline.status is BaselineStatus.NOT_ESTABLISHED:
            findings.append(
                MeasurementFinding(
                    measure.identifier,
                    "Missing baseline",
                    "Baseline must be collected; missing does not mean zero.",
                )
            )
        if not measure.evidence_source.name.strip():
            findings.append(
                MeasurementFinding(
                    measure.identifier,
                    "Missing evidence source",
                    "Measurement evidence source is not established.",
                )
            )
        if not measure.owner.established:
            findings.append(
                MeasurementFinding(
                    measure.identifier,
                    "Missing ownership",
                    "Measurement responsibility not established.",
                )
            )
        if not measure.observation_period.identifier.strip():
            findings.append(
                MeasurementFinding(
                    measure.identifier,
                    "Missing review period",
                    "A deterministic period identifier is required.",
                )
            )
        if not measure.target_condition.population.strip():
            findings.append(
                MeasurementFinding(
                    measure.identifier,
                    "Unsupported target condition",
                    "Target population is not established.",
                )
            )
        if measure.activity_only:
            findings.append(
                MeasurementFinding(
                    measure.identifier,
                    "Potential vanity metric",
                    "Activity is not connected to an established operational outcome.",
                )
            )
        if measure.measure_type is MeasureType.OUTCOME and not measure.evidence_source.name.strip():
            findings.append(
                MeasurementFinding(
                    measure.identifier,
                    "Unsupported outcome claim",
                    "No evidence supports an outcome claim.",
                )
            )
        if measure.measure_type is MeasureType.UNINTENDED_EFFECT:
            findings.append(
                MeasurementFinding(
                    measure.identifier,
                    "Unintended effect measure",
                    "Review intended gains alongside possible new burden.",
                )
            )
    return tuple(findings)


def build_harbor_street_success_plan() -> SuccessMeasurementPlan:
    """Reuse prior artifacts to build a plan, never fictional implementation results."""
    requirements = harbor_street_music_requirements()
    handoff = build_harbor_street_handoff()
    value = analyze_harbor_street_value()
    missing = Baseline(
        BaselineStatus.NOT_ESTABLISHED,
        "Collect during BASELINE_PERIOD; historical value is unknown.",
    )
    validation = Baseline(
        BaselineStatus.NOT_APPLICABLE,
        "Deterministic validation scenario, not an operational before/after baseline.",
    )
    first = ObservationPeriod(ObservationPeriodType.FIRST_REVIEW_PERIOD, "HSM-FIRST-REVIEW")
    initial = ObservationPeriod(
        ObservationPeriodType.INITIAL_VALIDATION_PERIOD, "HSM-INITIAL-VALIDATION"
    )
    inquiry = EvidenceSource(
        "Structured inquiry records",
        "Records can show entered data, not whether omitted inquiries existed.",
    )
    followup = EvidenceSource(
        "Follow-up history", "Completeness depends on consistent staff recording."
    )
    handoffs = EvidenceSource(
        "Scheduling-handoff records",
        "The repository validates deterministic behavior, not production operations.",
    )
    observation = EvidenceSource(
        "Process observation and staff review notes",
        "A supplied sample may not represent other periods.",
    )
    measures = (
        _measure(
            "SM-001",
            "Inquiry Status Coverage",
            "Assess adoption of visible workflow state.",
            MeasureType.ADOPTION,
            "Count and proportion of active inquiries containing one approved current status at the review point.",
            "count and proportion",
            missing,
            "All active inquiries in the supplied sample have one approved status.",
            inquiry,
            first,
            "REQ-001",
            "AC-001",
            "OUT-001",
            ("BEN-002",),
        ),
        _measure(
            "SM-002",
            "Follow-Up Ownership Visibility",
            "Assess whether responsibility is identifiable.",
            MeasureType.PROCESS,
            "Count and proportion of active inquiries with an identifiable responsible staff role.",
            "count and proportion",
            missing,
            "Each included active inquiry has one identifiable responsible role.",
            inquiry,
            first,
            "REQ-001",
            "AC-001",
            "OUT-002",
        ),
        _measure(
            "SM-003",
            "Ordered Follow-Up History",
            "Assess correct workflow use.",
            MeasureType.QUALITY,
            "Count of sampled active inquiries whose recorded follow-up events can be retrieved in chronological order.",
            "count",
            missing,
            "Every included inquiry returns its recorded events in chronological order.",
            followup,
            first,
            "REQ-001",
            "AC-001",
            "OUT-003",
        ),
        _measure(
            "SM-004",
            "Duplicate Scheduling Effects",
            "Detect duplicate downstream business effects.",
            MeasureType.OUTCOME,
            "Number of additional scheduling effects created by repeated delivery of the same logical confirmation in the deterministic validation scenario.",
            "additional business effects",
            validation,
            "Repeated delivery creates 0 additional scheduling effects in the supplied deterministic scenario.",
            handoffs,
            initial,
            "REQ-003",
            "AC-003",
            "OUT-004",
            ready=MeasurementReadiness.READY,
            timing=IndicatorTiming.LAGGING,
        ),
        _measure(
            "SM-005",
            "Manual Handoff Effort",
            "Test the time-reduction benefit hypothesis.",
            MeasureType.VALUE,
            "Staff minutes spent transferring confirmed lesson information into the scheduling process during the supplied period.",
            "minutes per confirmed lesson",
            missing,
            "Compare like-for-like baseline and follow-up samples; no reduction is promised.",
            observation,
            first,
            "REQ-003",
            "AC-003",
            "OUT-005",
            ("BEN-001",),
            ready=MeasurementReadiness.NOT_READY,
            timing=IndicatorTiming.LAGGING,
        ),
        _measure(
            "SM-006",
            "Inquiry Reconstruction Effort",
            "Test whether visibility reduces reconstruction effort.",
            MeasureType.VALUE,
            "Staff minutes required to determine current state and recorded history for each selected inquiry.",
            "minutes per selected inquiry",
            missing,
            "Compare like-for-like baseline and follow-up samples; do not convert time to cash automatically.",
            observation,
            first,
            "REQ-001",
            "AC-001",
            "OUT-006",
            ("BEN-001",),
            ready=MeasurementReadiness.NOT_READY,
            timing=IndicatorTiming.LAGGING,
        ),
        _measure(
            "SM-007",
            "Data-Entry Effort",
            "Monitor a possible burden introduced by the workflow.",
            MeasureType.UNINTENDED_EFFECT,
            "Staff minutes spent entering status and follow-up information for each included inquiry.",
            "minutes per inquiry",
            missing,
            "Review any increase alongside status coverage and note quality.",
            observation,
            first,
            "REQ-001",
            "AC-001",
            "OUT-007",
            ready=MeasurementReadiness.NOT_READY,
            timing=IndicatorTiming.LAGGING,
        ),
    )
    benefits = tuple(
        BenefitValidation(
            item.identifier,
            item.hypothesis,
            item.baseline_status,
            "SM-006"
            if item.identifier == "BEN-001"
            else "SM-001"
            if item.identifier == "BEN-002"
            else "OWNER_NOT_ESTABLISHED",
            item.evidence_status.value,
            None,
            ValidationStatus.NOT_READY,
            (item.uncertainty,),
        )
        for item in value.benefits
    )
    consequences = (
        UnintendedConsequence(
            "UC-001", "Status updates become mechanical and omit useful notes.", "SM-003"
        ),
        UnintendedConsequence("UC-002", "The defined workflow adds data-entry effort.", "SM-007"),
        UnintendedConsequence("UC-003", "Staff create shadow tracking systems.", "SM-001"),
    )
    actions = (
        CorrectiveAction(
            "CA-001",
            "Status usage is inconsistent.",
            "Clarify status definitions and revise training material.",
            "The defined review condition identifies inconsistent usage.",
            MeasurementOwner(OWNER_NOT_ESTABLISHED),
        ),
        CorrectiveAction(
            "CA-002",
            "Data-entry effort increases with no compensating operational gain.",
            "Review required fields and simplify the workflow boundary.",
            "SM-007 increases while intended outcome measures do not improve.",
            MeasurementOwner(OWNER_NOT_ESTABLISHED),
        ),
    )
    trace = tuple(
        TraceabilityRow(
            next(
                req.source_evidence_ids[0]
                for req in requirements.requirements
                if req.identifier == measure.requirement_ids[0]
            ),
            measure.requirement_ids[0],
            measure.success_criterion_ids[0],
            "REC-001",
            next(
                (
                    item.identifier
                    for item in handoff.scope_items
                    if measure.requirement_ids[0] in item.trace_ids
                ),
                "SCOPE-NOT-MAPPED",
            ),
            measure.identifier,
            measure.baseline.status,
            "NOT_OBSERVED",
            "PLANNED",
            "NOT_READY",
            "CA-001"
            if measure.identifier in {"SM-001", "SM-003"}
            else "CA-002"
            if measure.identifier == "SM-007"
            else "NONE",
        )
        for measure in measures
    )
    return SuccessMeasurementPlan(
        value.engagement,
        handoff.lifecycle_status.value,
        "Plan how delivery, adoption, process operation, outcomes, and value will be distinguished after an authorized implementation.",
        (
            ("OUT-001", "Active inquiries have a visible current status."),
            ("OUT-002", "Follow-up responsibility is identifiable."),
            ("OUT-003", "Recorded follow-up history is consistently ordered."),
            ("OUT-004", "Repeated confirmation creates no duplicate scheduling effect."),
            ("OUT-005", "Manual handoff and reconstruction effort can be compared honestly."),
        ),
        measures,
        validate_measurements(measures),
        benefits,
        consequences,
        actions,
        trace,
        (
            "Collect missing baseline samples before implementation or in an explicitly labeled initial period.",
            "Establish evidence-collection, outcome-validation, and corrective-decision owners.",
            "Review planned measures after an explicit implementation event; do not infer success from delivery.",
        ),
        (
            "Who owns measurement collection and review?",
            "What sampling periods and operational exceptions will the customer approve?",
            "Has any proposal scope been approved or implemented?",
        ),
    )


def experimental_reviews(plan: SuccessMeasurementPlan) -> tuple[CustomerSuccessReview, ...]:
    """Return independent fictional reviews; the canonical plan remains immutable."""
    owner = MeasurementOwner("Fictional experiment reviewer")
    positive = CustomerSuccessReview(
        "EXPERIMENTAL_MEASUREMENT_SCENARIO",
        "Positive operational evidence",
        (
            ObservedValue(
                "SM-001",
                "EXPERIMENT-BASELINE",
                Decimal(6),
                Decimal(20),
                "active inquiries with status",
            ),
            ObservedValue(
                "SM-001",
                "EXPERIMENT-FOLLOW-UP",
                Decimal(18),
                Decimal(20),
                "active inquiries with status",
            ),
        ),
        (
            OutcomeFinding(
                "SM-001",
                "Status coverage increased from 30% to 90%: 12 more of 20 inquiries, a 60 percentage-point change.",
                SuccessState.OUTCOME_OBSERVED,
                ValidationStatus.INCONCLUSIVE,
            ),
        ),
        (
            replace(
                plan.benefit_validations[1],
                observed_result="Status coverage improved in the fictional sample.",
                validation_status=ValidationStatus.PARTIALLY_SUPPORTED,
            ),
        ),
        (),
        (),
        (
            "Small fictional sample; no implementation, efficiency, revenue, or causal conclusion follows.",
        ),
        "Measure operational outcomes and unintended effects in a later supplied period.",
    )
    adoption = CustomerSuccessReview(
        "EXPERIMENTAL_MEASUREMENT_SCENARIO",
        "Adoption without outcome",
        (
            ObservedValue(
                "SM-001", "EXPERIMENT-FOLLOW-UP", Decimal(20), Decimal(20), "status coverage"
            ),
            ObservedValue(
                "SM-005", "EXPERIMENT-BASELINE", Decimal(8), Decimal(1), "minutes per handoff"
            ),
            ObservedValue(
                "SM-005", "EXPERIMENT-FOLLOW-UP", Decimal(8), Decimal(1), "minutes per handoff"
            ),
        ),
        (
            OutcomeFinding(
                "SM-001",
                "Adoption improved, but manual scheduling effort did not change.",
                SuccessState.ADOPTED,
                ValidationStatus.NOT_SUPPORTED,
            ),
        ),
        (
            replace(
                plan.benefit_validations[0],
                observed_result="No change in fictional handoff effort.",
                validation_status=ValidationStatus.NOT_SUPPORTED,
            ),
        ),
        (),
        (),
        ("Adoption does not automatically demonstrate efficiency or value.",),
        "Review handoff design without reversing the adoption finding.",
    )
    causality = CustomerSuccessReview(
        "EXPERIMENTAL_MEASUREMENT_SCENARIO",
        "Outcome with unclear causality",
        (
            ObservedValue("SM-006", "EXPERIMENT-BASELINE", Decimal(10), Decimal(1), "minutes"),
            ObservedValue("SM-006", "EXPERIMENT-FOLLOW-UP", Decimal(5), Decimal(1), "minutes"),
        ),
        (
            OutcomeFinding(
                "SM-006",
                "Inquiry handling improved while staffing also changed.",
                SuccessState.OUTCOME_OBSERVED,
                ValidationStatus.INCONCLUSIVE,
            ),
        ),
        (
            replace(
                plan.benefit_validations[0],
                observed_result="Fictional reconstruction effort decreased; attribution is unclear.",
                validation_status=ValidationStatus.INCONCLUSIVE,
            ),
        ),
        (),
        (),
        (
            "A concurrent staffing change prevents attribution of the entire difference to the solution.",
        ),
        "Design a comparison or collect contextual evidence.",
    )
    unintended = CustomerSuccessReview(
        "EXPERIMENTAL_MEASUREMENT_SCENARIO",
        "Unintended consequence",
        (
            ObservedValue(
                "SM-001", "EXPERIMENT-FOLLOW-UP", Decimal(18), Decimal(20), "status coverage"
            ),
            ObservedValue("SM-007", "EXPERIMENT-BASELINE", Decimal(1), Decimal(1), "minutes"),
            ObservedValue("SM-007", "EXPERIMENT-FOLLOW-UP", Decimal(3), Decimal(1), "minutes"),
        ),
        (
            OutcomeFinding(
                "SM-001",
                "Status coverage improved while average data-entry effort increased by two minutes.",
                SuccessState.OUTCOME_OBSERVED,
                ValidationStatus.PARTIALLY_SUPPORTED,
            ),
        ),
        (),
        (replace(plan.unintended_consequences[1], observed=True),),
        (replace(plan.corrective_actions[1], decision_owner=owner),),
        (
            "The intended outcome and unintended cost must be reviewed together; value remains conditional.",
        ),
        "Corrective review is required; the action is not automatically executed.",
    )
    return positive, adoption, causality, unintended
