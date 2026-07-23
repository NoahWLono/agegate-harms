#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

if (($#)); then
  echo "Usage: fish scripts/check_environment.fish" >&2
  exit 2
fi

missing=0

printf 'Project: %s\n' "$PROJECT_DIR"
printf 'OS: '
if [[ -f /etc/arch-release ]]; then
  echo 'Arch Linux detected'
else
  echo 'not Arch Linux; automatic pacman installation is unavailable'
fi

for command_name in fish bash python git uv; do
  printf '%s: ' "$command_name"
  if command -v "$command_name" >/dev/null 2>&1; then
    case "$command_name" in
      fish) fish --version ;;
      bash) bash --version | head -n 1 ;;
      python) python --version ;;
      git) git --version ;;
      uv) uv --version ;;
    esac
  else
    echo 'missing'
    missing=1
  fi
done

printf 'gh: '
if command -v gh >/dev/null 2>&1; then
  gh --version | head -n 1
else
  echo 'missing; required only for GitHub publishing and issue creation'
fi

for required in \
  pyproject.toml \
  data/scenarios/quebec_bill9_v02.yaml \
  data/evidence.csv \
  run_experiment.fish \
  run_experiment.sh; do
  if [[ ! -f "$PROJECT_DIR/$required" ]]; then
    echo "Required project file missing: $required" >&2
    missing=1
  fi
done

if [[ -f "$PROJECT_DIR/uv.lock" ]] && command -v uv >/dev/null 2>&1; then
  (cd -- "$PROJECT_DIR" && uv lock --check) || missing=1
else
  echo 'uv.lock: absent; the first successful uv sync on Momiji will create it'
fi

exit "$missing"
