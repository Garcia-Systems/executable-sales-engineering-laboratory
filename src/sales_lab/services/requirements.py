"""Transparent construction and validation of evidence-bounded requirements."""
# ruff: noqa: C901, PLR0912, PERF401

from dataclasses import dataclass

from sales_lab.domain.requirements import Requirement, RequirementSet, RequirementStatus
from sales_lab.domain.stakeholders import StakeholderMap

AMBIGUOUS_TERMS = ("easy", "modern", "fast", "better", "user-friendly", "seamless", "robust")
SOLUTION_PHRASES = (
    "buy ",
    "install ",
    "replace with",
    "replace the",
    "use salesforce",
    "build an app",
    "move to aws",
    "implement a crm",
)


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """One deterministic, learner-readable validation result."""

    requirement_id: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class RequirementsAnalysis:
    """Structured output retaining input order and derived findings."""

    requirement_set: RequirementSet
    stakeholder_map: StakeholderMap
    findings: tuple[ValidationFinding, ...]

    @property
    def accepted_requirements(self) -> tuple[Requirement, ...]:
        """Return established candidates without validation errors, in supplied order."""
        invalid = {finding.requirement_id for finding in self.findings}
        return tuple(
            item
            for item in self.requirement_set.requirements
            if item.status is RequirementStatus.ESTABLISHED and item.identifier not in invalid
        )


def contains_solution_language(statement: str) -> bool:
    """Flag a deliberately small vocabulary of common premature implementations."""
    normalized = " ".join(statement.lower().split())
    return any(phrase in normalized for phrase in SOLUTION_PHRASES)


def analyze_requirements(
    requirement_set: RequirementSet, stakeholder_map: StakeholderMap
) -> RequirementsAnalysis:
    """Validate supplied candidates; never infer or generate a missing requirement."""
    findings: list[ValidationFinding] = []
    identifiers = tuple(item.identifier for item in requirement_set.requirements)
    known_roles = {role.identifier for role in stakeholder_map.roles}
    known_evidence = {item.identifier for item in stakeholder_map.evidence}
    duplicate_ids = {item for item in identifiers if identifiers.count(item) > 1}
    for requirement in requirement_set.requirements:
        identifier = requirement.identifier
        if not identifier.strip():
            findings.append(ValidationFinding(identifier, "BLANK_ID", "Identifier is blank."))
        if identifier in duplicate_ids:
            findings.append(
                ValidationFinding(
                    identifier, "DUPLICATE_ID", "Requirement identifier is duplicated."
                )
            )
        if not requirement.statement.strip():
            findings.append(
                ValidationFinding(identifier, "BLANK_STATEMENT", "Requirement statement is blank.")
            )
        lowered = requirement.statement.lower()
        ambiguous = tuple(term for term in AMBIGUOUS_TERMS if term in lowered)
        if ambiguous:
            findings.append(
                ValidationFinding(
                    identifier,
                    "AMBIGUOUS_LANGUAGE",
                    f"Observable definition missing for: {', '.join(ambiguous)}.",
                )
            )
        if contains_solution_language(requirement.statement):
            findings.append(
                ValidationFinding(
                    identifier,
                    "SOLUTION_LANGUAGE",
                    "Potential solution language detected; describe the needed capability instead.",
                )
            )
        if not requirement.source_evidence_ids:
            findings.append(
                ValidationFinding(identifier, "MISSING_EVIDENCE", "No source evidence is linked.")
            )
        for evidence_id in requirement.source_evidence_ids:
            if evidence_id not in known_evidence:
                findings.append(
                    ValidationFinding(
                        identifier,
                        "UNKNOWN_EVIDENCE",
                        f"Evidence '{evidence_id}' is not in the stakeholder evidence record.",
                    )
                )
        if requirement.stakeholder_id not in known_roles:
            findings.append(
                ValidationFinding(
                    identifier,
                    "UNKNOWN_STAKEHOLDER",
                    f"Stakeholder '{requirement.stakeholder_id}' is not recorded.",
                )
            )
        if (
            requirement.status is RequirementStatus.ESTABLISHED
            and not requirement.acceptance_criteria
        ):
            findings.append(
                ValidationFinding(
                    identifier,
                    "MISSING_ACCEPTANCE_CRITERIA",
                    "An established requirement needs an observable acceptance criterion.",
                )
            )
        for conflict_id in requirement.conflicts_with:
            if conflict_id in identifiers:
                findings.append(
                    ValidationFinding(
                        identifier,
                        "EXPLICIT_CONFLICT",
                        f"Explicitly conflicts with requirement '{conflict_id}'.",
                    )
                )
    return RequirementsAnalysis(requirement_set, stakeholder_map, tuple(findings))
