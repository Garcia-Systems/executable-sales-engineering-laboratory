# Executable Sales Engineering Laboratory

[![CI](https://github.com/executable-laboratories/executable-sales-engineering-laboratory/actions/workflows/ci.yml/badge.svg)](https://github.com/executable-laboratories/executable-sales-engineering-laboratory/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An **executable textbook for learning Sales Engineering through deterministic simulations**.

This repository will connect the craft of technical discovery, solution design, demonstration,
validation, and communication to small programs that readers can run, inspect, test, and change.
It currently provides the production-quality foundation for that curriculum; it intentionally does
not contain chapters or domain models yet.

## Vision

Sales Engineering sits between customer context and technical possibility. Its lessons are often
taught through anecdotes or vendor-specific playbooks. This laboratory aims to make its core
reasoning concrete and testable: claims become explicit inputs, decisions become inspectable rules,
and outcomes become reproducible artifacts.

The finished project will let learners study a concept in Markdown, execute its accompanying model,
and verify their understanding by changing controlled inputs. It will remain local-first and will
not depend on random behavior, machine learning, large language models, or external APIs.

## Educational philosophy

The laboratory is guided by five principles:

1. **Learn by executing.** Every substantive concept should eventually have a runnable expression.
2. **Prefer transparent systems.** Rules, assumptions, and calculations must be easy to inspect.
3. **Make results reproducible.** Given the same inputs, a simulation must produce the same output.
4. **Separate concepts from tools.** Lessons should teach durable Sales Engineering judgment rather
   than promote a vendor or platform.
5. **Treat quality as part of the lesson.** Types, tests, documentation, and clear boundaries model
   the rigor expected in customer-facing technical work.

## Repository goals

- Build a coherent, chapter-based curriculum for Sales Engineering fundamentals.
- Pair future explanations with deterministic, typed Python simulations.
- Provide a CLI that makes chapters and examples easy to discover and execute.
- Produce reports and diagrams whose inputs and transformations are auditable.
- Maintain a welcoming reference implementation with strict automated quality checks.

## Installation

The project requires **Python 3.13**. [uv](https://docs.astral.sh/uv/) is recommended for fast,
reproducible environment and dependency management.

```console
git clone https://github.com/executable-laboratories/executable-sales-engineering-laboratory.git
cd executable-sales-engineering-laboratory
uv sync --all-extras --dev
```

To install the application with standard `pip` instead:

```console
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## CLI examples

The foundation includes three placeholder commands. They confirm the application is installed and
describe where educational material will appear without presenting unfinished content as a lesson.

```console
$ uv run sales-lab info
Executable Sales Engineering Laboratory
A deterministic, code-first environment for learning Sales Engineering.
Foundation status: ready for future chapters and simulations.

$ uv run sales-lab chapters
Chapters
No chapters have been published yet. The textbook foundation is ready for future lessons.

$ uv run sales-lab examples
Examples
No executable examples have been published yet.
```

Run `uv run sales-lab --help` to see all commands and options.

## Repository layout

```text
.
├── .github/workflows/       # Continuous integration
├── docs/
│   ├── chapters/            # Future textbook chapters
│   ├── diagrams/            # Future diagram sources
│   └── images/              # Future documentation images
├── examples/                # Future standalone executable examples
├── src/sales_lab/
│   ├── domain/              # Future domain concepts (currently empty)
│   ├── services/            # Future use-case orchestration
│   ├── reports/             # Future deterministic reporting
│   ├── diagrams/            # Future diagram generation
│   ├── examples/            # Future packaged examples
│   └── cli.py               # Typer command-line entry point
└── tests/                    # Automated tests
```

The `src/` layout prevents accidental imports from the repository root. Package boundaries are
present now so later chapters can grow without coupling domain concepts to the CLI or output layers.

## Quality and deterministic design

Every change is checked with Ruff, MyPy in strict mode, pytest, and branch coverage. CI runs the same
commands on Python 3.13. The project targets 100% coverage for its current executable foundation.

```console
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv run pre-commit run --all-files
```

Future simulations must use explicit inputs and stable ordering. Randomness, predictive models,
LLM dependencies, external services, and network-dependent behavior are outside the project scope.

## Roadmap

- [x] Establish Python 3.13 packaging, CLI, tests, type checking, linting, and CI.
- [ ] Define the curriculum map and chapter interface.
- [ ] Introduce the first deterministic Sales Engineering concept and simulation.
- [ ] Add reproducible reports and diagrams tied to learning objectives.
- [ ] Expand the example catalog and cross-chapter capstone exercises.

The unchecked items describe direction, not a promise of scope or delivery date. Domain models and
textbook content will be designed deliberately in later releases.

## Contributing

Contributions are welcome once they preserve the project's educational clarity and deterministic
constraints. Start with [CONTRIBUTING.md](CONTRIBUTING.md) for setup, quality commands, and design
principles, and follow the [Code of Conduct](CODE_OF_CONDUCT.md). For a substantial chapter or
architectural proposal, open an issue before writing the implementation so its learning objective
and boundaries can be discussed first.

## License

This project is available under the [MIT License](LICENSE).
