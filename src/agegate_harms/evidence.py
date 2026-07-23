"""Evidence registry validation and coverage analysis."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from .model import iter_numeric_parameters, load_config

REQUIRED_COLUMNS = [
    "evidence_id",
    "parameter",
    "method",
    "relationship",
    "estimate_low",
    "estimate_central",
    "estimate_high",
    "unit",
    "source_title",
    "source_url",
    "source_type",
    "jurisdiction",
    "population",
    "measurement_start",
    "measurement_end",
    "retrieved_on",
    "independence",
    "status",
    "confidence",
    "transferability",
    "limitations",
    "notes",
]

ALLOWED_RELATIONSHIPS = {"direct", "contextual", "legal", "guidance", "assumption", "gap"}
ALLOWED_STATUSES = {
    "empirical",
    "legal_fact",
    "official_guidance",
    "derived",
    "analyst_assumption",
    "research_gap",
}
ALLOWED_CONFIDENCE = {"high", "moderate", "low", "illustrative", "not_applicable"}
ALLOWED_TRANSFERABILITY = {"high", "moderate", "low", "not_applicable"}


def load_evidence(path: str | Path) -> pd.DataFrame:
    """Load evidence CSV as strings while preserving blank values."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def validate_evidence_registry(frame: pd.DataFrame) -> list[str]:
    """Return validation errors. An empty list means the registry is valid."""
    errors: list[str] = []
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        return [f"Evidence registry is missing columns: {missing}"]

    blank_ids = frame.index[frame["evidence_id"].str.strip() == ""].tolist()
    if blank_ids:
        errors.append(f"Blank evidence_id values at rows: {blank_ids[:10]}")
    duplicates = frame.loc[frame["evidence_id"].duplicated(), "evidence_id"].tolist()
    if duplicates:
        errors.append(f"Duplicate evidence_id values: {sorted(set(duplicates))}")

    for row_index, row in frame.iterrows():
        relationship = row["relationship"].strip()
        status = row["status"].strip()
        confidence = row["confidence"].strip()
        transferability = row["transferability"].strip()
        evidence_id = row["evidence_id"].strip() or f"row {row_index}"
        if relationship not in ALLOWED_RELATIONSHIPS:
            errors.append(f"{evidence_id}: invalid relationship '{relationship}'")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{evidence_id}: invalid status '{status}'")
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"{evidence_id}: invalid confidence '{confidence}'")
        if transferability not in ALLOWED_TRANSFERABILITY:
            errors.append(f"{evidence_id}: invalid transferability '{transferability}'")
        if status in {"empirical", "legal_fact", "official_guidance"} and not row[
            "source_url"
        ].strip():
            errors.append(f"{evidence_id}: sourced evidence requires source_url")

        numeric_values: list[float] = []
        for column in ["estimate_low", "estimate_central", "estimate_high"]:
            raw = row[column].strip()
            if raw:
                try:
                    numeric_values.append(float(raw))
                except ValueError:
                    errors.append(f"{evidence_id}: {column} is not numeric: '{raw}'")
        if len(numeric_values) == 3 and not (
            numeric_values[0] <= numeric_values[1] <= numeric_values[2]
        ):
            errors.append(f"{evidence_id}: expected low <= central <= high")
    return errors


def _coverage_class(rows: pd.DataFrame) -> str:
    if rows.empty:
        return "unmapped"
    direct = rows[(rows["relationship"] == "direct") & (rows["status"] == "empirical")]
    if not direct.empty:
        return "direct_empirical"
    if (rows["relationship"] == "legal").any():
        return "legal_fact"
    if (rows["relationship"] == "guidance").any():
        return "official_guidance"
    if rows["relationship"].isin(["contextual"]).any():
        return "context_only"
    if rows["relationship"].isin(["gap"]).any():
        return "explicit_gap"
    if rows["relationship"].isin(["assumption"]).any():
        return "assumption_only"
    return "unmapped"


def coverage_report(config: Mapping[str, Any], evidence: pd.DataFrame) -> pd.DataFrame:
    """Map every model input to its registered evidence and classify coverage."""
    by_id = evidence.set_index("evidence_id", drop=False)
    output: list[dict[str, Any]] = []
    for parameter in iter_numeric_parameters(config):
        evidence_ids = parameter["evidence_ids"]
        missing_ids = [identifier for identifier in evidence_ids if identifier not in by_id.index]
        matched = evidence[evidence["evidence_id"].isin(evidence_ids)].copy()
        coverage_class = _coverage_class(matched)
        output.append(
            {
                **{key: value for key, value in parameter.items() if key != "evidence_ids"},
                "evidence_ids": ";".join(evidence_ids),
                "evidence_count": len(matched),
                "missing_evidence_ids": ";".join(missing_ids),
                "coverage_class": coverage_class,
                "direct_empirical_count": int(
                    (
                        (matched["relationship"] == "direct")
                        & (matched["status"] == "empirical")
                    ).sum()
                )
                if not matched.empty
                else 0,
                "contextual_count": int((matched["relationship"] == "contextual").sum())
                if not matched.empty
                else 0,
                "assumption_count": int((matched["relationship"] == "assumption").sum())
                if not matched.empty
                else 0,
                "gap_count": int((matched["relationship"] == "gap").sum())
                if not matched.empty
                else 0,
                "needs_research": coverage_class != "direct_empirical",
            }
        )
    return pd.DataFrame(output)


def summarize_coverage(coverage: pd.DataFrame) -> pd.DataFrame:
    """Count model parameters by evidence coverage class."""
    return (
        coverage.groupby("coverage_class", as_index=False)
        .agg(parameters=("parameter_key", "count"))
        .sort_values("parameters", ascending=False)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the AgeGate Harms evidence registry.")
    parser.add_argument("--config", type=Path, default=Path("data/scenarios/quebec_bill9_v02.yaml"))
    parser.add_argument("--evidence", type=Path, default=Path("data/evidence.csv"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    config = load_config(args.config)
    evidence = load_evidence(args.evidence)
    errors = validate_evidence_registry(evidence)
    if errors:
        raise SystemExit("\n".join(errors))
    coverage = coverage_report(config, evidence)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        coverage.to_csv(args.output, index=False)
    print(summarize_coverage(coverage).to_string(index=False))
    missing = coverage.loc[coverage["missing_evidence_ids"] != ""]
    if not missing.empty:
        raise SystemExit("Some configuration evidence identifiers are missing from the registry.")


if __name__ == "__main__":
    main()
