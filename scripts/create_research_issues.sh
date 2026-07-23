#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd -- "$PROJECT_DIR"
command -v uv >/dev/null 2>&1 || {
  echo 'uv is required' >&2
  exit 1
}
uv run python scripts/create_research_issues.py "$@"
