"""Reproducible run-manifest helpers."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def build_manifest(
    *,
    config_path: str | Path,
    evidence_path: str | Path,
    simulations: int,
    seed: int,
    output_files: list[str | Path],
) -> dict[str, Any]:
    return {
        "project": "AgeGate Harms",
        "project_version": "0.2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "simulations": simulations,
        "seed": seed,
        "config": {
            "path": str(config_path),
            "sha256": sha256_file(config_path),
        },
        "evidence_registry": {
            "path": str(evidence_path),
            "sha256": sha256_file(evidence_path),
        },
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": _package_version("numpy"),
            "pandas": _package_version("pandas"),
            "matplotlib": _package_version("matplotlib"),
            "pyyaml": _package_version("pyyaml"),
        },
        "outputs": [
            {"path": str(path), "sha256": sha256_file(path)}
            for path in output_files
            if Path(path).is_file()
        ],
    }


def write_manifest(manifest: dict[str, Any], destination: str | Path) -> None:
    Path(destination).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
