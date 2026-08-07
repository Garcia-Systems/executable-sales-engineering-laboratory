"""Deterministic Chapter 13 risk analysis and immutable experiments."""

# ruff: noqa: D103, E501, PLR0913, RUF001, RUF002

from dataclasses import replace

from sales_lab.domain.risks import (
    Applicability,
    ApproachRiskProfile,
    AssumptionExperiment,
    AssumptionRecord,
    AssumptionValidationStatus,
    ClassificationFinding,
    ConstraintRecord,
    ConstraintScope,
    DependencyCategory,
    DependencyRecord,
    DependencyStatus,
    IssueRecord,
    MitigationExperiment,
    QualitativeLevel,
    ResidualRisk,
    ResponseType,
    Risk,
    RiskAnalysis,
    RiskCategory,
    RiskEvidence,
    RiskRegister,
    RiskResponse,
    RiskStatus,
    RiskValueLink,
    ValidationAction,
)


def classify_statement(
    statement: str, evidence_state: str = ""
) -> tuple[ClassificationFinding, ...]:
    """Apply narrow teaching guardrails; never manufacture a risk from prose."""
    text = statement.casefold()
    findings: list[ClassificationFinding] = []
    if "currently" in text or "current process" in text:
        findings.append(
            ClassificationFinding(
                statement,
                "Possible issue classification",
                "The statement describes an existing condition rather than an uncertain future event.",
            )
        )
    if "no budget" in text or "budget has been approved" in text:
        findings.append(
            ClassificationFinding(
                statement,
                "Possible constraint or dependency",
                "Rewrite the uncertain future effect as a cause-event-consequence risk statement.",
            )
        )
    if (
        "no api" in text or "not feasible" in text or "absent" in text
    ) and "unknown" in evidence_state.casefold():
        findings.append(
            ClassificationFinding(
                statement,
                "Unsupported conclusion",
                "Unknown interface availability establishes neither absence nor infeasibility.",
            )
        )
    return tuple(findings)


def analyze_risks(register: RiskRegister) -> RiskAnalysis:
    """Validate references and derive transparent omissions in stable authored order."""
    risk_ids = {risk.identifier for risk in register.risks}
    evidence_ids = {item.evidence_id for item in register.evidence}
    for risk in register.risks:
        missing = set(risk.evidence_ids) - evidence_ids
        if missing:
            message = f"{risk.identifier} references unknown evidence: {sorted(missing)}"
            raise ValueError(message)
    response_risk_ids = {response.risk_id for response in register.responses}
    unvalidated = tuple(
        item
        for item in register.assumptions
        if item.validation_status
        in {AssumptionValidationStatus.UNVALIDATED, AssumptionValidationStatus.NOT_VALIDATABLE_YET}
        and item.validation_action is None
    )
    unresolved = tuple(
        item
        for item in register.dependencies
        if item.status is not DependencyStatus.SATISFIED
        and (item.owner_role is None or item.resolution_action is None)
    )
    findings = (
        *classify_statement("Staff currently copy confirmed appointments manually."),
        *classify_statement("The calendar has no API.", "Interface availability is unknown."),
        *classify_statement("No budget has been approved."),
    )
    return RiskAnalysis(
        register,
        unvalidated,
        unresolved,
        tuple(risk for risk in register.risks if risk.identifier not in response_risk_ids),
        tuple(response for response in register.responses if response.risk_id not in risk_ids),
        findings,
    )


def _risk(
    identifier: str,
    title: str,
    cause: str,
    event: str,
    consequence: str,
    categories: tuple[RiskCategory, ...],
    approaches: tuple[str, ...],
    trace: tuple[str, ...],
    evidence: tuple[str, ...],
    *,
    likelihood: QualitativeLevel = QualitativeLevel.UNKNOWN,
    impact: QualitativeLevel = QualitativeLevel.HIGH,
) -> Risk:
    return Risk(
        identifier,
        title,
        cause,
        event,
        consequence,
        categories,
        RiskStatus.UNDER_REVIEW,
        likelihood,
        impact,
        "The relevant feasibility, behavior, or baseline has not yet been established.",
        approaches,
        trace,
        evidence,
    )


def harbor_street_risk_register() -> RiskRegister:
    """Build risks explicitly from evidence established in Chapters 0–12."""
    evidence = (
        RiskEvidence(
            "E2",
            "Staff copy confirmed lessons from a spreadsheet to a separate calendar.",
            "Chapters 2–4 discovery and process evidence",
        ),
        RiskEvidence(
            "E5",
            "Technology ownership has not been established.",
            "Chapter 4 stakeholder evidence gap",
        ),
        RiskEvidence(
            "E7",
            "The organization has not approved a software budget.",
            "Chapter 0 constraint / Chapter 4 evidence",
        ),
        RiskEvidence(
            "INT-UNKNOWN",
            "Calendar interface availability remains unknown.",
            "Chapter 10 integration analysis",
        ),
        RiskEvidence(
            "AUT-DATA",
            "Reminder automation requires defined, complete inquiry status data.",
            "Chapter 11 automation readiness",
        ),
        RiskEvidence(
            "VAL-BASELINE",
            "Current inquiry-handling time and lost-inquiry outcomes have not been measured.",
            "Chapter 12 value analysis",
        ),
    )
    risks = (
        _risk(
            "RISK-001",
            "Calendar integration feasibility",
            "Existing calendar interface capabilities remain unverified.",
            "The candidate integration cannot exchange confirmed lesson information as designed.",
            "The architecture may require redesign, continued manual entry, or additional cost.",
            (RiskCategory.TECHNICAL, RiskCategory.INTEGRATION),
            ("APP-003", "APP-004", "APP-005"),
            (
                "E2",
                "REQ-004",
                "CAP-004",
                "GAP-004",
                "APP-003",
                "ARCH-001",
                "FLOW-004",
                "INT-003",
                "ASM-001",
                "RISK-001",
            ),
            ("E2", "INT-UNKNOWN"),
        ),
        _risk(
            "RISK-002",
            "Inquiry data quality",
            "Inquiry status values and ownership rules remain incompletely defined.",
            "Incomplete or inconsistent records cause reminders or reports to act on the wrong state.",
            "Staff may perform rework and expected visibility may not be realized.",
            (RiskCategory.DATA, RiskCategory.PROCESS),
            ("APP-002", "APP-004", "APP-005"),
            ("E2", "REQ-001", "CAP-001", "GAP-001", "APP-002", "AUT-001", "DEP-002", "RISK-002"),
            ("E2", "AUT-DATA"),
            likelihood=QualitativeLevel.MODERATE,
        ),
        _risk(
            "RISK-003",
            "Custom maintenance ownership",
            "Ongoing technical ownership and maintenance have not been assigned.",
            "Defects or required changes in a custom solution remain unresolved after implementation.",
            "Process reliability and expected benefits may degrade.",
            (RiskCategory.MAINTENANCE, RiskCategory.ORGANIZATIONAL),
            ("APP-005",),
            ("E5", "APP-005", "ARCH-002", "DEP-003", "RISK-003"),
            ("E5",),
        ),
        _risk(
            "RISK-004",
            "Value cannot be demonstrated",
            "Baseline handling time and outcome measures have not been captured.",
            "The organization cannot determine whether the change produced the intended benefit.",
            "Value hypotheses remain unsupported and future decisions lack outcome evidence.",
            (RiskCategory.VALUE_REALIZATION,),
            ("APP-001", "APP-002", "APP-003", "APP-004", "APP-005"),
            ("E2", "REQ-001", "CAP-001", "APP-002", "BEN-001", "RISK-004"),
            ("VAL-BASELINE",),
            impact=QualitativeLevel.MODERATE,
        ),
    )
    assumptions = (
        AssumptionRecord(
            "ASM-001",
            "The existing calendar can receive confirmed lesson information programmatically.",
            "Chapter 10 unverified integration assumption",
            ("APP-003", "APP-004", "APP-005"),
            AssumptionValidationStatus.UNVALIDATED,
            ValidationAction(
                "Review platform documentation and conduct a technical proof of concept.",
                "Technology owner—not established",
            ),
            "Use a documented manual handoff or redesign the integration.",
            ("INT-UNKNOWN",),
        ),
    )
    dependencies = (
        DependencyRecord(
            "DEP-001",
            "Software budget approval",
            DependencyCategory.COMMERCIAL,
            ("APP-004", "APP-005"),
            DependencyStatus.UNRESOLVED,
            ("E7",),
            "Implementation may be delayed or reduced in scope.",
            ValidationAction("Establish approval authority and funding decision date."),
            None,
        ),
        DependencyRecord(
            "DEP-002",
            "Defined lesson-confirmation and inquiry-status states",
            DependencyCategory.DATA,
            ("AUT-001", "RISK-002"),
            DependencyStatus.RESOLUTION_PLANNED,
            ("AUT-DATA",),
            "Automation cannot distinguish eligible records reliably.",
            ValidationAction(
                "Facilitate a rule-definition workshop.", "Store manager and front desk staff"
            ),
            "Store manager",
        ),
        DependencyRecord(
            "DEP-003",
            "Technical ownership",
            DependencyCategory.ORGANIZATIONAL,
            ("APP-003", "APP-005", "RISK-003"),
            DependencyStatus.UNKNOWN,
            ("E5",),
            "Administration, support, and maintenance may remain unassigned.",
            None,
            None,
        ),
    )
    constraints = (
        ConstraintRecord(
            "CON-001",
            "No approved software budget has yet been established.",
            ConstraintScope.CUSTOMER,
            "E7",
            ("APP-004", "APP-005"),
        ),
        ConstraintRecord(
            "CON-002",
            "No external API may be assumed.",
            ConstraintScope.LABORATORY,
            "Chapter 10 evidence boundary",
            ("APP-003", "APP-004", "APP-005"),
        ),
        ConstraintRecord(
            "CON-003",
            "The laboratory and generated analysis must remain deterministic.",
            ConstraintScope.LABORATORY,
            "Repository educational design",
            (),
        ),
        ConstraintRecord(
            "CON-004",
            "Customer data must not be sent to external systems in this educational scenario.",
            ConstraintScope.LABORATORY,
            "Repository educational design",
            (),
        ),
    )
    issues = (
        IssueRecord(
            "ISS-001",
            "Confirmed appointments are currently copied manually between separate spreadsheet and calendar artifacts.",
            ("E2",),
            "Reliable confirmed-lesson scheduling",
        ),
    )
    responses = (
        RiskResponse(
            "RESP-001",
            "RISK-001",
            ResponseType.INVESTIGATE,
            "Conduct a technical proof of concept before final architecture approval.",
            None,
            "Before committing to programmatic calendar integration",
            "Establish supported interface behavior without assuming feasibility.",
            "A supported interface may still impose limits or operational constraints.",
        ),
        RiskResponse(
            "RESP-002",
            "RISK-001",
            ResponseType.CONTINGENCY,
            "Use a documented manual scheduling handoff.",
            "Front desk staff",
            "The selected calendar configuration has no supported integration interface",
            "Preserve confirmed scheduling while the architecture is revised.",
            "Manual duplicate entry and reconciliation remain.",
        ),
        RiskResponse(
            "RESP-003",
            "RISK-002",
            ResponseType.REDUCE,
            "Validate required status and ownership fields before enabling reminder rules.",
            "Store manager and front desk staff",
            "Before automation is enabled",
            "Reduce incorrect reminder actions caused by missing state.",
            "Human entry errors and exceptions remain possible.",
        ),
    )
    residual = (
        ResidualRisk(
            "RES-001",
            "RISK-001",
            "A supported interface may impose usage limits, duplicate delivery behavior, or operational constraints.",
            QualitativeLevel.UNKNOWN,
            QualitativeLevel.MODERATE,
        ),
        ResidualRisk(
            "RES-002",
            "RISK-002",
            "Validated fields do not eliminate later entry errors or undocumented exceptions.",
            QualitativeLevel.MODERATE,
            QualitativeLevel.MODERATE,
        ),
    )
    approach_names = (
        ("APP-002", "Configure Existing Tools"),
        ("APP-004", "Buy Commercial Software"),
        ("APP-005", "Build Custom Software"),
        ("APP-007", "Status Quo"),
    )
    profiles = tuple(
        ApproachRiskProfile(
            identifier,
            name,
            tuple(
                (
                    risk.identifier,
                    Applicability.APPLICABLE
                    if identifier in risk.affected_approach_ids
                    else Applicability.NOT_APPLICABLE,
                )
                for risk in risks
            ),
        )
        for identifier, name in approach_names
    )
    return RiskRegister(
        "Harbor Street Music lesson inquiry process",
        "Candidate approaches, architecture, integration, automation, and value hypotheses from Chapters 0–12",
        risks,
        evidence,
        assumptions,
        dependencies,
        constraints,
        issues,
        responses,
        residual,
        profiles,
        (
            RiskValueLink(
                "BEN-001", "RISK-001", "Reduced manual scheduling effort may not be realized."
            ),
            RiskValueLink(
                "BEN-001", "RISK-004", "The benefit cannot be demonstrated without a baseline."
            ),
        ),
        tuple(
            (
                *risk.trace_ids,
                *(
                    response.identifier
                    for response in responses
                    if response.risk_id == risk.identifier
                ),
                *(item.identifier for item in residual if item.risk_id == risk.identifier),
            )
            for risk in risks
        ),
        (
            "Which calendar product and configuration are in use?",
            "Who owns technology administration?",
            "Who can approve software spending?",
        ),
    )


def analyze_harbor_street_risks() -> RiskAnalysis:
    return analyze_risks(harbor_street_risk_register())


def assumption_disproved_experiment(original: RiskAnalysis | None = None) -> AssumptionExperiment:
    """Return a new analysis while retaining the original object and authored history."""
    source = original or analyze_harbor_street_risks()
    evidence = RiskEvidence(
        "EXP-API-ABSENT",
        "The selected calendar configuration provides no supported integration interface.",
        "Chapter 13 experimental scenario",
    )
    assumption = replace(
        source.register.assumptions[0], validation_status=AssumptionValidationStatus.DISPROVED
    )
    risk = replace(
        source.register.risks[0],
        status=RiskStatus.RESPONSE_PLANNED,
        consequence="The documented manual scheduling contingency is required while the architecture is redesigned.",
    )
    updated_register = replace(
        source.register,
        assumptions=(assumption,),
        risks=(risk, *source.register.risks[1:]),
        evidence=(*source.register.evidence, evidence),
    )
    return AssumptionExperiment(
        source,
        analyze_risks(updated_register),
        evidence,
        "Not feasible for the selected configuration",
        "RESP-002",
    )


def mitigation_added_experiment(original: RiskAnalysis | None = None) -> MitigationExperiment:
    """Plan a mitigation for a response-free copy without closing or scoring its risk."""
    source = original or analyze_harbor_street_risks()
    risk = source.register.risks[2]
    action = ValidationAction("Conduct a proof of concept before final architecture approval.")
    response = RiskResponse(
        "EXP-RESP-001",
        risk.identifier,
        ResponseType.INVESTIGATE,
        action.action,
        None,
        "Before architecture approval",
        "Test the relevant technical premise.",
        "Maintenance ownership and post-release behavior remain uncertain.",
    )
    residual = ResidualRisk(
        "EXP-RES-001",
        risk.identifier,
        "A proof of concept does not establish ongoing maintenance ownership.",
        QualitativeLevel.UNKNOWN,
        QualitativeLevel.HIGH,
    )
    updated_risk = replace(risk, status=RiskStatus.RESPONSE_PLANNED)
    updated_register = replace(
        source.register,
        risks=tuple(
            updated_risk if item.identifier == risk.identifier else item
            for item in source.register.risks
        ),
        responses=(*source.register.responses, response),
        residual_risks=(*source.register.residual_risks, residual),
    )
    return MitigationExperiment(source, analyze_risks(updated_register), action)
