"""Deterministic Markdown report for Chapter 11."""

# ruff: noqa: E501 - long Markdown rows and educational sentences are intentional output.

from sales_lab.diagrams.automation import render_approval_mermaid, render_human_loop_mermaid
from sales_lab.services.automation import AutomationAnalysis


def render_automation_report(analysis: AutomationAnalysis) -> str:
    """Render assessments, accountability, guardrails, traceability, and diagrams."""
    assessments = analysis.plan.assessments

    def bullets(values: tuple[str, ...]) -> list[str]:
        return [f"- {value}" for value in (values or ("None.",))]

    lines = [
        "# Automation Opportunity Analysis",
        "",
        "## 1. Engagement",
        f"- {analysis.plan.engagement}",
    ]
    sections = (
        (
            "2. Workflow Activities",
            tuple(f"{a.activity.identifier}: {a.activity.name}" for a in assessments),
        ),
        (
            "3. Activity Characteristics",
            tuple(
                f"{a.activity.name}: {', '.join(c.value for c in a.characteristics)}"
                for a in assessments
            ),
        ),
        (
            "4. Candidate Automation Modes",
            tuple(f"{a.activity.name}: {a.automation_mode.value}" for a in assessments),
        ),
        (
            "5. Human Responsibilities",
            tuple(
                f"{a.activity.name}: {a.human_responsibility.role_id} — {a.human_responsibility.accountable_for}"
                for a in assessments
            ),
        ),
        (
            "6. Approval Boundaries",
            tuple(
                f"{a.activity.name}: {a.approval_boundary.approver_role_id} must approve; rejection → {a.approval_boundary.rejection_result}"
                for a in assessments
                if a.approval_boundary
            ),
        ),
        (
            "7. Exception Paths",
            tuple(
                f"{a.activity.name}: {e.condition} → {e.result} ({e.owner_role_id})"
                for a in assessments
                for e in a.exception_paths
            ),
        ),
        (
            "8. Automation Readiness",
            tuple(f"{a.identifier}: {a.readiness.value}" for a in assessments),
        ),
        (
            "9. Rules Not Yet Defined",
            tuple(f"{a.activity.name}: {r}" for a in assessments for r in a.unresolved_rules),
        ),
        (
            "10. Data Dependencies",
            tuple(f"{a.activity.name}: {d}" for a in assessments for d in a.data_dependencies),
        ),
        (
            "11. Automation Risks",
            tuple(f"{a.activity.name}: {', '.join(r.value for r in a.risks)}" for a in assessments),
        ),
        (
            "12. Activities Not Ready for Automation",
            tuple(
                f"{a.activity.name}: {a.readiness.value}"
                for a in assessments
                if a.unresolved_rules or a.readiness.value.startswith("Not ready")
            ),
        ),
        (
            "13. Unsupported Automation Proposals",
            tuple(
                f"{f.assessment_id}: {f.message}"
                for f in analysis.findings
                if f.kind == "Unsupported automation proposal"
            ),
        ),
    )
    for heading, values in sections:
        lines.extend(("", f"## {heading}", *bullets(values)))
    lines.extend(
        (
            "",
            "## 14. Responsibility Matrix",
            "",
            "| Activity | System Responsibility | Human Responsibility | Approval Required | Exception Owner |",
            "|---|---|---|---|---|",
        )
    )
    for a in assessments:
        owners = ", ".join(e.owner_role_id for e in a.exception_paths) or "None"
        lines.append(
            f"| {a.activity.name} | {a.system_responsibility} | {a.human_responsibility.role_id}: {a.human_responsibility.accountable_for} | {'Yes' if a.approval_boundary else 'No'} | {owners} |"
        )
    lines.extend(
        (
            "",
            "## Automation Matrix",
            "",
            "| Activity | Characteristics | Candidate Mode | Human Role | Readiness | Open Questions |",
            "|---|---|---|---|---|---|",
        )
    )
    lines.extend(
        f"| {a.activity.name} | {', '.join(c.value for c in a.characteristics)} | {a.automation_mode.value} | {a.human_responsibility.role_id} | {a.readiness.value} | {'; '.join(a.open_questions) or 'None'} |"
        for a in assessments
    )
    lines.extend(("", "## 15. Traceability"))
    lines.extend(
        bullets(
            tuple(
                " → ".join(
                    (
                        *a.evidence_ids,
                        *a.activity.process_step_ids,
                        *a.requirement_ids,
                        *a.capability_ids,
                        *a.architecture_ids,
                        a.activity.identifier,
                        a.identifier,
                        a.human_responsibility.role_id,
                    )
                )
                for a in assessments
            )
        )
    )
    lines.extend(("", "## 16. Open Questions"))
    lines.extend(bullets(tuple(q for a in assessments for q in a.open_questions)))
    lines.extend(
        (
            "",
            "## 17. Educational Limitations",
            "- Candidate modes are explicitly authored, not automatically optimized, scored, or recommended.",
            "- The model does not rank people, predict conversion, send messages, update calendars, use real time, or perform external actions.",
            "- Better evidence can improve implementability without proving desirability.",
            "",
            "## Mermaid Diagrams",
            "",
            "```mermaid",
            render_human_loop_mermaid(assessments[0]).rstrip(),
            "```",
            "",
            "```mermaid",
            render_approval_mermaid(assessments[2]).rstrip(),
            "```",
            "",
        )
    )
    return "\n".join(lines)
