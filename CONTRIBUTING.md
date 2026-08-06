# Contributing

Thank you for helping make Sales Engineering education more rigorous and accessible.

## Development setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Create the environment and install all dependencies with `uv sync --all-extras --dev`.
3. Install Git hooks with `uv run pre-commit install`.
4. Run the quality suite before submitting a change:

   ```console
   uv run ruff format --check .
   uv run ruff check .
   uv run mypy
   uv run pytest
   ```

## Contribution principles

- Keep simulations deterministic: explicit inputs must always produce reproducible outputs.
- Add complete type hints and tests with every behavior change.
- Do not introduce randomness, machine learning, LLMs, external APIs, or hidden network access.
- Keep concepts small, inspectable, and connected to a clear learning objective.
- Separate educational explanations from domain, service, reporting, and presentation concerns.

Open an issue before proposing a substantial chapter or architectural change. Pull requests should
explain the learning objective, implementation choices, tests, and documentation impact. By
participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

