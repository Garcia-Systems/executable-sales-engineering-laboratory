# Contributing

Thank you for helping make Sales Engineering education more rigorous and accessible.

## Before opening a pull request

1. Install Python 3.13 and create an isolated environment:

   ```console
   python3.13 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -e '.[dev]'
   ```
2. Optionally install the fast Git hooks with `pre-commit install`.
3. Run the complete local quality suite from any directory inside the repository:

   ```console
   ./scripts/check.sh
   ```

The script stops at the first failure and runs the same logical checks as CI. To troubleshoot a
specific failure, run the individual read-only checks from the repository root:

```console
python -m ruff check .
python -m ruff format --check .
python -m mypy src tests
python -m pytest
sales-lab info
python -m build
```

GitHub Actions runs automatically for every pull request. Its exact job/check name is
**Python quality checks**. Open the pull request's **Checks** tab, or expand a failed check near the
merge box, to see its logs. Do not merge a pull request until this required check passes. Repository
owners can select that exact name when configuring branch protection; this documentation does not
claim that branch protection is already enabled.

## Contribution principles

- Keep simulations deterministic: explicit inputs must always produce reproducible outputs.
- Add complete type hints and tests with every behavior change.
- Do not introduce randomness, machine learning, LLMs, external APIs, or hidden network access.
- Keep concepts small, inspectable, and connected to a clear learning objective.
- Separate educational explanations from domain, service, reporting, and presentation concerns.

Open an issue before proposing a substantial chapter or architectural change. Pull requests should
explain the learning objective, implementation choices, tests, and documentation impact. By
participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
