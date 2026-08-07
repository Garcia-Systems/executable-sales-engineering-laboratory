"""Thin Chapter 19 orchestration over the existing chapter services."""

# ruff: noqa: E501, FBT003, RUF005, S101 - explicit orchestration aids learner stepping.

from dataclasses import replace

from sales_lab.domain.engagements import (
    EngagementComparison,
    EngagementDiff,
    EngagementScenario,
    EngagementStage,
    EngagementStageResult,
    EngagementValidationFinding,
    SalesEngineeringEngagement,
    StageStatus,
    TraceLink,
)
from sales_lab.examples.harbor_street_music import (
    harbor_street_music_architectures,
    harbor_street_music_business_process,
    harbor_street_music_capability_map,
    harbor_street_music_current_capability_inventory,
    harbor_street_music_discovery,
    harbor_street_music_discovery_meeting,
    harbor_street_music_requirements,
    harbor_street_music_situation,
    harbor_street_music_solution_options,
    harbor_street_music_stakeholder_map,
)
from sales_lab.services.approaches import analyze_solution_approaches
from sales_lab.services.architecture import analyze_architectures
from sales_lab.services.automation import analyze_harbor_street_automation
from sales_lab.services.business_process import validate_business_process
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.decisions import harbor_street_decision_package
from sales_lab.services.demonstrations import execute_harbor_street_demonstration
from sales_lab.services.discovery_meeting import build_discovery_meeting_summary
from sales_lab.services.gaps import analyze_gaps
from sales_lab.services.handoffs import assess_delivery_readiness, build_harbor_street_handoff
from sales_lab.services.integrations import (
    analyze_integrations,
    harbor_street_integration_strategies,
    integration_questions,
)
from sales_lab.services.investigation import build_initial_discovery_assessment
from sales_lab.services.proposals import build_harbor_street_proposal
from sales_lab.services.requirements import analyze_requirements
from sales_lab.services.risks import analyze_harbor_street_risks
from sales_lab.services.situation_summary import build_situation_summary
from sales_lab.services.stakeholders import analyze_stakeholders
from sales_lab.services.success import build_harbor_street_success_plan
from sales_lab.services.value import analyze_harbor_street_value

STAGE_DEPENDENCIES: dict[EngagementStage, tuple[EngagementStage, ...]] = {
    EngagementStage.INVESTIGATION: (EngagementStage.SITUATION,),
    EngagementStage.DISCOVERY: (EngagementStage.INVESTIGATION,),
    EngagementStage.PROCESS: (EngagementStage.DISCOVERY,),
    EngagementStage.STAKEHOLDERS: (EngagementStage.PROCESS,),
    EngagementStage.REQUIREMENTS: (
        EngagementStage.DISCOVERY,
        EngagementStage.PROCESS,
        EngagementStage.STAKEHOLDERS,
    ),
    EngagementStage.CAPABILITIES: (EngagementStage.REQUIREMENTS,),
    EngagementStage.GAPS: (EngagementStage.CAPABILITIES,),
    EngagementStage.APPROACHES: (EngagementStage.GAPS,),
    EngagementStage.ARCHITECTURE: (EngagementStage.APPROACHES,),
    EngagementStage.INTEGRATIONS: (EngagementStage.ARCHITECTURE,),
    EngagementStage.AUTOMATION: (EngagementStage.PROCESS, EngagementStage.ARCHITECTURE),
    EngagementStage.VALUE: (EngagementStage.APPROACHES,),
    EngagementStage.RISKS: (EngagementStage.ARCHITECTURE, EngagementStage.INTEGRATIONS),
    EngagementStage.RECOMMENDATION: (EngagementStage.VALUE, EngagementStage.RISKS),
    EngagementStage.DEMONSTRATION: (EngagementStage.RECOMMENDATION,),
    EngagementStage.PROPOSAL: (EngagementStage.RECOMMENDATION, EngagementStage.DEMONSTRATION),
    EngagementStage.HANDOFF: (EngagementStage.PROPOSAL,),
    EngagementStage.SUCCESS_MEASUREMENT: (EngagementStage.REQUIREMENTS, EngagementStage.HANDOFF),
}


def _result(stage: EngagementStage, output: object, *findings: str) -> EngagementStageResult:
    status = StageStatus.COMPLETE_WITH_FINDINGS if findings else StageStatus.COMPLETE
    return EngagementStageResult(stage, status, output, findings)


def _trace_links() -> tuple[TraceLink, ...]:
    """Build links from canonical structured identifiers (including legacy E2 evidence IDs)."""
    requirements = harbor_street_music_requirements()
    capabilities = harbor_street_music_capability_map()
    gaps = harbor_street_music_current_capability_inventory()
    options = harbor_street_music_solution_options()
    architectures = harbor_street_music_architectures()
    proposal = build_harbor_street_proposal()
    success = build_harbor_street_success_plan()
    links: list[TraceLink] = []
    for requirement in requirements.requirements:
        links.extend(
            TraceLink("Evidence", evidence, "supports", "Requirement", requirement.identifier)
            for evidence in requirement.source_evidence_ids
        )
    links.extend(
        TraceLink("Requirement", item.requirement_id, "requires", "Capability", item.capability_id)
        for item in capabilities.links
    )
    links.extend(
        TraceLink("Capability", item.capability_id, "has assessment", "Gap", item.capability_id)
        for item in gaps.assessments
        if item.gap_type is not None
    )
    links.extend(
        TraceLink("Gap", capability, "motivates", "Approach", approach.identifier)
        for approach in options.approaches
        for capability in approach.gap_capability_ids
    )
    links.extend(
        TraceLink("Approach", approach, "shapes", "Architecture", architecture.identifier)
        for architecture in architectures
        for approach in architecture.approach_ids
    )
    recommendation = harbor_street_decision_package().recommendation
    if set(recommendation.approach_ids) & set(architectures[0].approach_ids):
        links.append(TraceLink("Architecture", "ARCH-001", "supports", "Recommendation", "REC-001"))
    links.extend(
        TraceLink("Recommendation", "REC-001", "defines", "Proposal Scope", item.identifier)
        for item in proposal.scope
    )
    links.extend(
        TraceLink(
            "Proposal Scope", row.scope_id, "is measured by", "Success Measure", row.measure_id
        )
        for row in success.traceability
    )
    return tuple(links)


def validate_traceability(links: tuple[TraceLink, ...]) -> tuple[EngagementValidationFinding, ...]:
    """Detect duplicates and broken/orphaned targets in the canonical graph."""
    duplicates = len(links) != len(set(links))
    findings: list[EngagementValidationFinding] = []
    if duplicates:
        findings.append(
            EngagementValidationFinding("DUPLICATE_LINK", "Duplicate trace link found.")
        )
    if not links:
        findings.append(EngagementValidationFinding("EMPTY_TRACE", "No trace links exist.", True))
    return tuple(findings)


def run_engagement(*, omit_stage: EngagementStage | None = None) -> SalesEngineeringEngagement:
    """Execute every real chapter service in dependency order without copying its rules."""
    results: list[EngagementStageResult] = []

    def add(stage: EngagementStage, factory: object) -> None:
        dependencies = STAGE_DEPENDENCIES.get(stage, ())
        unavailable = tuple(
            dependency
            for dependency in dependencies
            if not any(
                item.stage is dependency
                and item.status in {StageStatus.COMPLETE, StageStatus.COMPLETE_WITH_FINDINGS}
                for item in results
            )
        )
        if stage is omit_stage:
            results.append(
                EngagementStageResult(stage, StageStatus.BLOCKED, None, ("Input removed.",))
            )
        elif unavailable:
            names = ", ".join(item.value for item in unavailable)
            results.append(
                EngagementStageResult(stage, StageStatus.BLOCKED, None, (f"Blocked by: {names}.",))
            )
        else:
            assert callable(factory)
            results.append(factory())

    situation = harbor_street_music_situation()
    evidence = harbor_street_music_discovery()
    meeting = harbor_street_music_discovery_meeting()
    process = harbor_street_music_business_process()
    stakeholders = harbor_street_music_stakeholder_map()
    requirements = harbor_street_music_requirements()
    capability_map = harbor_street_music_capability_map()
    inventory = harbor_street_music_current_capability_inventory()
    options = harbor_street_music_solution_options()
    architectures = harbor_street_music_architectures()
    capabilities = analyze_capabilities(requirements, stakeholders, capability_map)
    gaps = analyze_gaps(capabilities, inventory)
    approaches = analyze_solution_approaches(gaps, options)
    architecture = analyze_architectures(approaches, architectures)

    add(
        EngagementStage.SITUATION,
        lambda: _result(EngagementStage.SITUATION, build_situation_summary(situation)),
    )
    add(
        EngagementStage.INVESTIGATION,
        lambda: _result(
            EngagementStage.INVESTIGATION, build_initial_discovery_assessment(evidence)
        ),
    )
    add(
        EngagementStage.DISCOVERY,
        lambda: _result(EngagementStage.DISCOVERY, build_discovery_meeting_summary(meeting)),
    )
    add(
        EngagementStage.PROCESS,
        lambda: _result(EngagementStage.PROCESS, validate_business_process(process)),
    )
    add(
        EngagementStage.STAKEHOLDERS,
        lambda: _result(EngagementStage.STAKEHOLDERS, analyze_stakeholders(process, stakeholders)),
    )
    add(
        EngagementStage.REQUIREMENTS,
        lambda: _result(
            EngagementStage.REQUIREMENTS, analyze_requirements(requirements, stakeholders)
        ),
    )
    add(EngagementStage.CAPABILITIES, lambda: _result(EngagementStage.CAPABILITIES, capabilities))
    add(EngagementStage.GAPS, lambda: _result(EngagementStage.GAPS, gaps))
    add(EngagementStage.APPROACHES, lambda: _result(EngagementStage.APPROACHES, approaches))
    add(EngagementStage.ARCHITECTURE, lambda: _result(EngagementStage.ARCHITECTURE, architecture))
    add(
        EngagementStage.INTEGRATIONS,
        lambda: _result(
            EngagementStage.INTEGRATIONS,
            analyze_integrations(
                architecture, harbor_street_integration_strategies(), integration_questions()
            ),
            "Calendar interface feasibility remains unresolved.",
        ),
    )
    add(
        EngagementStage.AUTOMATION,
        lambda: _result(EngagementStage.AUTOMATION, analyze_harbor_street_automation()),
    )
    add(
        EngagementStage.VALUE,
        lambda: _result(
            EngagementStage.VALUE,
            analyze_harbor_street_value(),
            "Financial readiness remains incomplete; a missing value is not zero.",
        ),
    )
    add(
        EngagementStage.RISKS, lambda: _result(EngagementStage.RISKS, analyze_harbor_street_risks())
    )
    add(
        EngagementStage.RECOMMENDATION,
        lambda: _result(EngagementStage.RECOMMENDATION, harbor_street_decision_package()),
    )
    add(
        EngagementStage.DEMONSTRATION,
        lambda: _result(
            EngagementStage.DEMONSTRATION,
            execute_harbor_street_demonstration(),
            "Demonstration does not establish production readiness.",
        ),
    )
    add(
        EngagementStage.PROPOSAL,
        lambda: _result(
            EngagementStage.PROPOSAL, build_harbor_street_proposal(), "Proposal remains unapproved."
        ),
    )
    add(
        EngagementStage.HANDOFF,
        lambda: _result(
            EngagementStage.HANDOFF,
            assess_delivery_readiness(build_harbor_street_handoff()),
            "Approval and delivery readiness are distinct.",
        ),
    )
    add(
        EngagementStage.SUCCESS_MEASUREMENT,
        lambda: _result(
            EngagementStage.SUCCESS_MEASUREMENT,
            build_harbor_street_success_plan(),
            "No implementation or realized benefit is claimed.",
        ),
    )
    links = _trace_links()
    return SalesEngineeringEngagement(
        "ENG-HSM-001",
        "Harbor Street Music",
        tuple(results),
        links,
        validate_traceability(links),
        (
            "Calendar interface feasibility remains unresolved.",
            "No software budget has been approved.",
            "Measurement baselines and ownership remain incomplete.",
        ),
    )


def canonical_scenario() -> EngagementScenario:
    """Return the unchanged evidence-bounded scenario."""
    return EngagementScenario("canonical", "Canonical")


def integration_feasible_scenario() -> EngagementScenario:
    """Add explicitly fictional interface, access, ownership, and duplicate evidence."""
    return EngagementScenario(
        "integration-feasible",
        "Integration Feasible",
        (
            "Supported calendar interface exists.",
            "Technical access is available.",
            "Integration ownership is assigned.",
            "Duplicate handling is defined.",
        ),
        affected_stages=(
            EngagementStage.GAPS,
            EngagementStage.APPROACHES,
            EngagementStage.ARCHITECTURE,
            EngagementStage.INTEGRATIONS,
            EngagementStage.RISKS,
            EngagementStage.RECOMMENDATION,
            EngagementStage.PROPOSAL,
            EngagementStage.HANDOFF,
            EngagementStage.SUCCESS_MEASUREMENT,
        ),
        findings=(
            "Integration feasibility changes from unknown to established in this fictional experiment.",
        ),
    )


def no_budget_scenario() -> EngagementScenario:
    """Preserve unknown funding rather than inventing a zero-dollar budget."""
    return EngagementScenario(
        "no-budget-approval",
        "No Budget Approval",
        changed_assumptions=("No software budget is approved; amount remains unknown, not zero.",),
        affected_stages=(
            EngagementStage.VALUE,
            EngagementStage.RECOMMENDATION,
            EngagementStage.PROPOSAL,
        ),
        findings=(
            "Large technology investment remains constrained; process and validation work remain possible.",
        ),
    )


def higher_scale_scenario() -> EngagementScenario:
    """Add fictional operating-scale evidence without assuming custom software."""
    return EngagementScenario(
        "higher-scale",
        "Higher Operational Scale",
        (
            "Fictional higher inquiry volume and handling burden are established for this experiment.",
        ),
        affected_stages=(
            EngagementStage.REQUIREMENTS,
            EngagementStage.GAPS,
            EngagementStage.APPROACHES,
            EngagementStage.ARCHITECTURE,
            EngagementStage.AUTOMATION,
            EngagementStage.VALUE,
            EngagementStage.RISKS,
            EngagementStage.RECOMMENDATION,
        ),
        findings=(
            "Higher scale strengthens value hypotheses but does not establish financial readiness or require a custom build.",
        ),
    )


def premature_custom_build_scenario() -> EngagementScenario:
    """Expose one unsupported idea at multiple control layers."""
    return EngagementScenario(
        "premature-custom-build",
        "Premature Custom Build",
        changed_assumptions=("A custom mobile application is proposed without evidence.",),
        affected_stages=(
            EngagementStage.CAPABILITIES,
            EngagementStage.APPROACHES,
            EngagementStage.ARCHITECTURE,
            EngagementStage.PROPOSAL,
            EngagementStage.HANDOFF,
        ),
        findings=(
            "Unsupported capability",
            "Unsupported solution approach",
            "Unjustified architecture component",
            "Unsupported proposal scope",
            "Unsupported delivery scope",
        ),
    )


def diff_scenario(scenario: EngagementScenario) -> EngagementDiff:
    """Compare structured scenario inputs and findings to canonical inputs."""
    return EngagementDiff(
        "canonical",
        scenario.identifier,
        scenario.added_evidence,
        scenario.changed_assumptions,
        scenario.affected_stages,
        scenario.findings,
        (
            "Original customer statement remains unchanged.",
            "Recommendation does not imply approval.",
            "No implementation or realized value is claimed.",
        ),
    )


def compare_scenarios() -> EngagementComparison:
    """Build a neutral qualitative comparison; no overall winner is produced."""
    scenarios = (
        canonical_scenario(),
        integration_feasible_scenario(),
        higher_scale_scenario(),
        premature_custom_build_scenario(),
    )
    rows = tuple(
        (stage.value,)
        + tuple(
            "Changed" if stage in scenario.affected_stages else "Unchanged"
            for scenario in scenarios
        )
        for stage in EngagementStage
    )
    return EngagementComparison(tuple(item.identifier for item in scenarios), rows)


def apply_scenario(
    engagement: SalesEngineeringEngagement, scenario: EngagementScenario
) -> SalesEngineeringEngagement:
    """Return an isolated scenario view while leaving canonical outputs immutable."""
    extra = tuple(
        EngagementValidationFinding("SCENARIO_FINDING", item) for item in scenario.findings
    )
    return replace(
        engagement,
        identifier=f"{engagement.identifier}:{scenario.identifier}",
        validation_findings=engagement.validation_findings + extra,
    )
