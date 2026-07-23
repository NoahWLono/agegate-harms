"""Command-line entry point for AgeGate Harms v0.2."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .evidence import coverage_report, load_evidence, validate_evidence_registry
from .manifest import build_manifest, write_manifest
from .model import (
    deterministic_comparison,
    load_config,
    run_monte_carlo,
    sensitivity_analysis,
    summarize_simulations,
)
from .priorities import build_evidence_priorities
from .reporting import (
    create_priority_chart,
    create_privacy_chart,
    create_substitution_chart,
    create_tradeoff_chart,
    write_html_dashboard,
    write_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the transparent AgeGate Harms v0.2 scenario experiment."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("data/scenarios/quebec_bill9_v02.yaml"),
        help="Path to scenario YAML.",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("data/evidence.csv"),
        help="Path to evidence registry CSV.",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("results"), help="Output directory."
    )
    parser.add_argument("--simulations", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument(
        "--save-raw", action="store_true", help="Save every simulation draw as gzip CSV."
    )
    parser.add_argument(
        "--strict-evidence",
        action="store_true",
        help="Fail when any modeled parameter lacks direct empirical evidence.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate configuration and evidence mappings without running simulations.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    config = load_config(args.config)
    evidence = load_evidence(args.evidence)
    evidence_errors = validate_evidence_registry(evidence)
    if evidence_errors:
        raise SystemExit("Evidence registry validation failed:\n" + "\n".join(evidence_errors))
    coverage = coverage_report(config, evidence)
    missing = coverage.loc[coverage["missing_evidence_ids"] != ""]
    if not missing.empty:
        raise SystemExit(
            "Configuration references missing evidence identifiers:\n"
            + missing[["parameter_key", "missing_evidence_ids"]].to_string(index=False)
        )
    coverage.to_csv(args.output / "evidence_coverage.csv", index=False)

    if args.strict_evidence:
        gaps = coverage.loc[coverage["coverage_class"] != "direct_empirical"]
        if not gaps.empty:
            raise SystemExit(
                f"Strict evidence check failed: {len(gaps)} modeled parameters do not have direct empirical evidence."
            )
    if args.validate_only:
        print(f"Validated {len(coverage)} modeled parameters and {len(evidence)} evidence records.")
        return

    deterministic = deterministic_comparison(config)
    simulations = run_monte_carlo(config, args.simulations, args.seed)
    summary = summarize_simulations(simulations)
    sensitivity = sensitivity_analysis(simulations)
    priorities = build_evidence_priorities(sensitivity, coverage)

    output_files = [
        args.output / "deterministic_results.csv",
        args.output / "monte_carlo_summary.csv",
        args.output / "sensitivity.csv",
        args.output / "evidence_coverage.csv",
        args.output / "evidence_priorities.csv",
        args.output / "REPORT.md",
        args.output / "tradeoff.png",
        args.output / "privacy_footprint.png",
        args.output / "substitution.png",
        args.output / "evidence_priorities.png",
        args.output / "dashboard.html",
    ]
    deterministic.to_csv(output_files[0], index=False)
    summary.to_csv(output_files[1], index=False)
    sensitivity.to_csv(output_files[2], index=False)
    priorities.to_csv(output_files[4], index=False)

    if args.save_raw:
        raw = pd.concat(simulations.values(), ignore_index=True)
        raw_path = args.output / "monte_carlo_raw.csv.gz"
        raw.to_csv(raw_path, index=False, compression="gzip")
        output_files.append(raw_path)

    write_report(
        config,
        deterministic,
        summary,
        sensitivity,
        coverage,
        priorities,
        output_files[5],
        simulations=args.simulations,
        seed=args.seed,
    )
    create_tradeoff_chart(summary, output_files[6])
    create_privacy_chart(summary, output_files[7])
    create_substitution_chart(summary, output_files[8])
    create_priority_chart(priorities, output_files[9])
    write_html_dashboard(
        config,
        summary,
        coverage,
        priorities,
        {
            "Access trade-off": output_files[6],
            "Identity-data footprint": output_files[7],
            "Transaction versus consumption prevention": output_files[8],
            "Evidence priorities": output_files[9],
        },
        output_files[10],
        simulations=args.simulations,
        seed=args.seed,
    )

    manifest_path = args.output / "run_manifest.json"
    manifest = build_manifest(
        config_path=args.config,
        evidence_path=args.evidence,
        simulations=args.simulations,
        seed=args.seed,
        output_files=output_files,
    )
    write_manifest(manifest, manifest_path)

    print(f"Wrote results to {args.output.resolve()}")
    print(
        deterministic[
            [
                "method",
                "minor_purchases_prevented",
                "minor_consumption_prevented",
                "adult_adverse_outcomes",
                "centralized_records_at_risk",
                "total_annual_cost",
            ]
        ].to_string(index=False)
    )
    print("\nEvidence coverage:")
    print(coverage["coverage_class"].value_counts().to_string())


if __name__ == "__main__":
    main()
