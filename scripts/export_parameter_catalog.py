#!/usr/bin/env python3
"""Export a reviewer-friendly catalog of parameters and evidence coverage."""

from __future__ import annotations

import argparse
from pathlib import Path

from agegate_harms.evidence import coverage_report, load_evidence
from agegate_harms.model import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("data/scenarios/quebec_bill9_v02.yaml"),
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("data/evidence.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/parameter_catalog.csv"),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    evidence = load_evidence(args.evidence)
    coverage = coverage_report(config, evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    coverage.sort_values(["scope", "method_id", "parameter"]).to_csv(
        args.output, index=False
    )
    print(f"Wrote {len(coverage)} parameters to {args.output}")


if __name__ == "__main__":
    main()
