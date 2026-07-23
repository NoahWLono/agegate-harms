#!/usr/bin/env python3
"""Validate the evidence registry and write parameter-level coverage."""

from __future__ import annotations

from pathlib import Path

from agegate_harms.evidence import (
    coverage_report,
    load_evidence,
    summarize_coverage,
    validate_evidence_registry,
)
from agegate_harms.model import load_config

CONFIG = Path("data/scenarios/quebec_bill9_v02.yaml")
EVIDENCE = Path("data/evidence.csv")
OUTPUT = Path("results/evidence_coverage.csv")


def main() -> None:
    config = load_config(CONFIG)
    evidence = load_evidence(EVIDENCE)
    errors = validate_evidence_registry(evidence)
    if errors:
        raise SystemExit("\n".join(errors))
    coverage = coverage_report(config, evidence)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(OUTPUT, index=False)
    print(summarize_coverage(coverage).to_string(index=False))
    missing = coverage[coverage["missing_evidence_ids"] != ""]
    if not missing.empty:
        raise SystemExit(missing[["parameter_key", "missing_evidence_ids"]].to_string(index=False))


if __name__ == "__main__":
    main()
