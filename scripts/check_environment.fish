#!/usr/bin/env fish

if test (count $argv) -gt 0
    echo 'Usage: fish scripts/check_environment.fish' >&2
    exit 2
end

set -l missing 0

printf 'OS: '
if test -f /etc/arch-release
    echo 'Arch Linux detected'
else
    echo 'not Arch Linux; automatic pacman installation is unavailable'
end

for command_name in fish python git uv
    printf '%s: ' "$command_name"
    if type -q "$command_name"
        switch "$command_name"
            case fish
                fish --version
            case python
                python --version
            case git
                git --version
            case uv
                uv --version
        end
    else
        echo 'missing'
        set missing 1
    end
end

if type -q python
    python -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'
    if test $status -ne 0
        echo 'python: AgeGate Harms requires Python 3.11 or newer' >&2
        set missing 1
    end
end

printf 'gh: '
if type -q gh
    gh --version | head -n 1
else
    echo 'missing; required only for GitHub publishing and issue creation'
end

printf 'bash: '
if type -q bash
    bash --version | head -n 1
else
    echo 'missing; optional legacy runner only'
end

exit $missing
