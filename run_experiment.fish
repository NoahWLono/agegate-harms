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
        'Run the complete AgeGate Harms v0.2 workflow natively from fish.' \
        '' \
        'Usage:' \
        '  fish run_experiment.fish [options]' \
        '  ./run_experiment.fish [options]' \
        '' \
        'Options:' \
        '  -s, --simulations N   Monte Carlo draws. Default: 50000' \
        '      --seed N          Random seed. Default: 20260722' \
        '  -c, --config PATH     Scenario YAML' \
        '  -e, --evidence PATH   Evidence registry CSV' \
        '  -o, --output PATH     Output directory. Default: results' \
        '      --skip-ui         Do not sync the optional Streamlit dependency' \
        '  -h, --help            Show this help' \
        '' \
        'SIMULATIONS, SEED, CONFIG, EVIDENCE, and OUTPUT may also be set as' \
        'environment variables. Explicit options take precedence.'
end

argparse --name run_experiment \
    's/simulations=' \
    'seed=' \
    'c/config=' \
    'e/evidence=' \
    'o/output=' \
    'skip-ui' \
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

set -l script_dir (cd (status dirname); and pwd -P)
or fail 'Could not resolve the project directory.'
cd -- "$script_dir"
or fail "Could not enter the project directory: $script_dir"

set -l simulations 50000
set -l seed 20260722
set -l config data/scenarios/quebec_bill9_v02.yaml
set -l evidence data/evidence.csv
set -l output results
set -l with_ui 1

set -q SIMULATIONS; and set simulations "$SIMULATIONS"
set -q SEED; and set seed "$SEED"
set -q CONFIG; and set config "$CONFIG"
set -q EVIDENCE; and set evidence "$EVIDENCE"
set -q OUTPUT; and set output "$OUTPUT"

set -q _flag_simulations[1]; and set simulations $_flag_simulations[-1]
set -q _flag_seed[1]; and set seed $_flag_seed[-1]
set -q _flag_config[1]; and set config $_flag_config[-1]
set -q _flag_evidence[1]; and set evidence $_flag_evidence[-1]
set -q _flag_output[1]; and set output $_flag_output[-1]
set -q _flag_skip_ui; and set with_ui 0

string match -qr '^[1-9][0-9]*$' -- "$simulations"
or fail '--simulations must be a positive integer.'
string match -qr '^[0-9]+$' -- "$seed"
or fail '--seed must be a nonnegative integer.'

type -q uv
or fail 'uv is missing. On Momiji run: sudo pacman -S --needed uv'
test -f "$config"
or fail "Configuration not found: $config"
test -f "$evidence"
or fail "Evidence registry not found: $evidence"

set -l canonical_git_whitespace blank-at-eol,blank-at-eof,space-before-tab
if type -q git; and git rev-parse --is-inside-work-tree >/dev/null 2>&1
    git config --local core.whitespace "$canonical_git_whitespace"
    or fail 'Could not set the repository-local Git whitespace policy.'
end

mkdir -p -- "$output"
or fail "Could not create output directory: $output"

reset_stale_virtualenv

set -l sync_args --extra dev
if test $with_ui -eq 1
    set -a sync_args --extra ui
end
if test -f uv.lock
    set sync_args --locked $sync_args
end

printf '%s\n' \
    'AgeGate Harms v0.2 native fish workflow' \
    "Project: $script_dir" \
    "Config: $config" \
    "Evidence: $evidence" \
    "Output: $output" \
    "Simulations: $simulations" \
    "Seed: $seed"

echo '1/7 Syntax-checking fish entry points...'
for fish_file in run_experiment.fish scripts/*.fish packaging/*.fish
    test -f "$fish_file"; or continue
    fish -n "$fish_file"
    or fail "Fish syntax check failed: $fish_file"
end

echo '2/7 Synchronizing dependencies...'
uv sync $sync_args
or fail 'uv dependency synchronization failed.'

# The first sync can create uv.lock. Normalize it and every UTF-8 project file now.
python scripts/normalize_whitespace.py --write
or fail 'Could not normalize dependency-generated text files.'
python scripts/normalize_whitespace.py
or fail 'Repository text contains whitespace defects after dependency synchronization.'
if test -f uv.lock
    uv lock --check
    or fail 'uv.lock does not match pyproject.toml.'
end

echo '3/7 Validating evidence mappings...'
uv run agegate-evidence \
    --config "$config" \
    --evidence "$evidence" \
    --output "$output/evidence_coverage.csv"
or fail 'Evidence validation failed.'

echo '4/7 Running automated tests...'
uv run pytest -v
or fail 'The automated test suite failed.'

echo '5/7 Running Ruff checks...'
uv run ruff check .
or fail 'Ruff checks failed.'

echo '6/7 Running the Monte Carlo experiment and report build...'
uv run agegate-run \
    --config "$config" \
    --evidence "$evidence" \
    --output "$output" \
    --simulations "$simulations" \
    --seed "$seed"
or fail 'The experiment failed.'

echo '7/7 Exporting the parameter catalog...'
uv run python scripts/export_parameter_catalog.py \
    --config "$config" \
    --evidence "$evidence" \
    --output "$output/parameter_catalog.csv"
or fail 'Parameter-catalog export failed.'

set -l output_display "$output"
if not string match -q '/*' -- "$output"
    set output_display "$script_dir/$output"
end

printf '\n%s\n' \
    'Complete.' \
    "Report: $output_display/REPORT.md" \
    "Dashboard: $output_display/dashboard.html" \
    'Interactive UI: uv run streamlit run app.py'
