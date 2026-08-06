"""Learner-owned Chapter 3 debugging laboratory."""

from sales_lab.diagrams.business_process import render_process_mermaid
from sales_lab.examples.harbor_street_music import harbor_street_music_business_process
from sales_lab.reports.business_process import render_business_process_report
from sales_lab.services.business_process import validate_business_process


def main() -> None:
    """Expose deterministic objects and transformations for debugger inspection."""
    process = harbor_street_music_business_process()  # Breakpoint 1: inspect frozen tuples.
    transitions = process.transitions  # noqa: F841  # Breakpoint 2: follow sources and targets.
    model = validate_business_process(process)  # Breakpoint 3: step into validation.
    mermaid = render_process_mermaid(model)  # Breakpoint 4: inspect stable node aliases.
    report = render_business_process_report(model)  # Breakpoint 5: compare evidence and gaps.
    print(mermaid, report, sep="\n")  # noqa: T201


if __name__ == "__main__":
    main()
