#!/usr/bin/env fish

# Native Fish installer for the Momiji release bundle.
# Never commits, pushes, tags, opens a pull request, or creates a release.

function fail --argument-names message
    printf 'Error: %s\n' "$message" >&2
    exit 1
end

function usage
    printf '%s\n' \
        'Install the AgeGate Harms v0.2.0 local release on Momiji.' \
        '' \
        'Usage:' \
        '  fish install-on-momiji.fish [options]' \
        '  ./install-on-momiji.fish [options]' \
        '' \
        'Options:' \
        '      --target PATH       Install target. Default: ~/Projects/agegate-harms' \
        '      --simulations N     Monte Carlo draws. Default: 50000' \
        '      --seed N            Random seed. Default: 20260722' \
        '      --skip-ui           Do not install the optional Streamlit interface' \
        '      --with-gh           Install GitHub CLI when it is missing' \
        '      --skip-build        Copy and back up files only' \
        '      --open-dashboard    Open the dashboard after a successful run' \
        '  -y, --yes               Do not ask for confirmation' \
        '  -h, --help              Show this help' \
        '' \
        'Safety behavior:' \
        '  * Moves ~/Downloads/agegate-harms to the target when appropriate.' \
        '  * Makes a timestamped backup of an existing target.' \
        '  * Preserves an existing .git directory.' \
        '  * Never publishes anything to GitHub.'
end

argparse --name install-on-momiji \
    'target=' \
    'simulations=' \
    'seed=' \
    'skip-ui' \
    'with-gh' \
    'skip-build' \
    'open-dashboard' \
    'y/yes' \
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

set -l version 0.2.0
set -l script_dir (cd (status dirname); and pwd -P)
or fail 'Could not resolve the bundle directory.'
set -l source_dir "$script_dir/project"
set -l target "$HOME/Projects/agegate-harms"
set -l downloads_repo "$HOME/Downloads/agegate-harms"
set -l simulations 50000
set -l seed 20260722
set -l with_ui 1
set -l with_gh 0
set -l skip_build 0
set -l open_dashboard 0
set -l assume_yes 0

set -q _flag_target[1]; and set target $_flag_target[-1]
set -q _flag_simulations[1]; and set simulations $_flag_simulations[-1]
set -q _flag_seed[1]; and set seed $_flag_seed[-1]
set -q _flag_skip_ui; and set with_ui 0
set -q _flag_with_gh; and set with_gh 1
set -q _flag_skip_build; and set skip_build 1
set -q _flag_open_dashboard; and set open_dashboard 1
set -q _flag_yes; and set assume_yes 1

if string match -qr '^~(/|$)' -- "$target"
    set target (string replace -r -- '^~' "$HOME" "$target")
end

string match -qr '^[1-9][0-9]*$' -- "$simulations"
or fail '--simulations must be a positive integer.'
string match -qr '^[0-9]+$' -- "$seed"
or fail '--seed must be a nonnegative integer.'
test -d "$source_dir"; and test -f "$source_dir/pyproject.toml"
or fail "Bundle project directory is missing or incomplete: $source_dir"

printf '%s\n' \
    "AgeGate Harms v$version local installation" \
    '' \
    "Source: $source_dir" \
    "Target: $target" \
    "Existing Downloads repository: $downloads_repo" \
    "Simulations: $simulations" \
    "Seed: $seed"

if test $assume_yes -eq 0
    read -P 'Continue with backup and installation? [y/N] ' answer
    switch (string lower -- "$answer")
        case y yes
        case '*'
            echo 'Cancelled.'
            exit 0
    end
end

set -l target_parent (dirname -- "$target")
mkdir -p -- "$target_parent"
or fail "Could not create target parent directory: $target_parent"

if not test -e "$target"; and test -d "$downloads_repo"
    echo 'Moving existing repository from Downloads to Projects...'
    mv -- "$downloads_repo" "$target"
    or fail 'Could not move the existing Downloads repository.'
end

if test -e "$target"; and not test -d "$target"
    fail "Target exists but is not a directory: $target"
end

set -l backup ''
if test -d "$target"
    set -l timestamp (date +%Y%m%d-%H%M%S)
    set backup "$target.backup-$timestamp"
    set -l suffix 0
    while test -e "$backup"
        set suffix (math "$suffix + 1")
        set backup "$target.backup-$timestamp-$suffix"
    end
    echo "Creating safety backup: $backup"
    cp -a --reflink=auto -- "$target" "$backup"
    or fail 'Could not create the safety backup.'
end

mkdir -p -- "$target"
or fail "Could not create target: $target"
echo 'Applying the v0.2.0 file overlay...'
cp -a -- "$source_dir/." "$target/"
or fail 'Could not apply the project overlay.'

echo 'Removing non-portable virtual environments and caches...'
rm -rf -- "$target/.venv" "$target/.pytest_cache" "$target/.ruff_cache"
find "$target" -type d -name __pycache__ -prune -exec rm -rf -- '{}' + 2>/dev/null; or true
find "$target" -type f -name '*.pyc' -delete 2>/dev/null; or true
find "$target" -type f -name '*.pyo' -delete 2>/dev/null; or true

if test -d "$target/.git"
    echo "Preserved Git metadata: $target/.git"
else
    echo 'No existing .git directory was found. The project is still runnable locally.'
end

if test $skip_build -eq 1
    echo
    echo 'Copy-only installation completed.'
    test -n "$backup"; and echo "Backup: $backup"
    echo "Target: $target"
    exit 0
end

function install_arch_package --argument-names package assume_yes
    if not test -f /etc/arch-release; or not type -q pacman
        fail "Automatic package installation is for Arch Linux. Install '$package' manually, then rerun."
    end

    set -l pacman_args -S --needed
    if test "$assume_yes" -eq 1
        set -a pacman_args --noconfirm
    end

    if test (id -u) -eq 0
        command pacman $pacman_args "$package"
        or fail "Could not install '$package'."
    else if type -q sudo
        command sudo pacman $pacman_args "$package"
        or fail "Could not install '$package'."
    else
        fail "sudo is unavailable. Install '$package' as root, then rerun."
    end
end

for package_pair in git:git python:python uv:uv
    set -l pair (string split -m 1 -- ':' "$package_pair")
    set -l command_name $pair[1]
    set -l package_name $pair[2]
    if not type -q "$command_name"
        echo "Installing $package_name from the official Arch repository..."
        install_arch_package "$package_name" "$assume_yes"
    end
end

if test $with_gh -eq 1; and not type -q gh
    echo 'Installing GitHub CLI from the official Arch repository...'
    install_arch_package github-cli "$assume_yes"
end

cd -- "$target"
or fail "Could not enter the installed project: $target"

set -l canonical_git_whitespace blank-at-eol,blank-at-eof,space-before-tab
if git rev-parse --is-inside-work-tree >/dev/null 2>&1
    git config --local core.whitespace "$canonical_git_whitespace"
    or fail 'Could not set the repository-local Git whitespace policy.'
end

echo 'Normalizing repository text files...'
python scripts/normalize_whitespace.py --write
or fail 'Could not normalize repository text files.'
python scripts/normalize_whitespace.py
or fail 'Repository text still contains whitespace defects.'

echo 'Checking Fish entry-point syntax...'
for fish_file in run_experiment.fish scripts/*.fish packaging/*.fish
    test -f "$fish_file"; or continue
    fish -n "$fish_file"
    or fail "Fish syntax check failed: $fish_file"
end

set -l run_args --simulations "$simulations" --seed "$seed"
if test $with_ui -eq 0
    set -a run_args --skip-ui
end

echo 'Running the complete native Fish workflow...'
fish ./run_experiment.fish $run_args
or fail 'The complete experiment workflow failed.'

echo
if git rev-parse --is-inside-work-tree >/dev/null 2>&1
    echo 'Local Git status after installation:'
    git status --short
    echo
end

echo 'Installation and local run completed.'
test -n "$backup"; and echo "Backup: $backup"
echo "Project: $target"
echo "Report: $target/results/REPORT.md"
echo "Dashboard: $target/results/dashboard.html"
echo "Streamlit: cd '$target'; and uv run streamlit run app.py"
echo "Publishing guide: $target/PUBLISHING.md"

if test $with_gh -eq 1
    printf '%s\n' \
        'Research issues: authenticate, review the dry run, then run:' \
        "  cd '$target'" \
        '  uv run python scripts/create_research_issues.py --dry-run' \
        '  fish scripts/create_research_issues.fish'
end

if test $open_dashboard -eq 1
    set -l graphical_session 0
    set -q DISPLAY; and set graphical_session 1
    set -q WAYLAND_DISPLAY; and set graphical_session 1
    if type -q xdg-open; and test $graphical_session -eq 1
        command xdg-open "$target/results/dashboard.html" >/dev/null 2>&1 &
    else
        echo 'Could not open the dashboard automatically. Open it from the path above.'
    end
end
