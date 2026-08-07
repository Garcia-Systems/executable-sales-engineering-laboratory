# Executable Sales Engineering Laboratory

[![CI](https://github.com/executable-laboratories/executable-sales-engineering-laboratory/actions/workflows/ci.yml/badge.svg)](https://github.com/executable-laboratories/executable-sales-engineering-laboratory/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An **executable textbook for learning Sales Engineering through deterministic simulations**.

This repository will connect the craft of technical discovery, solution design, demonstration,
validation, and communication to small programs that readers can run, inspect, test, and change.
Chapters 0–14 now progress from immutable customer facts through discovery and process modeling to
traceable requirements, capabilities, gaps, product-neutral approaches, and logical candidate
solution architectures, evidence-bounded integration strategies, and accountable automation
boundaries, auditable cost-and-value and risk analysis, and a transparent conditional recommendation.

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

The CLI exposes the chapter catalog and a deterministic setup scenario. The first scenario records
what is known before discovery begins; it neither diagnoses nor recommends a solution.

```console
uv run sales-lab info
uv run sales-lab chapters
uv run sales-lab examples
uv run sales-lab situation
uv run sales-lab investigate
uv run sales-lab discovery
uv run sales-lab process
uv run sales-lab stakeholders
uv run sales-lab requirements
uv run sales-lab capabilities
uv run sales-lab gaps
uv run sales-lab approaches
uv run sales-lab architecture
uv run sales-lab integrations
uv run sales-lab automation
uv run sales-lab value
uv run sales-lab risks
uv run sales-lab recommend
```

Run `uv run sales-lab --help` to see all commands and options.

## Repository layout

```text
.
├── .github/workflows/       # Continuous integration
├── docs/
│   ├── chapters/            # Chapter index and textbook prose
│   ├── diagrams/            # Future diagram sources
│   └── images/              # Future documentation images
├── examples/                # Learner-owned debugger entry points
├── src/sales_lab/
│   ├── domain/              # Immutable customer facts
│   ├── services/            # Structured deterministic summaries
│   ├── reports/             # Markdown presentation
│   ├── diagrams/            # Future diagram generation
│   ├── examples/            # Reusable fictional fixtures
│   └── cli.py               # Typer command-line entry point
└── tests/                    # Automated tests
```

The `src/` layout prevents accidental imports from the repository root. Package boundaries are
present now so later chapters can grow without coupling domain concepts to the CLI or output layers.

## Quality and deterministic design

Every change is checked with Ruff, MyPy in strict mode, pytest, and branch coverage. CI runs the same
commands on Python 3.13. The project targets 100% coverage for its current executable foundation.

```console
./scripts/check.sh
```

See [Before opening a pull request](CONTRIBUTING.md#before-opening-a-pull-request) for environment
setup, individual troubleshooting commands, and the GitHub Actions check contributors must pass.

Simulations use explicit inputs and stable ordering. Randomness, predictive models,
LLM dependencies, external services, and network-dependent behavior are outside the project scope.

## Roadmap

- [x] Establish Python 3.13 packaging, CLI, tests, type checking, linting, and CI.
- [x] Define the Chapter 0 interface and curriculum entry point.
- [x] Introduce an immutable customer situation and deterministic summary.
- [x] Add a reproducible Markdown report and Chapter 0 diagram.
- [x] Add a deterministic Chapter 2 discovery workflow and evidence-bounded meeting summary.
- [x] Model the Chapter 3 current-state workflow with explicit boundaries, gaps, and Mermaid output.
- [x] Map Chapter 4 roles, responsibilities, process participation, authority, and perspective gaps.
- [x] Translate evidence into validated, traceable Chapter 5 requirements and explicit unknowns.
- [x] Map Chapter 5 requirements to vendor-neutral Chapter 6 capabilities and explicit coverage gaps.
- [x] Assess Chapter 7 current resources, partial capabilities, unknowns, and evidence-based gaps.
- [x] Compare solution approaches in Chapter 8 without prematurely selecting products.
- [x] Model coherent future-state solution concepts in Chapter 9.
- [x] Compare manual, batch, API, webhook, and event-driven integration strategies in Chapter 10.
- [x] Explore automation boundaries and human judgment in Chapter 11.
- [x] Evaluate costs, benefits, and consequences without fabricated precision in Chapter 12.
- [x] Unify risks, assumptions, dependencies, constraints, issues, responses, and residual risk in Chapter 13.
- [x] Produce a transparent, evidence-traceable, conditional recommendation in Chapter 14.
- [ ] Define Chapter 15 demonstration and proof-of-concept evidence.

The unchecked items describe direction, not a promise of scope or delivery date. Proposals,
implementation planning, and customer-success systems remain future chapters. Chapter 15 is next.

## Contributing

Contributions are welcome once they preserve the project's educational clarity and deterministic
constraints. Start with [CONTRIBUTING.md](CONTRIBUTING.md) for setup, quality commands, and design
principles, and follow the [Code of Conduct](CODE_OF_CONDUCT.md). For a substantial chapter or
architectural proposal, open an issue before writing the implementation so its learning objective
and boundaries can be discussed first.

## License

This project is available under the [MIT License](LICENSE).
