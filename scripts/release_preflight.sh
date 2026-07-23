#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
SIMULATIONS="2000"
KEEP_OUTPUT=0

usage() {
  cat <<'USAGE'
Run v0.2 release checks without committing, pushing, tagging, or publishing.

Usage:
  fish scripts/release_preflight.fish [options]
  bash scripts/release_preflight.sh [options]

Options:
  -s, --simulations N   Reduced Monte Carlo draws. Default: 2000
      --keep-output     Preserve the temporary output directory
  -h, --help            Show this help
USAGE
}

while (($#)); do
  case "$1" in
    -s|--simulations)
      [[ $# -ge 2 ]] || { echo "$1 requires an integer" >&2; exit 2; }
      SIMULATIONS="$2"
      shift 2
      ;;
    --keep-output)
      KEEP_OUTPUT=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ "$SIMULATIONS" =~ ^[1-9][0-9]*$ ]] || {
  echo "--simulations must be a positive integer" >&2
  exit 2
}

cd -- "$PROJECT_DIR"

echo "Repairing canonical LF line endings and trailing whitespace..."
python scripts/normalize_whitespace.py --write
python scripts/normalize_whitespace.py
command -v git >/dev/null 2>&1 || { echo 'git is required' >&2; exit 1; }
command -v uv >/dev/null 2>&1 || { echo 'uv is required' >&2; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo 'This directory is not a Git repository.' >&2
  exit 1
}

CANONICAL_GIT_WHITESPACE='blank-at-eol,blank-at-eof,space-before-tab'
INHERITED_GIT_WHITESPACE="$(git config --show-origin --get core.whitespace 2>/dev/null || true)"
git config --local core.whitespace "$CANONICAL_GIT_WHITESPACE"
[[ -z "$INHERITED_GIT_WHITESPACE" ]] || \
  echo "Previous effective Git whitespace policy: $INHERITED_GIT_WHITESPACE"
echo "Repository Git whitespace policy: $CANONICAL_GIT_WHITESPACE"

grep -q '^version = "0.2.0"$' pyproject.toml || {
  echo 'pyproject.toml does not declare version 0.2.0' >&2
  exit 1
}
grep -q '^version: 0.2.0$' CITATION.cff || {
  echo 'CITATION.cff does not declare version 0.2.0' >&2
  exit 1
}
grep -q '^## 0.2.0 - 2026-07-22$' CHANGELOG.md || {
  echo 'CHANGELOG.md does not contain the expected v0.2.0 heading' >&2
  exit 1
}

TEMP_OUTPUT="$(mktemp -d -t agegate-v02-preflight.XXXXXX)"
cleanup() {
  if ((KEEP_OUTPUT == 0)); then
    rm -rf -- "$TEMP_OUTPUT"
  fi
}
trap cleanup EXIT

sync_args=(--extra dev --extra ui)
if [[ -f uv.lock ]]; then
  sync_args=(--locked "${sync_args[@]}")
fi

cat <<INFO
AgeGate Harms v0.2 release preflight
Repository: $PROJECT_DIR
Branch: $(git branch --show-current)
Origin: $(git remote get-url origin 2>/dev/null || echo missing)
Temporary output: $TEMP_OUTPUT
Simulation draws: $SIMULATIONS
INFO

uv sync "${sync_args[@]}"
# uv may create uv.lock after the first source cleanup. Normalize it before Git checks.
python scripts/normalize_whitespace.py --write
python scripts/normalize_whitespace.py
[[ ! -f uv.lock ]] || uv lock --check
uv run agegate-evidence \
  --config data/scenarios/quebec_bill9_v02.yaml \
  --evidence data/evidence.csv \
  --output "$TEMP_OUTPUT/evidence_coverage.csv"
uv run pytest
uv run ruff check .
uv run agegate-run \
  --config data/scenarios/quebec_bill9_v02.yaml \
  --evidence data/evidence.csv \
  --output "$TEMP_OUTPUT" \
  --simulations "$SIMULATIONS" \
  --seed 20260722
uv run python scripts/export_parameter_catalog.py \
  --config data/scenarios/quebec_bill9_v02.yaml \
  --evidence data/evidence.csv \
  --output "$TEMP_OUTPUT/parameter_catalog.csv"
git -c core.whitespace="$CANONICAL_GIT_WHITESPACE" diff --check
git -c core.whitespace="$CANONICAL_GIT_WHITESPACE" diff --cached --check

echo
echo 'Git status:'
git status -sb

echo
echo 'Unstaged diff summary:'
git diff --stat

echo
echo 'Staged diff summary:'
git diff --cached --stat

echo
echo 'Configured remotes:'
git remote -v

echo
if ((KEEP_OUTPUT == 1)); then
  echo "Preflight passed. Temporary results: $TEMP_OUTPUT"
else
  echo 'Preflight passed. Temporary results will be removed.'
fi
echo 'No commit, push, tag, pull request, or release was created.'
