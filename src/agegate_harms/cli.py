"""Command-line entry point for the AgeGate Harms experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .model import (
    deterministic_comparison,
    load_config,
    run_monte_carlo,
    sensitivity_analysis,
    summarize_simulations,
)
from .reporting import (
    create_privacy_chart,
    create_tradeoff_chart,
    write_html_dashboard,
    write_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the transparent AgeGate Harms scenario experiment."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("data/assumptions.yaml"),
        help="Path to assumptions YAML.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Output directory.",
    )
    parser.add_argument("--simulations", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument(
        "--save-raw",
        action="store_true",
        help="Save every simulation draw. This creates a large CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    config = load_config(args.config)
    deterministic = deterministic_comparison(config)
    simulations = run_monte_carlo(config, args.simulations, args.seed)
    summary = summarize_simulations(simulations)
    sensitivity = sensitivity_analysis(simulations)

    deterministic.to_csv(args.output / "deterministic_results.csv", index=False)
    summary.to_csv(args.output / "monte_carlo_summary.csv", index=False)
    sensitivity.to_csv(args.output / "sensitivity.csv", index=False)

    if args.save_raw:
        raw = pd.concat(simulations.values(), ignore_index=True)
        raw.to_csv(args.output / "monte_carlo_raw.csv.gz", index=False, compression="gzip")

    write_report(
        config,
        deterministic,
        summary,
        sensitivity,
        args.output / "REPORT.md",
        simulations=args.simulations,
        seed=args.seed,
    )
    create_tradeoff_chart(summary, args.output / "tradeoff.png")
    create_privacy_chart(summary, args.output / "privacy_footprint.png")
    write_html_dashboard(
        config,
        summary,
        args.output / "tradeoff.png",
        args.output / "privacy_footprint.png",
        args.output / "dashboard.html",
        simulations=args.simulations,
        seed=args.seed,
    )

    print(f"Wrote results to {args.output.resolve()}")
    print(deterministic[[
        "method",
        "minor_purchases_prevented",
        "adult_adverse_outcomes",
        "identity_records_created",
        "total_annual_cost",
    ]].to_string(index=False))


if __name__ == "__main__":
    main()
