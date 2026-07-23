# Virtual-machine build report

- **Project:** AgeGate Harms
- **Release candidate:** 0.2.0
- **Build date:** 2026-07-22
- **Target platform:** Momiji, Arch Linux
- **Recommended location:** `~/Projects/agegate-harms`

## Build result

The repository was upgraded locally from its public v0.1 design into a v0.2 evidence-baseline release candidate. The connected GitHub repository was read-only during this build, so no upstream branch, issue, commit, or pull request was created. A backup-safe local installer and complete source archive are distributed separately.

## Quality checks

- Configuration validation: passed.
- Evidence registry validation: passed.
- Evidence identifier mapping: 180 of 180 modeled inputs mapped.
- Automated tests: 27 passed.
- Python bytecode compilation: passed.
- Reduced 5,000-draw experiment: passed.
- Full 50,000-draw experiment: passed.
- Static charts visually inspected: passed.
- Static dashboard generated: passed.
- Run manifest with SHA-256 hashes generated: passed.
- Backup-safe Bash compatibility installer copy-only integration test: passed.
- Native Fish installer and runner structural coverage: passed.
- Hostile global Git whitespace-policy override tests: passed.
- Dependency-generated lockfile normalization test: passed.

## Evidence coverage at build time

The exact counts are written to `results/evidence_coverage.csv` and summarized in `results/REPORT.md`. Complete mapping does not imply that a parameter is empirical. Direct measurements remain the central research task.

## Reproducibility note

The VM could not access the Python package registry, so it could not generate a fresh `uv.lock`. The reference run used the package versions recorded in `results/run_manifest.json`. On Momiji, `uv sync` will resolve dependencies and create or update `uv.lock`; review and commit that lock file after the local build succeeds.

## Installation safety

The Momiji installer:

1. uses `~/Projects/agegate-harms` by default;
2. moves an existing `~/Downloads/agegate-harms` repository only when the target is absent;
3. creates a timestamped full backup before applying v0.2 files;
4. overlays files without deleting the existing `.git` directory;
5. does not commit, push, or change the public repository;
6. validates, tests, and runs the model locally.

## Human-research boundary

No interviews, user studies, retailer observations, accessibility sessions, or external expert reviews were fabricated. The repository contains protocols and backlog items for those tasks. See `RESEARCH_STATUS.md`.

## Fish and GitHub publication hardening

- Added native Fish entry points for bundle installation, full experiment execution, environment checks, issue creation, Momiji smoke testing, and release preflight.
- Added lock-aware dependency synchronization. A present `uv.lock` is enforced with `uv sync --locked` and `uv lock --check`.
- Retained Bash compatibility entry points for non-Fish environments, with syntax checks covering those files separately.
- Added 23 automated tests, including shell-entry-point permissions, native Fish workflow coverage, installer safety assertions, Bash syntax checks, and CI configuration checks.
- Added a GitHub Actions `momiji-fish` job using `archlinux:latest`. It installs the official Arch Fish, Python, Git, and `uv` packages, parses every Fish entry point, exercises the bundle installer, runs the experiment through Fish, and verifies the generated artifacts.
- Added `PUBLISHING.md`, a release-specific pull-request body, and release notes for the `v0.2.0` branch, tag, and GitHub release workflow.

The isolated build container could not install a Fish binary because outbound package-network access is disabled. Therefore, native Fish execution was not falsely claimed as a local VM result. The shared model workflow, full 50,000-draw experiment, evidence validation, Python tests, Bash syntax checks, and installer safety behavior were verified locally. Actual Fish parsing and execution are enforced by the included Arch Linux CI job and can be run immediately on Momiji with `fish scripts/momiji_smoke_test.fish`.
