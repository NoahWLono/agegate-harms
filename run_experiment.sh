#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$SCRIPT_DIR"

SIMULATIONS="${SIMULATIONS:-50000}"
SEED="${SEED:-20260722}"
CONFIG="${CONFIG:-data/scenarios/quebec_bill9_v02.yaml}"
EVIDENCE="${EVIDENCE:-data/evidence.csv}"
OUTPUT="${OUTPUT:-results}"
WITH_UI=1

usage() {
  cat <<'USAGE'
Run the complete AgeGate Harms v0.2 workflow.

Usage:
  fish run_experiment.fish [options]
  bash run_experiment.sh [options]

Options:
  -s, --simulations N   Monte Carlo draws. Default: 50000
      --seed N          Random seed. Default: 20260722
  -c, --config PATH     Scenario YAML
  -e, --evidence PATH   Evidence registry CSV
  -o, --output PATH     Output directory. Default: results
      --skip-ui         Do not sync the optional Streamlit dependency
  -h, --help            Show this help

SIMULATIONS, SEED, CONFIG, EVIDENCE, and OUTPUT may also be set as environment
variables. Explicit options take precedence.
USAGE
}

while (($#)); do
  case "$1" in
    -s|--simulations)
      [[ $# -ge 2 ]] || { echo "$1 requires an integer" >&2; exit 2; }
      SIMULATIONS="$2"
      shift 2
      ;;
    --seed)
      [[ $# -ge 2 ]] || { echo "$1 requires an integer" >&2; exit 2; }
      SEED="$2"
      shift 2
      ;;
    -c|--config)
      [[ $# -ge 2 ]] || { echo "$1 requires a path" >&2; exit 2; }
      CONFIG="$2"
      shift 2
      ;;
    -e|--evidence)
      [[ $# -ge 2 ]] || { echo "$1 requires a path" >&2; exit 2; }
      EVIDENCE="$2"
      shift 2
      ;;
    -o|--output)
      [[ $# -ge 2 ]] || { echo "$1 requires a path" >&2; exit 2; }
      OUTPUT="$2"
      shift 2
      ;;
    --skip-ui)
      WITH_UI=0
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
[[ "$SEED" =~ ^[0-9]+$ ]] || {
  echo "--seed must be a nonnegative integer" >&2
  exit 2
}
command -v uv >/dev/null 2>&1 || {
  echo "uv is missing. On Momiji run: sudo pacman -S --needed uv" >&2
  exit 1
}
[[ -f "$CONFIG" ]] || { echo "Configuration not found: $CONFIG" >&2; exit 1; }
[[ -f "$EVIDENCE" ]] || { echo "Evidence registry not found: $EVIDENCE" >&2; exit 1; }

CANONICAL_GIT_WHITESPACE='blank-at-eol,blank-at-eof,space-before-tab'
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git config --local core.whitespace "$CANONICAL_GIT_WHITESPACE"
fi

mkdir -p -- "$OUTPUT"

sync_args=(--extra dev)
if ((WITH_UI == 1)); then
  sync_args+=(--extra ui)
fi
if [[ -f uv.lock ]]; then
  sync_args=(--locked "${sync_args[@]}")
fi

cat <<INFO
AgeGate Harms v0.2 workflow
Project: $SCRIPT_DIR
Config: $CONFIG
Evidence: $EVIDENCE
Output: $OUTPUT
Simulations: $SIMULATIONS
Seed: $SEED
INFO

echo "1/6 Synchronizing dependencies..."
uv sync "${sync_args[@]}"
# The first sync can create uv.lock. Normalize it and every UTF-8 project file now.
python scripts/normalize_whitespace.py --write
python scripts/normalize_whitespace.py
if [[ -f uv.lock ]]; then
  uv lock --check
fi

echo "2/6 Validating evidence mappings..."
uv run agegate-evidence \
  --config "$CONFIG" \
  --evidence "$EVIDENCE" \
  --output "$OUTPUT/evidence_coverage.csv"

echo "3/6 Running automated tests..."
uv run pytest -v

echo "4/6 Running Ruff checks..."
uv run ruff check .

echo "5/6 Running the Monte Carlo experiment and report build..."
uv run agegate-run \
  --config "$CONFIG" \
  --evidence "$EVIDENCE" \
  --output "$OUTPUT" \
  --simulations "$SIMULATIONS" \
  --seed "$SEED"

echo "6/6 Exporting the parameter catalog..."
uv run python scripts/export_parameter_catalog.py \
  --config "$CONFIG" \
  --evidence "$EVIDENCE" \
  --output "$OUTPUT/parameter_catalog.csv"

echo
printf '%s\n' \
  "Complete." \
  "Report: $SCRIPT_DIR/$OUTPUT/REPORT.md" \
  "Dashboard: $SCRIPT_DIR/$OUTPUT/dashboard.html" \
  "Interactive UI: uv run streamlit run app.py"
