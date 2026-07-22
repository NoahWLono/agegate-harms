#!/usr/bin/env bash
set -euo pipefail

SIMULATIONS="${SIMULATIONS:-50000}"
SEED="${SEED:-20260722}"

uv sync --extra dev
uv run agegate-run --simulations "$SIMULATIONS" --seed "$SEED"
uv run pytest -v

printf '\nOpen results/dashboard.html in a browser.\n'
