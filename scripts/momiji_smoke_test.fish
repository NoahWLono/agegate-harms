#!/usr/bin/env fish

function fail --argument-names message
    printf 'Error: %s\n' "$message" >&2
    exit 1
end

set -l script_dir (cd (status dirname); and pwd -P)
or fail 'Could not resolve the scripts directory.'
set -l project_dir (cd "$script_dir/.."; and pwd -P)
or fail 'Could not resolve the project directory.'
cd -- "$project_dir"
or fail "Could not enter the project directory: $project_dir"

echo 'Checking native fish syntax...'
for fish_file in run_experiment.fish scripts/*.fish packaging/*.fish
    test -f "$fish_file"; or continue
    fish -n "$fish_file"
    or fail "Fish syntax check failed: $fish_file"
end

fish scripts/check_environment.fish
or fail 'Momiji environment check failed.'

type -q uv
or fail 'uv is required.'

set -g __agegate_smoke_output (mktemp -d -t agegate-fish-smoke.XXXXXX)
or fail 'Could not create a temporary output directory.'
function __agegate_smoke_cleanup --on-event fish_exit
    if test -n "$__agegate_smoke_output"; and test -d "$__agegate_smoke_output"
        rm -rf -- "$__agegate_smoke_output"
    end
end

set -l sync_args --extra dev
if test -f uv.lock
    set sync_args --locked $sync_args
end
uv sync $sync_args
or fail 'uv dependency synchronization failed.'
if test -f uv.lock
    uv lock --check
    or fail 'uv.lock does not match pyproject.toml.'
end
uv run ruff check .
or fail 'Ruff checks failed.'
uv run agegate-evidence \
    --config data/scenarios/quebec_bill9_v02.yaml \
    --evidence data/evidence.csv \
    --output "$__agegate_smoke_output/evidence_coverage.csv"
or fail 'Evidence validation failed.'
uv run pytest
or fail 'The automated test suite failed.'
uv run agegate-run \
    --config data/scenarios/quebec_bill9_v02.yaml \
    --evidence data/evidence.csv \
    --output "$__agegate_smoke_output" \
    --simulations 250 \
    --seed 20260722
or fail 'The reduced experiment failed.'
uv run python scripts/export_parameter_catalog.py \
    --config data/scenarios/quebec_bill9_v02.yaml \
    --evidence data/evidence.csv \
    --output "$__agegate_smoke_output/parameter_catalog.csv"
or fail 'Parameter-catalog export failed.'

for required_output in \
    "$__agegate_smoke_output/REPORT.md" \
    "$__agegate_smoke_output/dashboard.html" \
    "$__agegate_smoke_output/run_manifest.json" \
    "$__agegate_smoke_output/parameter_catalog.csv"
    test -s "$required_output"
    or fail "Expected smoke-test output is missing: $required_output"
end

printf '\nMomiji native fish smoke test passed.\n'
