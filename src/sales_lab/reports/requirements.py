"""Deterministic Chapter 5 requirements report and traceability matrix."""
# ruff: noqa: PERF401

from sales_lab.diagrams.requirements import render_requirements_mermaid
from sales_lab.domain.requirements import RequirementType
from sales_lab.services.requirements import RequirementsAnalysis


def render_traceability_matrix(analysis: RequirementsAnalysis) -> str:
    """Resolve stakeholder and evidence identifiers into an auditable table."""
    roles = {item.identifier: item.name for item in analysis.stakeholder_map.roles}
    rows = [
        "| Requirement | Type | Stakeholder | Evidence | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in analysis.requirement_set.requirements:
        rows.append(
            "| "
            + " | ".join(
                (
                    item.identifier or "(blank)",
                    item.requirement_type.value,
                    roles.get(item.stakeholder_id, item.stakeholder_id or "(blank)"),
                    ", ".join(item.source_evidence_ids) or "None",
                    item.status.value,
                )
            )
            + " |"
        )
    return "\n".join(rows) + "\n"


def render_requirements_report(analysis: RequirementsAnalysis) -> str:
    """Render all mandated report sections in stable order."""
    requirements = analysis.requirement_set.requirements

    def category(kind: RequirementType) -> tuple[str, ...]:
        return tuple(
            f"{item.identifier}: {item.statement}"
            for item in requirements
            if item.requirement_type is kind
        ) or ("None established.",)

    criteria = tuple(
        f"{item.identifier} / {criterion.identifier}: Given {criterion.given}; when "
        f"{criterion.when}; then {criterion.then}."
        for item in requirements
        for criterion in item.acceptance_criteria
    ) or ("None established.",)
    findings = tuple(
        f"{item.requirement_id or '(blank)'} [{item.code}]: {item.message}"
        for item in analysis.findings
    ) or ("No validation findings.",)
    sections = (
        ("Engagement", (analysis.requirement_set.engagement,)),
        (
            "Requirements Overview",
            (
                (
                    "A requirement states a needed capability, constraint, quality, rule, or "
                    "outcome—not a preferred implementation."
                ),
                (
                    f"{len(analysis.accepted_requirements)} accepted of {len(requirements)} "
                    "supplied candidates."
                ),
            ),
        ),
        ("Functional Requirements", category(RequirementType.FUNCTIONAL)),
        ("Non-Functional Requirements", category(RequirementType.NON_FUNCTIONAL)),
        ("Business Rules", category(RequirementType.BUSINESS_RULE)),
        ("Constraints", category(RequirementType.CONSTRAINT)),
        ("Success Criteria", category(RequirementType.SUCCESS_CRITERION)),
        ("Acceptance Criteria", criteria),
    )
    lines = ["# Requirements Analysis"]
    for heading, items in sections:
        lines.extend(("", f"## {heading}", *(f"- {item}" for item in items)))
    lines.extend(("", "## Evidence Traceability", render_traceability_matrix(analysis).rstrip()))
    lines.extend(("", "## Requirements Not Yet Established"))
    lines.extend(
        f"- {item.area}: {item.status.value} (UNKNOWN does not mean NOT REQUIRED)."
        for item in analysis.requirement_set.unresolved
    )
    lines.extend(("", "## Validation Findings", *(f"- {item}" for item in findings)))
    lines.extend(
        (
            "",
            "## Educational Limitations",
            (
                "- Vocabulary checks are transparent guardrails, not semantic classifiers; "
                "context and professional judgment remain necessary."
            ),
            (
                "- The service validates only supplied candidates and never generates unsupported "
                "requirements, performance targets, priorities, products, or architecture."
            ),
            "",
            "## Mermaid Diagram",
            "```mermaid",
            render_requirements_mermaid().rstrip(),
            "```",
        )
    )
    return "\n".join(lines) + "\n"
