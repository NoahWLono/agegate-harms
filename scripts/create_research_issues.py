#!/usr/bin/env python3
"""Create the prepared research backlog in GitHub using the gh CLI."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

LABEL_COLORS = {
    "evidence": "1D76DB",
    "methodology": "5319E7",
    "model": "0052CC",
    "legal": "B60205",
    "accessibility": "0E8A16",
    "privacy": "D93F0B",
    "economics": "FBCA04",
    "distributional": "C2E0C6",
    "documentation": "0075CA",
}


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        ["gh", *args],
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout if capture else ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path("research/issues.csv"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run:
        run("auth", "status")
        existing_json = run(
            "issue", "list", "--state", "all", "--limit", "1000", "--json", "title", capture=True
        )
        existing = {item["title"] for item in json.loads(existing_json)}
    else:
        existing = set()

    with args.file.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    for label in sorted({row["label"] for row in rows}):
        if args.dry_run:
            print(f"LABEL   {label}")
        else:
            run(
                "label",
                "create",
                label,
                "--force",
                "--color",
                LABEL_COLORS.get(label, "EDEDED"),
                "--description",
                f"AgeGate Harms research: {label}",
            )

    for row in rows:
        title = row["title"]
        body = Path(row["body_file"]).read_text(encoding="utf-8")
        body = f"**Priority:** {row['priority']}\n\n{body}"
        if title in existing:
            print(f"SKIP    {title}")
            continue
        if args.dry_run:
            print(f"CREATE  [{row['label']}] {title}")
        else:
            run("issue", "create", "--title", title, "--label", row["label"], "--body", body)
            print(f"CREATED {title}")


if __name__ == "__main__":
    main()
