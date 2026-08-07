"""Command-line interface for the laboratory."""

from typing import Annotated

import typer

from sales_lab.diagrams.business_process import render_process_mermaid
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
from sales_lab.reports.approaches import render_solution_approach_report
from sales_lab.reports.architecture import render_architecture_report
from sales_lab.reports.automation import render_automation_report
from sales_lab.reports.business_process import render_business_process_report
from sales_lab.reports.capabilities import render_capability_report
from sales_lab.reports.gaps import render_gap_report
from sales_lab.reports.integrations import render_integration_report
from sales_lab.reports.markdown import (
    render_discovery_meeting_summary,
    render_initial_discovery_assessment,
    render_situation_summary,
)
from sales_lab.reports.requirements import render_requirements_report
from sales_lab.reports.risks import render_risk_report
from sales_lab.reports.stakeholders import render_stakeholder_report
from sales_lab.reports.value import render_value_report
from sales_lab.services.approaches import analyze_solution_approaches
from sales_lab.services.architecture import analyze_architectures
from sales_lab.services.automation import analyze_harbor_street_automation
from sales_lab.services.business_process import validate_business_process
from sales_lab.services.capabilities import analyze_capabilities
from sales_lab.services.discovery_meeting import build_discovery_meeting_summary
from sales_lab.services.gaps import analyze_gaps
from sales_lab.services.integrations import (
    analyze_integrations,
    harbor_street_integration_strategies,
    integration_questions,
)
from sales_lab.services.investigation import build_initial_discovery_assessment
from sales_lab.services.requirements import analyze_requirements
from sales_lab.services.risks import analyze_harbor_street_risks
from sales_lab.services.situation_summary import build_situation_summary
from sales_lab.services.stakeholders import analyze_stakeholders
from sales_lab.services.value import analyze_harbor_street_value

app = typer.Typer(
    help="Explore the executable Sales Engineering laboratory.",
    no_args_is_help=True,
)


@app.command()
def info() -> None:
    """Describe the purpose and current status of the laboratory."""
    typer.echo(
        "Executable Sales Engineering Laboratory\n"
        "A deterministic, code-first environment for learning Sales Engineering.\n"
        "Chapter 0 status: ready; customer facts remain separate from assumptions."
    )


@app.command()
def chapters() -> None:
    """List the educational chapters available in the laboratory."""
    typer.echo(
        "Chapters\n"
        "0. Setting Up the Sales Engineering Laboratory\n"
        "1. Customer Problems vs. Customer Symptoms\n"
        "2. Discovery Meetings\n"
        "3. Business Process Modeling"
        "\n4. Stakeholder Analysis"
        "\n5. Requirements Engineering"
        "\n6. Capability Mapping"
        "\n7. Current Capabilities & Gap Analysis"
        "\n8. Solution Approaches"
        "\n9. Future-State Solution Architecture"
        "\n10. Integration Strategies"
        "\n11. Automation Opportunities and Human-in-the-Loop Design"
        "\n12. Cost, Benefit, and Value Analysis"
        "\n13. Risks, Assumptions, Dependencies, and Constraints"
    )


@app.command()
def examples(
    *,
    verbose: Annotated[
        bool,
        typer.Option(help="Show additional guidance about future examples."),
    ] = False,
) -> None:
    """List deterministic examples available in the laboratory."""
    message = "Examples\nHarbor Street Music — customer situation setup check"
    if verbose:
        message += " Uses fixed customer-supplied inputs and reproducible output."
    typer.echo(message)


@app.command()
def situation() -> None:
    """Print the deterministic Chapter 0 customer situation."""
    summary = build_situation_summary(harbor_street_music_situation())
    typer.echo(render_situation_summary(summary), nl=False)


@app.command()
def investigate() -> None:
    """Print the deterministic Chapter 1 initial discovery assessment."""
    assessment = build_initial_discovery_assessment(harbor_street_music_discovery())
    typer.echo(render_initial_discovery_assessment(assessment), nl=False)


@app.command()
def discovery() -> None:
    """Print the deterministic Chapter 2 discovery meeting summary."""
    meeting = harbor_street_music_discovery_meeting()
    summary = build_discovery_meeting_summary(meeting)
    typer.echo(render_discovery_meeting_summary(summary), nl=False)


@app.command()
def process() -> None:
    """Print the Chapter 3 current-state workflow, Mermaid diagram, and report."""
    model = validate_business_process(harbor_street_music_business_process())
    terminal_names = ", ".join(step.description for step in model.terminal_steps)
    typer.echo(
        "Workflow Summary\n"
        f"Process: {model.process.name}\n"
        f"Start: {model.start_step.description}\n"
        f"Terminal steps: {terminal_names}\n\n"
        "Mermaid Diagram\n"
        "```mermaid\n"
        f"{render_process_mermaid(model)}```\n\n"
        f"{render_business_process_report(model)}",
        nl=False,
    )


@app.command()
def stakeholders() -> None:
    """Print the Chapter 4 evidence-bounded stakeholder analysis and report."""
    analysis = analyze_stakeholders(
        harbor_street_music_business_process(), harbor_street_music_stakeholder_map()
    )
    typer.echo(render_stakeholder_report(analysis), nl=False)


@app.command()
def requirements() -> None:
    """Print the Chapter 5 evidence-traceable requirements analysis."""
    analysis = analyze_requirements(
        harbor_street_music_requirements(), harbor_street_music_stakeholder_map()
    )
    typer.echo(render_requirements_report(analysis), nl=False)


@app.command()
def capabilities() -> None:
    """Print the Chapter 6 vendor-neutral capability mapping analysis."""
    analysis = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    typer.echo(render_capability_report(analysis), nl=False)


@app.command()
def gaps() -> None:
    """Print the Chapter 7 evidence-based current capability gap analysis."""
    required = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    analysis = analyze_gaps(required, harbor_street_music_current_capability_inventory())
    typer.echo(render_gap_report(analysis), nl=False)


@app.command()
def approaches() -> None:
    """Print the Chapter 8 neutral alternative analysis without selecting a winner."""
    required = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    gaps_analysis = analyze_gaps(required, harbor_street_music_current_capability_inventory())
    analysis = analyze_solution_approaches(gaps_analysis, harbor_street_music_solution_options())
    typer.echo(render_solution_approach_report(analysis), nl=False)


@app.command()
def architecture() -> None:
    """Print Chapter 9 logical candidates, traceability, and validation findings."""
    required = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    gaps_analysis = analyze_gaps(required, harbor_street_music_current_capability_inventory())
    approaches_analysis = analyze_solution_approaches(
        gaps_analysis, harbor_street_music_solution_options()
    )
    analysis = analyze_architectures(approaches_analysis, harbor_street_music_architectures())
    typer.echo(render_architecture_report(analysis), nl=False)


@app.command()
def integrations() -> None:
    """Print Chapter 10 alternatives, dependencies, failures, and traceability."""
    required = analyze_capabilities(
        harbor_street_music_requirements(),
        harbor_street_music_stakeholder_map(),
        harbor_street_music_capability_map(),
    )
    gaps_analysis = analyze_gaps(required, harbor_street_music_current_capability_inventory())
    approaches_analysis = analyze_solution_approaches(
        gaps_analysis, harbor_street_music_solution_options()
    )
    architecture_analysis = analyze_architectures(
        approaches_analysis, harbor_street_music_architectures()
    )
    analysis = analyze_integrations(
        architecture_analysis, harbor_street_integration_strategies(), integration_questions()
    )
    typer.echo(render_integration_report(analysis), nl=False)


@app.command()
def automation() -> None:
    """Print Chapter 11 candidate modes, human accountability, and guardrails."""
    typer.echo(render_automation_report(analyze_harbor_street_automation()), nl=False)


@app.command()
def value() -> None:
    """Print Chapter 12 supported claims, unknowns, and fictional experiments."""
    typer.echo(render_value_report(analyze_harbor_street_value()), nl=False)


@app.command()
def risks() -> None:
    """Print Chapter 13 traceable risks and related registers without scoring."""
    typer.echo(render_risk_report(analyze_harbor_street_risks()), nl=False)


if __name__ == "__main__":  # pragma: no cover - exercised by the installed entry point.
    app()
