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
