"""Deterministic Chapter 6 capability-boundary diagram."""

from sales_lab.services.capabilities import CapabilityAnalysis


def render_capability_mermaid(analysis: CapabilityAnalysis) -> str:
    """Show evidence-to-capability flow while stopping before product selection."""
    lines = [
        "flowchart LR",
        "    E[Discovery Evidence] --> R[Requirements]",
        "    P[Business Process] --> R",
        "    S[Stakeholders] --> R",
    ]
    for index, capability in enumerate(analysis.capability_map.capabilities, 1):
        lines.append(f"    R --> C{index}[{capability.name}]")
        lines.append(f"    C{index} --> Future[Future Solution Options]")
    lines.append('    Boundary["Capabilities ≠ Products"]')
    return "\n".join(lines) + "\n"
