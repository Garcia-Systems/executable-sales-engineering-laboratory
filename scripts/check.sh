#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
build_directory="$(mktemp -d)"
trap 'rm -rf "$build_directory"' EXIT

run_check() {
  printf '\n==> %s\n' "$1"
  shift
  "$@"
}

run_check "Ruff lint" python -m ruff check .
run_check "Ruff format check" python -m ruff format --check .
run_check "MyPy type check" python -m mypy src tests
run_check "Tests and coverage" python -m pytest
run_check "Installed CLI smoke test" sales-lab info
run_check "Package build" python -m build --outdir "$build_directory"

printf '\nAll quality checks passed.\n'
