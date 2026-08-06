"""Deterministic Chapter 10 integration analysis and simulations."""

# Validation messages are intentionally colocated for learner stepping.
# ruff: noqa: EM101, TRY003

from dataclasses import dataclass

from sales_lab.domain.architecture import SolutionArchitecture
from sales_lab.domain.integrations import (
    AssumptionStatus,
    FailureMode,
    FeasibilityState,
    IntegrationAssumption,
    IntegrationDependency,
    IntegrationDirection,
    IntegrationPattern,
    IntegrationQuestion,
    IntegrationStrategy,
    IntegrationTiming,
)
from sales_lab.services.architecture import ArchitectureAnalysis


@dataclass(frozen=True, slots=True)
class IntegrationFinding:
    """One stable validation finding."""

    strategy_id: str
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class IntegrationAnalysis:
    """Ordered alternatives and questions, deliberately without a winner."""

    architecture_analysis: ArchitectureAnalysis
    strategies: tuple[IntegrationStrategy, ...]
    findings: tuple[IntegrationFinding, ...]
    questions: tuple[IntegrationQuestion, ...]


@dataclass(frozen=True, slots=True)
class SimulationStep:
    """An observable deterministic simulation step."""

    action: str
    outcome: str


def _architecture(analysis: ArchitectureAnalysis, identifier: str) -> SolutionArchitecture | None:
    return next(
        (
            item.architecture
            for item in analysis.validations
            if item.architecture.identifier == identifier
        ),
        None,
    )


def validate_integration(
    architecture_analysis: ArchitectureAnalysis, strategy: IntegrationStrategy
) -> tuple[IntegrationFinding, ...]:
    """Detect missing, unsupported, contradictory, and unjustified integration claims."""
    findings: list[IntegrationFinding] = []
    architecture = _architecture(architecture_analysis, strategy.architecture_id)
    if architecture is None:
        return (
            IntegrationFinding(
                strategy.identifier,
                "Unsupported Architecture Reference",
                f"Architecture {strategy.architecture_id!r} is not in the analysis.",
            ),
        )
    component_ids = {item.identifier for item in architecture.components}
    if strategy.source_id not in component_ids:
        findings.append(
            IntegrationFinding(strategy.identifier, "Missing Source Component", strategy.source_id)
        )
    if strategy.destination_id not in component_ids:
        findings.append(
            IntegrationFinding(
                strategy.identifier, "Missing Destination Component", strategy.destination_id
            )
        )
    flow = next(
        (
            item
            for item in architecture.information_flows
            if item.identifier == strategy.information_flow_id
        ),
        None,
    )
    if flow is None:
        findings.append(
            IntegrationFinding(
                strategy.identifier,
                "Unjustified Integration",
                "No architectural information flow supports this integration.",
            )
        )
    else:
        connection = next(
            item for item in architecture.connections if item.identifier == flow.connection_id
        )
        if (strategy.source_id, strategy.destination_id) != (
            connection.source_id,
            connection.destination_id,
        ):
            findings.append(
                IntegrationFinding(
                    strategy.identifier,
                    "Contradictory Direction",
                    "Strategy endpoints contradict the one-way architecture connection.",
                )
            )
    if not strategy.information.strip():
        findings.append(
            IntegrationFinding(
                strategy.identifier, "Missing Exchanged Information", "Information must be named."
            )
        )
    if not strategy.traceability:
        findings.append(
            IntegrationFinding(
                strategy.identifier, "Missing Traceability", "No trace chain was supplied."
            )
        )
    if any(not dependency.known for dependency in strategy.dependencies):
        findings.append(
            IntegrationFinding(
                strategy.identifier,
                "Unverified External Interface",
                "An external interface dependency remains unresolved.",
            )
        )
    return tuple(findings)


def analyze_integrations(
    architecture_analysis: ArchitectureAnalysis,
    strategies: tuple[IntegrationStrategy, ...],
    questions: tuple[IntegrationQuestion, ...],
) -> IntegrationAnalysis:
    """Validate candidates in authored order; never score or select them."""
    identifiers = [item.identifier for item in strategies]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("integration strategy identifiers must be unique")
    findings = tuple(
        finding
        for strategy in strategies
        for finding in validate_integration(architecture_analysis, strategy)
    )
    return IntegrationAnalysis(architecture_analysis, strategies, findings, questions)


def harbor_street_integration_strategies() -> tuple[IntegrationStrategy, ...]:
    """Compare mechanisms for Chapter 9 FLOW-004 without promising a calendar API."""
    trace = ("E4", "REQ-002", "CAP-002", "CAP-002", "APP-003", "ARCH-001", "FLOW-004")
    unknown_interface = IntegrationDependency(
        "INT-DEP-CALENDAR", "Existing calendar programmatic interface availability", known=False
    )
    assumption = IntegrationAssumption(
        "INT-ASM-001",
        "The existing calendar supports programmatic integration.",
        AssumptionStatus.UNVERIFIED,
    )

    def candidate(  # noqa: PLR0913 - explicit educational dimensions belong together.
        identifier: str,
        pattern: IntegrationPattern,
        timing: IntegrationTiming,
        dependencies: tuple[IntegrationDependency, ...],
        assumptions: tuple[IntegrationAssumption, ...],
        feasibility: FeasibilityState,
        failure_modes: tuple[FailureMode, ...],
        human_work: str,
        interface_dependency: str,
    ) -> IntegrationStrategy:
        return IntegrationStrategy(
            identifier,
            "ARCH-001",
            "FLOW-004",
            "CMP-FOLLOWUP",
            "CMP-CALENDAR",
            "Confirmed Appointment",
            "Record confirmed schedule information.",
            pattern,
            IntegrationDirection.ONE_WAY,
            timing,
            dependencies,
            assumptions,
            feasibility,
            failure_modes,
            trace,
            human_work,
            interface_dependency,
        )

    return (
        candidate(
            "INT-001",
            IntegrationPattern.MANUAL_HANDOFF,
            IntegrationTiming.MANUAL,
            (),
            (),
            FeasibilityState.ESTABLISHED,
            (FailureMode.INVALID_DATA,),
            "Staff re-entry",
            "Human-readable calendar access",
        ),
        candidate(
            "INT-002",
            IntegrationPattern.FILE_BATCH,
            IntegrationTiming.SCHEDULED,
            (unknown_interface,),
            (assumption,),
            FeasibilityState.REQUIRES_VALIDATION,
            (FailureMode.INVALID_DATA, FailureMode.DUPLICATE_DELIVERY),
            "Export/import oversight",
            "File export and import",
        ),
        candidate(
            "INT-003",
            IntegrationPattern.REQUEST_RESPONSE_API,
            IntegrationTiming.ON_DEMAND,
            (unknown_interface,),
            (assumption,),
            FeasibilityState.REQUIRES_VALIDATION,
            (
                FailureMode.TIMEOUT,
                FailureMode.AUTHENTICATION_FAILURE,
                FailureMode.AUTHORIZATION_FAILURE,
            ),
            "Exception handling",
            "Unverified API endpoint and credentials",
        ),
        candidate(
            "INT-004",
            IntegrationPattern.WEBHOOK,
            IntegrationTiming.NEAR_REAL_TIME,
            (unknown_interface,),
            (assumption,),
            FeasibilityState.REQUIRES_VALIDATION,
            (FailureMode.DESTINATION_UNAVAILABLE, FailureMode.DUPLICATE_DELIVERY),
            "Exception handling",
            "Unverified push/receive interface",
        ),
        candidate(
            "INT-005",
            IntegrationPattern.EVENT_DRIVEN,
            IntegrationTiming.EVENT_DRIVEN,
            (unknown_interface,),
            (assumption,),
            FeasibilityState.NOT_EVALUATED,
            (FailureMode.DUPLICATE_DELIVERY, FailureMode.OUT_OF_ORDER_DELIVERY),
            "Exception handling",
            "Channel and consumer interfaces",
        ),
    )


def integration_questions() -> tuple[IntegrationQuestion, ...]:
    """Return bounded technical questions, distinguishing identity concerns."""
    return (
        IntegrationQuestion("Authentication", "How does the caller prove who it is?"),
        IntegrationQuestion("Authorization", "May that identity create or change appointments?"),
        IntegrationQuestion("Ownership", "Which process or system owns confirmed lesson status?"),
        IntegrationQuestion(
            "Recovery", "After a timeout, did the operation fail or only its response?"
        ),
    )


def simulate_manual_handoff() -> tuple[SimulationStep, ...]:
    """Expose the human boundary crossing without random errors."""
    return (
        SimulationStep("Read confirmed lesson", "Staff sees Confirmed Appointment"),
        SimulationStep("Enter calendar appointment", "One calendar entry is recorded"),
    )


def simulate_duplicate_delivery(*, idempotent: bool) -> tuple[SimulationStep, ...]:
    """Deliver the same event twice and show the chosen educational behavior."""
    second = (
        "Duplicate recognized; no second business effect"
        if idempotent
        else "Second appointment created"
    )
    return (
        SimulationStep("Deliver CONFIRMED_LESSON_CREATED event-001", "Appointment created"),
        SimulationStep("Deliver CONFIRMED_LESSON_CREATED event-001", second),
    )


def simulate_destination_failure() -> tuple[SimulationStep, ...]:
    """Record a fixed destination-unavailable outcome and defer recovery policy."""
    return (
        SimulationStep("Send confirmed lesson", "Attempt recorded"),
        SimulationStep("Reach destination", "Destination unavailable"),
        SimulationStep("Record failure", "DESTINATION_UNAVAILABLE"),
        SimulationStep("Ask recovery question", "What should happen next?"),
    )
