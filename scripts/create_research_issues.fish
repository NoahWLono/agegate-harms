#!/usr/bin/env fish

set -l script_dir (cd (status dirname); and pwd -P)
or begin
    echo 'Could not resolve the scripts directory.' >&2
    exit 1
end
set -l project_dir (cd "$script_dir/.."; and pwd -P)
or begin
    echo 'Could not resolve the project directory.' >&2
    exit 1
end
cd -- "$project_dir"
or exit 1

type -q uv
or begin
    echo 'uv is required. On Momiji run: sudo pacman -S --needed uv' >&2
    exit 1
end

exec uv run python scripts/create_research_issues.py $argv
