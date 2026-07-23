from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

CANONICAL = "blank-at-eol,blank-at-eof,space-before-tab"


def run_git(repo: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize("hostile_policy", ["indent-with-non-tab", "tab-in-indent"])
def test_repo_local_whitespace_policy_overrides_hostile_global_config(
    tmp_path: Path, hostile_policy: str
) -> None:
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    home.mkdir()
    repo.mkdir()
    env = {
        **os.environ,
        "HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
    }

    assert run_git(repo, "init", "-q", env=env).returncode == 0
    assert run_git(repo, "config", "--global", "core.whitespace", hostile_policy, env=env).returncode == 0

    # The lockfile deliberately includes deeply space-indented package metadata.
    package_blocks = []
    for number in range(1, 25):
        package_blocks.append(
            "\n".join(
                [
                    "[[package]]",
                    f'name = "example-{number}"',
                    'version = "1.0.0"',
                    "dependencies = [",
                    '        { name = "dependency" },',
                    "]",
                ]
            )
        )
    (repo / "uv.lock").write_text("\n\n".join(package_blocks) + "\n", encoding="utf-8")
    (repo / "Makefile").write_text("test:\n\t@echo ok\n", encoding="utf-8")
    (repo / "scenario.yml").write_text("root:\n        child: value\n", encoding="utf-8")

    assert run_git(repo, "add", "--all", env=env).returncode == 0
    hostile = run_git(repo, "diff", "--cached", "--check", env=env)
    assert hostile.returncode != 0

    assert run_git(repo, "config", "--local", "core.whitespace", CANONICAL, env=env).returncode == 0
    canonical = run_git(repo, "diff", "--cached", "--check", env=env)
    assert canonical.returncode == 0, canonical.stdout + canonical.stderr


def test_release_scripts_pin_canonical_git_whitespace_policy() -> None:
    root = Path(__file__).parents[1]
    paths = [
        root / "run_experiment.fish",
        root / "run_experiment.sh",
        root / "scripts" / "release_preflight.fish",
        root / "scripts" / "release_preflight.sh",
        root / "packaging" / "install-on-momiji.fish",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert CANONICAL in text
