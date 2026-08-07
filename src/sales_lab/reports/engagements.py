"""Chapter 19 summaries and package composition."""

# ruff: noqa: E501, RUF005, TC001 - renderer type imports document chapter boundaries.

from pathlib import Path
from typing import cast

from sales_lab.diagrams.engagements import (
    render_engagement_mermaid,
    render_traceability_mermaid,
)
from sales_lab.domain.decisions import DecisionPackage
from sales_lab.domain.demonstrations import DemonstrationReport
from sales_lab.domain.engagements import (
    EngagementComparison,
    EngagementPackage,
    EngagementStage,
    SalesEngineeringEngagement,
)
from sales_lab.domain.handoffs import DeliveryPackage
from sales_lab.domain.proposals import ProposalPackage
from sales_lab.domain.risks import RiskAnalysis
from sales_lab.domain.success import SuccessMeasurementPlan
from sales_lab.domain.value import ValueAnalysis
from sales_lab.reports.approaches import render_solution_approach_report
from sales_lab.reports.architecture import render_architecture_report
from sales_lab.reports.automation import render_automation_report
from sales_lab.reports.business_process import render_business_process_report
from sales_lab.reports.capabilities import render_capability_report
from sales_lab.reports.decisions import render_decision_report
from sales_lab.reports.demonstrations import render_demonstration_report
from sales_lab.reports.gaps import render_gap_report
from sales_lab.reports.handoffs import render_handoff_report
from sales_lab.reports.integrations import render_integration_report
from sales_lab.reports.markdown import (
    render_discovery_meeting_summary,
    render_initial_discovery_assessment,
    render_situation_summary,
)
from sales_lab.reports.proposals import render_customer_proposal, render_traceability
from sales_lab.reports.requirements import render_requirements_report
from sales_lab.reports.risks import render_risk_report
from sales_lab.reports.stakeholders import render_stakeholder_report
from sales_lab.reports.success import render_success_plan
from sales_lab.reports.value import render_value_report
from sales_lab.services.approaches import SolutionApproachAnalysis
from sales_lab.services.architecture import ArchitectureAnalysis
from sales_lab.services.automation import AutomationAnalysis
from sales_lab.services.business_process import ProcessModel
from sales_lab.services.capabilities import CapabilityAnalysis
from sales_lab.services.discovery_meeting import DiscoveryMeetingSummary
from sales_lab.services.gaps import GapAnalysis
from sales_lab.services.integrations import IntegrationAnalysis
from sales_lab.services.investigation import InitialDiscoveryAssessment
from sales_lab.services.requirements import RequirementsAnalysis
from sales_lab.services.situation_summary import SituationSummary
from sales_lab.services.stakeholders import StakeholderAnalysis


def _output(engagement: SalesEngineeringEngagement, stage: EngagementStage) -> object:
    output = engagement.result(stage).output
    if output is None:
        msg = f"{stage.value} has no output"
        raise ValueError(msg)
    return output


def render_engagement_summary(engagement: SalesEngineeringEngagement) -> str:
    """Summarize existing conclusions without claiming approval or implementation."""
    decision = cast("DecisionPackage", _output(engagement, EngagementStage.RECOMMENDATION))
    proposal = cast("ProposalPackage", _output(engagement, EngagementStage.PROPOSAL))
    handoff = cast("DeliveryPackage", _output(engagement, EngagementStage.HANDOFF))
    success = cast(
        "SuccessMeasurementPlan", _output(engagement, EngagementStage.SUCCESS_MEASUREMENT)
    )
    sections = (
        ("Engagement", engagement.customer),
        ("Original Customer Statement", decision.context),
        ("Evidence-Supported Problem", decision.recommendation.need_addressed),
        (
            "Current-State Summary",
            "Inquiry information is split across a spreadsheet, manual follow-up, and a separate calendar.",
        ),
        (
            "Key Stakeholders",
            "Prospective students or parents, authorized staff, instructors, and the manager.",
        ),
        (
            "Established Requirements",
            "Traceable status visibility, confirmed schedule visibility, and preservation of the unapproved-budget constraint.",
        ),
        (
            "Capability Gaps",
            "Inquiry status is partial; instructor calendar access and cross-role sharing remain incompletely established.",
        ),
        ("Candidate Approaches", ", ".join(name for _, name in decision.approaches)),
        (
            "Candidate Architectures",
            "Existing-tool enhancement and unified-application logical candidates.",
        ),
        (
            "Major Integration Questions",
            "Calendar interface, access, ownership, failure, and duplicate behavior.",
        ),
        ("Automation Boundaries", "Human approval and exception ownership remain explicit."),
        (
            "Value Readiness",
            "Benefits remain hypotheses and missing financial inputs are not zero.",
        ),
        ("Major Risks and Assumptions", "; ".join(decision.risks_and_unknowns)),
        ("Recommendation", decision.recommendation.statement),
        (
            "Demonstration Findings",
            "The narrow deterministic demonstration supplies evidence, not production readiness.",
        ),
        ("Proposal Decision Request", proposal.decision_request.statement),
        ("Delivery Readiness", handoff.readiness.value),
        ("Success Measurement Readiness", success.lifecycle_status),
        ("Unresolved Questions", "; ".join(engagement.unresolved_questions)),
        (
            "End-to-End Traceability",
            f"{len(engagement.trace_links)} structured links; {len(engagement.validation_findings)} validation findings.",
        ),
        (
            "Educational Limitations",
            "Recommendation is not approval; demonstration is not production readiness; implementation and realized value are not claimed.",
        ),
    )
    return (
        "# End-to-End Sales Engineering Engagement Summary\n\n"
        + "\n\n".join(f"## {title}\n\n{text}" for title, text in sections)
        + "\n"
    )


def build_engagement_package(engagement: SalesEngineeringEngagement) -> EngagementPackage:
    """Compose the existing chapter renderers into deterministic files."""

    def out(stage: EngagementStage) -> object:
        return _output(engagement, stage)

    proposal = cast("ProposalPackage", out(EngagementStage.PROPOSAL))
    documents = (
        (
            "00-situation.md",
            render_situation_summary(cast("SituationSummary", out(EngagementStage.SITUATION))),
        ),
        (
            "01-investigation.md",
            render_initial_discovery_assessment(
                cast("InitialDiscoveryAssessment", out(EngagementStage.INVESTIGATION))
            ),
        ),
        (
            "02-discovery.md",
            render_discovery_meeting_summary(
                cast("DiscoveryMeetingSummary", out(EngagementStage.DISCOVERY))
            ),
        ),
        (
            "03-process.md",
            render_business_process_report(cast("ProcessModel", out(EngagementStage.PROCESS))),
        ),
        (
            "04-stakeholders.md",
            render_stakeholder_report(
                cast("StakeholderAnalysis", out(EngagementStage.STAKEHOLDERS))
            ),
        ),
        (
            "05-requirements.md",
            render_requirements_report(
                cast("RequirementsAnalysis", out(EngagementStage.REQUIREMENTS))
            ),
        ),
        (
            "06-capabilities.md",
            render_capability_report(cast("CapabilityAnalysis", out(EngagementStage.CAPABILITIES))),
        ),
        ("07-gaps.md", render_gap_report(cast("GapAnalysis", out(EngagementStage.GAPS)))),
        (
            "08-approaches.md",
            render_solution_approach_report(
                cast("SolutionApproachAnalysis", out(EngagementStage.APPROACHES))
            ),
        ),
        (
            "09-architecture.md",
            render_architecture_report(
                cast("ArchitectureAnalysis", out(EngagementStage.ARCHITECTURE))
            ),
        ),
        (
            "10-integrations.md",
            render_integration_report(
                cast("IntegrationAnalysis", out(EngagementStage.INTEGRATIONS))
            ),
        ),
        (
            "11-automation.md",
            render_automation_report(cast("AutomationAnalysis", out(EngagementStage.AUTOMATION))),
        ),
        ("12-value.md", render_value_report(cast("ValueAnalysis", out(EngagementStage.VALUE)))),
        ("13-risks.md", render_risk_report(cast("RiskAnalysis", out(EngagementStage.RISKS)))),
        (
            "14-recommendation.md",
            render_decision_report(cast("DecisionPackage", out(EngagementStage.RECOMMENDATION))),
        ),
        (
            "15-demonstration.md",
            render_demonstration_report(
                cast("DemonstrationReport", out(EngagementStage.DEMONSTRATION))
            ),
        ),
        ("16-proposal.md", render_customer_proposal(proposal)),
        ("16-internal-decision-package.md", render_traceability(proposal)),
        (
            "17-handoff.md",
            render_handoff_report(cast("DeliveryPackage", out(EngagementStage.HANDOFF))),
        ),
        (
            "18-success.md",
            render_success_plan(
                cast("SuccessMeasurementPlan", out(EngagementStage.SUCCESS_MEASUREMENT))
            ),
        ),
        ("19-engagement-summary.md", render_engagement_summary(engagement)),
        (
            "traceability.md",
            "# Engagement Traceability Index\n\n```mermaid\n"
            + render_traceability_mermaid(engagement)
            + "```\n",
        ),
        (
            "engagement-flow.md",
            "# Engagement Flow\n\n```mermaid\n" + render_engagement_mermaid() + "```\n",
        ),
    )
    return EngagementPackage(engagement.identifier, documents)


def export_engagement_package(package: EngagementPackage, output_dir: Path) -> tuple[Path, ...]:
    """Write deterministic UTF-8 package artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = tuple(output_dir / name for name, _ in package.documents)
    for path, (_, content) in zip(paths, package.documents, strict=True):
        path.write_text(content, encoding="utf-8")
    return paths


def render_scenario_comparison(comparison: EngagementComparison) -> str:
    """Render a neutral table without a winner, score, or forecast."""
    headings = ("Stage",) + comparison.scenario_ids
    separator = tuple("---" for _ in headings)
    rows = (headings, separator, *comparison.rows)
    return (
        "# Engagement Scenario Comparison\n\n"
        + "\n".join("| " + " | ".join(row) + " |" for row in rows)
        + "\n\nNo overall winner is produced.\n"
    )
