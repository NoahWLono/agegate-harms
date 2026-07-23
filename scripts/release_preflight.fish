#!/usr/bin/env fish

function fail --argument-names message
    printf 'Error: %s\n' "$message" >&2
    exit 1
end

function reset_stale_virtualenv
    if not test -d .venv
        return 0
    end

    set -l stale 0
    for launcher in .venv/bin/pytest .venv/bin/ruff .venv/bin/agegate-run .venv/bin/agegate-evidence
        test -f "$launcher"; or continue
        set -l first_line (head -n 1 "$launcher" 2>/dev/null)
        string match -q '#!*' -- "$first_line"; or continue
        set -l interpreter (string replace -r '^#!' '' -- "$first_line")
        if string match -q '/*' -- "$interpreter"; and not test -x "$interpreter"
            set stale 1
            break
        end
    end

    if test "$stale" -eq 1
        echo 'Removing stale .venv left by a directory move...'
        rm -rf -- .venv
        or fail 'Could not remove the stale virtual environment.'
    end
end

function usage
    printf '%s\n' \
        'Run v0.2 release checks natively from fish without publishing.' \
        '' \
        'Usage:' \
        '  fish scripts/release_preflight.fish [options]' \
        '' \
        'Options:' \
        '  -s, --simulations N   Reduced Monte Carlo draws. Default: 2000' \
        '      --keep-output     Preserve the temporary output directory' \
        '  -h, --help            Show this help'
end

argparse --name release_preflight \
    's/simulations=' \
    'keep-output' \
    'h/help' \
    -- $argv
or exit 2

if set -q _flag_help
    usage
    exit 0
end

if test (count $argv) -gt 0
    printf 'Unexpected positional argument: %s\n' "$argv[1]" >&2
    usage >&2
    exit 2
end

set -l simulations 2000
set -l keep_output 0
set -q _flag_simulations[1]; and set simulations $_flag_simulations[-1]
set -q _flag_keep_output; and set keep_output 1

string match -qr '^[1-9][0-9]*$' -- "$simulations"
or fail '--simulations must be a positive integer.'

set -l script_dir (cd (status dirname); and pwd -P)
or fail 'Could not resolve the scripts directory.'
set -l project_dir (cd "$script_dir/.."; and pwd -P)
or fail 'Could not resolve the project directory.'
cd -- "$project_dir"
or fail "Could not enter the project directory: $project_dir"

type -q git; or fail 'git is required.'
type -q uv; or fail 'uv is required.'
git rev-parse --is-inside-work-tree >/dev/null 2>&1
or fail 'This directory is not a Git repository.'

set -l canonical_git_whitespace blank-at-eol,blank-at-eof,space-before-tab
set -l inherited_git_whitespace (git config --show-origin --get core.whitespace 2>/dev/null)
git config --local core.whitespace "$canonical_git_whitespace"
or fail 'Could not set the repository-local Git whitespace policy.'
if test -n "$inherited_git_whitespace"
    echo "Previous effective Git whitespace policy: $inherited_git_whitespace"
end
echo "Repository Git whitespace policy: $canonical_git_whitespace"

grep -q '^version = "0.2.0"$' pyproject.toml
or fail 'pyproject.toml does not declare version 0.2.0.'
grep -q '^version: 0.2.0$' CITATION.cff
or fail 'CITATION.cff does not declare version 0.2.0.'
grep -q '^## 0.2.0 - 2026-07-22$' CHANGELOG.md
or fail 'CHANGELOG.md does not contain the expected v0.2.0 heading.'

set -g __agegate_preflight_output (mktemp -d -t agegate-v02-preflight.XXXXXX)
or fail 'Could not create a temporary output directory.'
set -g __agegate_preflight_keep $keep_output

function __agegate_preflight_cleanup --on-event fish_exit
    if test "$__agegate_preflight_keep" -eq 0; and test -n "$__agegate_preflight_output"; and test -d "$__agegate_preflight_output"
        rm -rf -- "$__agegate_preflight_output"
    end
end

printf '%s\n' \
    'AgeGate Harms v0.2 native fish release preflight' \
    "Repository: $project_dir" \
    "Temporary output: $__agegate_preflight_output" \
    "Simulation draws: $simulations"

echo 'Syntax-checking fish entry points...'
for fish_file in run_experiment.fish scripts/*.fish packaging/*.fish
    test -f "$fish_file"; or continue
    fish -n "$fish_file"
    or fail "Fish syntax check failed: $fish_file"
end

reset_stale_virtualenv

echo 'Repairing canonical LF line endings and trailing whitespace...'
python scripts/normalize_whitespace.py --write
or fail 'Could not normalize repository text files.'
python scripts/normalize_whitespace.py
or fail 'Repository text contains line-ending or trailing-whitespace defects.'

set -l sync_args --extra dev --extra ui
if test -f uv.lock
    set sync_args --locked $sync_args
end
uv sync $sync_args
or fail 'uv dependency synchronization failed.'

# uv may create uv.lock after the first source cleanup. Normalize it before Git checks.
python scripts/normalize_whitespace.py --write
or fail 'Could not normalize dependency-generated text files.'
python scripts/normalize_whitespace.py
or fail 'Dependency-generated text still contains whitespace defects.'
if test -f uv.lock
    uv lock --check
    or fail 'uv.lock does not match pyproject.toml.'
end
uv run agegate-evidence \
    --config data/scenarios/quebec_bill9_v02.yaml \
    --evidence data/evidence.csv \
    --output "$__agegate_preflight_output/evidence_coverage.csv"
or fail 'Evidence validation failed.'
uv run pytest
or fail 'The automated test suite failed.'
uv run ruff check .
or fail 'Ruff checks failed.'
uv run agegate-run \
    --config data/scenarios/quebec_bill9_v02.yaml \
    --evidence data/evidence.csv \
    --output "$__agegate_preflight_output" \
    --simulations "$simulations" \
    --seed 20260722
or fail 'The reduced reproducibility experiment failed.'
uv run python scripts/export_parameter_catalog.py \
    --config data/scenarios/quebec_bill9_v02.yaml \
    --evidence data/evidence.csv \
    --output "$__agegate_preflight_output/parameter_catalog.csv"
or fail 'Parameter-catalog export failed.'
git -c core.whitespace="$canonical_git_whitespace" diff --check
or fail 'The unstaged diff contains canonical Git whitespace errors.'
git -c core.whitespace="$canonical_git_whitespace" diff --cached --check
or fail 'The staged diff contains canonical Git whitespace errors.'

for required_output in \
    "$__agegate_preflight_output/REPORT.md" \
    "$__agegate_preflight_output/dashboard.html" \
    "$__agegate_preflight_output/run_manifest.json" \
    "$__agegate_preflight_output/parameter_catalog.csv"
    test -s "$required_output"
    or fail "Expected output is missing or empty: $required_output"
end

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
git remote -v; or true

echo
if test $keep_output -eq 1
    echo "Preflight passed. Temporary results: $__agegate_preflight_output"
else
    echo 'Preflight passed. Temporary results will be removed.'
end
echo 'No commit, push, tag, pull request, or release was created.'
