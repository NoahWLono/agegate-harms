#!/usr/bin/env bash
set -euo pipefail

VERSION="0.2.0"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/project"
TARGET="$HOME/Projects/agegate-harms"
DOWNLOADS_REPO="$HOME/Downloads/agegate-harms"
SIMULATIONS="50000"
SEED="20260722"
WITH_UI=1
WITH_GH=0
SKIP_BUILD=0
OPEN_DASHBOARD=0
ASSUME_YES=0

usage() {
  cat <<'USAGE'
Install the AgeGate Harms v0.2.0 local release on Momiji.

Usage:
  fish install-on-momiji.fish [options]
  bash install-on-momiji.sh [options]

Options:
  --target PATH         Install target. Default: ~/Projects/agegate-harms
  --simulations N       Monte Carlo draws. Default: 50000
  --seed N              Random seed. Default: 20260722
  --skip-ui             Do not install the optional Streamlit interface
  --with-gh             Install GitHub CLI through pacman when it is missing
  --skip-build          Copy and back up files only; skip dependencies and run
  --open-dashboard      Open results/dashboard.html after a successful run
  -y, --yes             Do not ask for confirmation
  -h, --help            Show this help

Safety behavior:
  * If the target is absent and ~/Downloads/agegate-harms exists, that repository
    is moved to the target first.
  * An existing target is copied to a timestamped sibling backup.
  * The v0.2.0 tree is overlaid without deleting an existing .git directory.
  * Nothing is committed, pushed, tagged, or released.
USAGE
}

while (($#)); do
  case "$1" in
    --target)
      [[ $# -ge 2 ]] || { echo "--target requires a path" >&2; exit 2; }
      TARGET="$2"
      shift 2
      ;;
    --simulations)
      [[ $# -ge 2 ]] || { echo "--simulations requires an integer" >&2; exit 2; }
      SIMULATIONS="$2"
      shift 2
      ;;
    --seed)
      [[ $# -ge 2 ]] || { echo "--seed requires an integer" >&2; exit 2; }
      SEED="$2"
      shift 2
      ;;
    --skip-ui)
      WITH_UI=0
      shift
      ;;
    --with-gh)
      WITH_GH=1
      shift
      ;;
    --skip-build)
      SKIP_BUILD=1
      shift
      ;;
    --open-dashboard)
      OPEN_DASHBOARD=1
      shift
      ;;
    -y|--yes)
      ASSUME_YES=1
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

TARGET="${TARGET/#\~/$HOME}"

[[ "$SIMULATIONS" =~ ^[1-9][0-9]*$ ]] || {
  echo "--simulations must be a positive integer" >&2
  exit 2
}
[[ "$SEED" =~ ^[0-9]+$ ]] || {
  echo "--seed must be a nonnegative integer" >&2
  exit 2
}
[[ -d "$SOURCE_DIR" && -f "$SOURCE_DIR/pyproject.toml" ]] || {
  echo "Bundle project directory is missing or incomplete: $SOURCE_DIR" >&2
  exit 1
}

cat <<INFO
AgeGate Harms v$VERSION local installation

Source: $SOURCE_DIR
Target: $TARGET
Existing Downloads repository: $DOWNLOADS_REPO
Simulations: $SIMULATIONS
Seed: $SEED
INFO

if ((ASSUME_YES == 0)); then
  read -r -p "Continue with backup and installation? [y/N] " answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Cancelled."; exit 0 ;;
  esac
fi

mkdir -p -- "$(dirname -- "$TARGET")"

if [[ ! -e "$TARGET" && -d "$DOWNLOADS_REPO" ]]; then
  echo "Moving existing repository from Downloads to Projects..."
  mv -- "$DOWNLOADS_REPO" "$TARGET"
fi

if [[ -e "$TARGET" && ! -d "$TARGET" ]]; then
  echo "Target exists but is not a directory: $TARGET" >&2
  exit 1
fi

BACKUP=""
if [[ -d "$TARGET" ]]; then
  timestamp="$(date +%Y%m%d-%H%M%S)"
  BACKUP="${TARGET}.backup-${timestamp}"
  suffix=0
  while [[ -e "$BACKUP" ]]; do
    suffix=$((suffix + 1))
    BACKUP="${TARGET}.backup-${timestamp}-${suffix}"
  done
  echo "Creating safety backup: $BACKUP"
  cp -a --reflink=auto -- "$TARGET" "$BACKUP"
fi

mkdir -p -- "$TARGET"
echo "Applying the v0.2.0 file overlay..."
cp -a -- "$SOURCE_DIR/." "$TARGET/"

if [[ -d "$TARGET/.git" ]]; then
  echo "Preserved Git metadata: $TARGET/.git"
else
  echo "No existing .git directory was found. The source is still runnable locally."
fi

if ((SKIP_BUILD == 1)); then
  echo
  echo "Copy-only installation completed."
  [[ -n "$BACKUP" ]] && echo "Backup: $BACKUP"
  echo "Target: $TARGET"
  exit 0
fi

install_arch_package() {
  local package="$1"
  if [[ ! -f /etc/arch-release ]] || ! command -v pacman >/dev/null 2>&1; then
    echo "Automatic package installation is configured for Arch Linux only." >&2
    echo "Install '$package' manually, then rerun this installer." >&2
    exit 1
  fi
  local pacman_args=(-S --needed)
  if ((ASSUME_YES == 1)); then
    pacman_args+=(--noconfirm)
  fi
  if ((EUID == 0)); then
    pacman "${pacman_args[@]}" "$package"
  elif command -v sudo >/dev/null 2>&1; then
    sudo pacman "${pacman_args[@]}" "$package"
  else
    echo "sudo is unavailable. Install '$package' as root, then rerun." >&2
    exit 1
  fi
}

for package_command in bash:bash fish:fish git:git python:python uv:uv; do
  command_name="${package_command%%:*}"
  package_name="${package_command##*:}"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Installing $package_name from the official Arch repository..."
    install_arch_package "$package_name"
  fi
done

if ((WITH_GH == 1)) && ! command -v gh >/dev/null 2>&1; then
  echo "Installing GitHub CLI from the official Arch repository..."
  install_arch_package github-cli
fi

cd -- "$TARGET"

echo "Checking shell entry-point syntax..."
for script in run_experiment.sh scripts/*.sh packaging/install-on-momiji.sh; do
  bash -n "$script"
done
for script in run_experiment.fish scripts/*.fish packaging/install-on-momiji.fish; do
  fish -n "$script"
done

run_args=(--simulations "$SIMULATIONS" --seed "$SEED")
if ((WITH_UI == 0)); then
  run_args+=(--skip-ui)
fi

echo "Running the complete native Fish experiment workflow..."
fish ./run_experiment.fish "${run_args[@]}"

echo
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Local Git status after installation:"
  git status --short
  echo
fi

echo "Installation and local run completed."
[[ -n "$BACKUP" ]] && echo "Backup: $BACKUP"
echo "Project: $TARGET"
echo "Report: $TARGET/results/REPORT.md"
echo "Dashboard: $TARGET/results/dashboard.html"
echo "Streamlit: cd '$TARGET'; and uv run streamlit run app.py"
echo "Publishing guide: $TARGET/PUBLISHING.md"

if ((WITH_GH == 1)); then
  echo "Research issues: authenticate, review the dry run, then run:"
  echo "  cd '$TARGET'"
  echo "  uv run python scripts/create_research_issues.py --dry-run"
  echo "  fish scripts/create_research_issues.fish"
fi

if ((OPEN_DASHBOARD == 1)); then
  if command -v xdg-open >/dev/null 2>&1 && [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    xdg-open "$TARGET/results/dashboard.html" >/dev/null 2>&1 &
  else
    echo "Could not open the dashboard automatically. Open it from the path above."
  fi
fi
