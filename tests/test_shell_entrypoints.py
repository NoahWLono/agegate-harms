from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]

NATIVE_FISH_ENTRYPOINTS = [
    ROOT / "run_experiment.fish",
    ROOT / "scripts" / "check_environment.fish",
    ROOT / "scripts" / "create_research_issues.fish",
    ROOT / "scripts" / "momiji_smoke_test.fish",
    ROOT / "scripts" / "release_preflight.fish",
]

FISH_INSTALLER = ROOT / "packaging" / "install-on-momiji.fish"
BASH_INSTALLER = ROOT / "packaging" / "install-on-momiji.sh"


def test_all_fish_entrypoints_have_fish_shebang_and_are_executable() -> None:
    paths = [*NATIVE_FISH_ENTRYPOINTS, FISH_INSTALLER]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("#!/usr/bin/env fish\n")
        assert path.stat().st_mode & 0o111


def test_experiment_installer_and_maintenance_entrypoints_are_native_fish() -> None:
    for path in [*NATIVE_FISH_ENTRYPOINTS, FISH_INSTALLER]:
        text = path.read_text(encoding="utf-8")
        assert "exec bash" not in text
        assert "status dirname" in text or path.name == "check_environment.fish"


def test_native_fish_workflow_contains_every_release_check() -> None:
    runner = (ROOT / "run_experiment.fish").read_text(encoding="utf-8")
    for command in (
        "argparse",
        "fish -n",
        "uv sync",
        "uv lock --check",
        "uv run agegate-evidence",
        "uv run pytest",
        "uv run ruff check .",
        "uv run agegate-run",
        "export_parameter_catalog.py",
    ):
        assert command in runner


def test_native_fish_installer_preserves_repo_and_runs_fish_workflow() -> None:
    fish_installer = FISH_INSTALLER.read_text(encoding="utf-8")
    for command in (
        "argparse",
        "cp -a --reflink=auto",
        'cp -a -- "$source_dir/." "$target/"',
        "for package_pair in git:git python:python uv:uv",
        'install_arch_package github-cli "$assume_yes"',
        "fish ./run_experiment.fish $run_args",
        "Never commits, pushes, tags, opens a pull request, or creates a release.",
    ):
        assert command in fish_installer


def test_bash_compatibility_installer_provisions_and_uses_fish() -> None:
    bash_installer = BASH_INSTALLER.read_text(encoding="utf-8")
    for command in (
        "fish:fish",
        'fish -n "$script"',
        'fish ./run_experiment.fish "${run_args[@]}"',
        "Nothing is committed, pushed, tagged, or released.",
    ):
        assert command in bash_installer


def test_all_bash_entrypoints_pass_bash_syntax_check() -> None:
    scripts = [
        ROOT / "run_experiment.sh",
        *sorted((ROOT / "scripts").glob("*.sh")),
        BASH_INSTALLER,
    ]
    for script in scripts:
        subprocess.run(["bash", "-n", str(script)], check=True)


def test_ci_exercises_arch_fish_and_complete_bundle_installer() -> None:
    workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(
        encoding="utf-8"
    )
    for expected in (
        "image: archlinux:latest",
        "pacman -Syu --noconfirm git fish python uv",
        "fish -n $fish_file",
        "cp packaging/install-on-momiji.fish",
        "cp packaging/install-on-momiji.sh",
        "fish run_experiment.fish --simulations 1000",
    ):
        assert expected in workflow

def test_native_fish_workflows_repair_moved_virtualenvs() -> None:
    for path in [ROOT / "run_experiment.fish", ROOT / "scripts" / "release_preflight.fish"]:
        text = path.read_text(encoding="utf-8")
        assert "function reset_stale_virtualenv" in text
        assert ".venv/bin/pytest" in text
        assert "Removing stale .venv left by a directory move" in text


def test_momiji_installer_removes_nonportable_virtualenv() -> None:
    text = FISH_INSTALLER.read_text(encoding="utf-8")
    assert 'rm -rf -- "$target/.venv"' in text
