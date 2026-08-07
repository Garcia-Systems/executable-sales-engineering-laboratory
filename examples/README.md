# Examples

`debug_chapter_0.py` is a learner-owned entry point for inspecting the immutable Harbor Street Music
facts, structured summary, and rendered report. Run it from the repository root after installation:

```console
python examples/debug_chapter_0.py
```

## Chapter 1 debugging laboratory

Run `python examples/debug_chapter_1.py` and use the marked breakpoint locations to inspect immutable statements, observations, facts, questions, and the final ordered assessment.

## Chapter 2 debugging laboratory

Run `python examples/debug_chapter_2.py` and follow its five marked breakpoints to inspect an
immutable meeting as questions, responses, and sourced evidence are appended in chronological
order before the deterministic Markdown summary is rendered.

## Chapter 3 debugging laboratory

Run `python examples/debug_chapter_3.py`. Suggested breakpoints are marked at process creation,
transition inspection, validation, Mermaid generation, and report generation. Important variables
are `process.steps`, `transitions`, `model.terminal_steps`, `model.unknown_steps`, and `mermaid`.
Frozen dataclasses and tuples must remain unchanged; repeated runs must produce identical node
aliases, transition order, unknown markers, and Markdown.

## Chapter 4 debugging laboratory

Run `python examples/debug_chapter_4.py` or select **Debug Chapter 4 Stakeholders** in VS Code.
Follow the marked assignments from the Chapter 3 process through roles, responsibilities,
authority, evidence, perspective gaps, and the report. All domain objects and tuples remain
immutable, and repeated output remains deterministic.


## Chapter 5 debugging laboratory

Run `python examples/debug_chapter_5.py` or select **Debug Chapter 5 Requirements** in VS Code.
Inspect the marked evidence-to-validation and traceability-matrix breakpoints.

## Chapter 6 debugging laboratory

Run `python examples/debug_chapter_6.py` or select **Debug Chapter 6 Capabilities** in VS Code.
Follow requirements through explicit mappings, traceability validation, qualitative coverage, and
gap detection; then inspect the immutable unsupported-capability experiment.

## Chapter 7 debugging laboratory

Run `python examples/debug_chapter_7.py` or select **Debug Chapter 7 Gap Analysis** in VS Code.
Inspect the required capability, current resources, evidence, assessment, gap type, and originating
follow-up question without crossing into remedy selection.


## Chapter 8 debugging laboratory

Run `python examples/debug_chapter_8.py` or select **Debug Chapter 8 Solution Approaches** in VS Code.
Inspect gap-to-approach traceability, assumptions, constraints, evidence needs, qualitative tradeoffs,
feasibility, comparison, and the immutable unsupported mobile-app experiment.

## Chapter 9 debugging laboratory

Run `python examples/debug_chapter_9.py` or select **Debug Chapter 9 Architecture** in VS Code.
Follow requirement and capability links into components, connections, information flows, coverage,
unjustified-component findings, and unknown dependencies. The experiment helpers return new frozen
candidates rather than mutating the canonical architectures.


## Chapter 10 debugging laboratory

Run `python examples/debug_chapter_10.py` or select **Debug Chapter 10 Integrations** in VS Code. Follow the Chapter 9 information flow through patterns, data, dependencies, assumptions, feasibility, failures, and duplicate delivery.

## Chapter 11 debugging laboratory

Run `python examples/debug_chapter_11.py` or select **Debug Chapter 11 Automation** in VS Code.
Inspect the activity, characteristics, explicitly proposed mode, readiness, human responsibility,
approval boundary, exception paths, risks, and validation findings.


## Chapter 12 debugging laboratory

Run `python examples/debug_chapter_12.py` or select **Debug Chapter 12 Value Analysis** in VS Code. Inspect canonical unknowns, evidence statuses, immutable fictional scenarios, financial metrics, and deterministic sensitivity results.
