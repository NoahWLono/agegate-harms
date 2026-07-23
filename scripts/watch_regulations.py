#!/usr/bin/env python3
"""Watch authoritative regulatory sources for byte-level changes.

This script does not interpret law. It retrieves listed sources, computes
SHA-256 hashes, and tells the researcher which sources need manual review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_SOURCES = Path("data/regulatory_sources.csv")
DEFAULT_STATE = Path("research/legal/regulatory_state.json")
USER_AGENT = "AgeGate-Harms-Regulatory-Watcher/0.2 (+research source monitoring)"


def fetch(url: str, timeout: float) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310, URLs come from a reviewed local CSV
        return response.read()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_sources(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"source_id", "title", "url", "source_role"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"{path} must contain columns {sorted(required)}")
    return rows


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"sources": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--initialize",
        action="store_true",
        help="Create or replace the baseline without reporting every source as changed.",
    )
    parser.add_argument(
        "--save-snapshots",
        action="store_true",
        help="Save retrieved bytes under research/legal/snapshots for manual review.",
    )
    args = parser.parse_args()

    sources = load_sources(args.sources)
    previous = load_state(args.state)
    current = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {},
    }
    changed: list[str] = []
    failed: list[str] = []
    snapshot_dir = Path("research/legal/snapshots")
    if args.save_snapshots:
        snapshot_dir.mkdir(parents=True, exist_ok=True)

    for source in sources:
        source_id = source["source_id"]
        try:
            body = fetch(source["url"], args.timeout)
            sha = digest(body)
            record = {
                **source,
                "sha256": sha,
                "bytes": len(body),
                "checked_at_utc": current["checked_at_utc"],
            }
            old_sha = previous.get("sources", {}).get(source_id, {}).get("sha256")
            if old_sha and old_sha != sha:
                changed.append(source_id)
            current["sources"][source_id] = record
            if args.save_snapshots:
                suffix = ".pdf" if body.startswith(b"%PDF") else ".html"
                (snapshot_dir / f"{source_id}{suffix}").write_bytes(body)
            print(f"OK      {source_id:24} {sha[:12]}  {len(body):,} bytes")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            failed.append(source_id)
            current["sources"][source_id] = {**source, "error": str(exc)}
            print(f"ERROR   {source_id:24} {exc}", file=sys.stderr)

    args.state.parent.mkdir(parents=True, exist_ok=True)
    args.state.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.initialize or not previous.get("sources"):
        print(f"\nInitialized regulatory baseline at {args.state}.")
    elif changed:
        print("\nManual legal review required for changed sources:")
        for source_id in changed:
            print(f"  - {source_id}")
    else:
        print("\nNo byte-level source changes detected.")

    if failed:
        print("\nSome sources could not be checked. Do not treat this run as a complete update.", file=sys.stderr)
        raise SystemExit(2)
    if changed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
