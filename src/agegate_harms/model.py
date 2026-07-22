"""Core deterministic and Monte Carlo model for AgeGate Harms.

The model is deliberately transparent. It is a scenario calculator, not a causal
forecast. Every output follows directly from the supplied assumptions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
import yaml

RATE_FIELDS = {
    "purchase_attempt_rate",
    "minor_share",
    "higher_friction_adult_share",
    "minor_detection_rate",
    "minor_circumvention_rate",
    "adult_false_rejection_rate",
    "adult_abandonment_rate",
    "verification_check_rate",
    "annual_breach_probability",
    "centralized_record_fraction",
}

NONNEGATIVE_FIELDS = {
    "population",
    "higher_friction_false_rejection_multiplier",
    "higher_friction_abandonment_multiplier",
    "records_per_check",
    "third_party_disclosures_per_check",
    "biometric_scans_per_check",
    "variable_cost_per_check",
    "fixed_annual_cost",
}

KEY_METRICS = [
    "minor_purchases_prevented",
    "minor_purchases_permitted",
    "adult_false_rejections",
    "adult_abandonments",
    "adult_adverse_outcomes",
    "higher_friction_adult_adverse_outcomes",
    "adult_adverse_outcomes_per_minor_purchase_prevented",
    "adult_checks_per_minor_purchase_prevented",
    "identity_records_created",
    "expected_records_exposed",
    "biometric_scans",
    "third_party_disclosures",
    "total_annual_cost",
    "cost_per_minor_purchase_prevented",
]


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and minimally validate a YAML configuration."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("Configuration root must be a mapping.")
    if "scenario" not in config or "methods" not in config:
        raise ValueError("Configuration must contain 'scenario' and 'methods'.")
    if not config["methods"]:
        raise ValueError("At least one verification method is required.")
    _validate_config(config)
    return config


def _bounds(spec: Any) -> tuple[float, float, float]:
    if isinstance(spec, Mapping):
        missing = {"low", "mode", "high"} - set(spec)
        if missing:
            raise ValueError(f"Distribution is missing fields: {sorted(missing)}")
        low = float(spec["low"])
        mode = float(spec["mode"])
        high = float(spec["high"])
    else:
        low = mode = high = float(spec)
    if not low <= mode <= high:
        raise ValueError(f"Expected low <= mode <= high, got {low}, {mode}, {high}.")
    return low, mode, high


def _validate_field(name: str, spec: Any) -> None:
    low, _, high = _bounds(spec)
    if name in RATE_FIELDS and (low < 0 or high > 1):
        raise ValueError(f"Rate '{name}' must remain between 0 and 1.")
    if name in NONNEGATIVE_FIELDS and low < 0:
        raise ValueError(f"Field '{name}' cannot be negative.")


def _validate_config(config: Mapping[str, Any]) -> None:
    required_scenario = {
        "population",
        "purchase_attempt_rate",
        "minor_share",
        "higher_friction_adult_share",
    }
    required_method = {
        "label",
        "minor_detection_rate",
        "minor_circumvention_rate",
        "adult_false_rejection_rate",
        "adult_abandonment_rate",
        "higher_friction_false_rejection_multiplier",
        "higher_friction_abandonment_multiplier",
        "verification_check_rate",
        "records_per_check",
        "annual_breach_probability",
        "third_party_disclosures_per_check",
        "biometric_scans_per_check",
        "centralized_record_fraction",
        "variable_cost_per_check",
        "fixed_annual_cost",
    }
    scenario = config["scenario"]
    missing_scenario = required_scenario - set(scenario)
    if missing_scenario:
        raise ValueError(f"Scenario is missing: {sorted(missing_scenario)}")
    for name, spec in scenario.items():
        if name in required_scenario:
            _validate_field(name, spec)
    for method_name, method in config["methods"].items():
        missing_method = required_method - set(method)
        if missing_method:
            raise ValueError(f"Method '{method_name}' is missing: {sorted(missing_method)}")
        for name, spec in method.items():
            if name in required_method - {"label"}:
                _validate_field(name, spec)


def _mode(spec: Any) -> float:
    return _bounds(spec)[1]


def _sample(spec: Any, simulations: int, rng: np.random.Generator) -> np.ndarray:
    low, mode, high = _bounds(spec)
    if low == high:
        return np.full(simulations, low, dtype=float)
    return rng.triangular(low, mode, high, size=simulations)


def _mode_values(mapping: Mapping[str, Any]) -> dict[str, float]:
    return {
        key: _mode(value)
        for key, value in mapping.items()
        if key not in {"label", "description"}
    }


def _sample_values(
    mapping: Mapping[str, Any], simulations: int, rng: np.random.Generator
) -> dict[str, np.ndarray]:
    return {
        key: _sample(value, simulations, rng)
        for key, value in mapping.items()
        if key not in {"label", "description"}
    }


def calculate_outcomes(
    scenario: Mapping[str, float | np.ndarray],
    method: Mapping[str, float | np.ndarray],
) -> dict[str, float | np.ndarray]:
    """Calculate all outcomes for scalar or vectorized inputs."""
    population = np.asarray(scenario["population"], dtype=float)
    attempt_rate = np.asarray(scenario["purchase_attempt_rate"], dtype=float)
    minor_share = np.asarray(scenario["minor_share"], dtype=float)
    higher_friction_share = np.asarray(
        scenario["higher_friction_adult_share"], dtype=float
    )

    total_attempts = population * attempt_rate
    minor_attempts = total_attempts * minor_share
    adult_attempts = total_attempts - minor_attempts

    minor_detection = np.asarray(method["minor_detection_rate"], dtype=float)
    minor_circumvention = np.asarray(method["minor_circumvention_rate"], dtype=float)
    initially_blocked_minors = minor_attempts * minor_detection
    circumvented_minor_attempts = initially_blocked_minors * minor_circumvention
    minor_purchases_prevented = initially_blocked_minors - circumvented_minor_attempts
    minor_purchases_permitted = minor_attempts - minor_purchases_prevented

    hf_adult_attempts = adult_attempts * higher_friction_share
    other_adult_attempts = adult_attempts - hf_adult_attempts

    base_abandonment = np.asarray(method["adult_abandonment_rate"], dtype=float)
    hf_abandonment_rate = np.minimum(
        1.0,
        base_abandonment
        * np.asarray(method["higher_friction_abandonment_multiplier"], dtype=float),
    )
    other_abandonments = other_adult_attempts * base_abandonment
    hf_abandonments = hf_adult_attempts * hf_abandonment_rate
    adult_abandonments = other_abandonments + hf_abandonments

    other_processed = other_adult_attempts - other_abandonments
    hf_processed = hf_adult_attempts - hf_abandonments

    base_false_rejection = np.asarray(method["adult_false_rejection_rate"], dtype=float)
    hf_false_rejection_rate = np.minimum(
        1.0,
        base_false_rejection
        * np.asarray(
            method["higher_friction_false_rejection_multiplier"], dtype=float
        ),
    )
    other_false_rejections = other_processed * base_false_rejection
    hf_false_rejections = hf_processed * hf_false_rejection_rate
    adult_false_rejections = other_false_rejections + hf_false_rejections
    adult_correctly_permitted = (
        other_processed + hf_processed - adult_false_rejections
    )

    adult_adverse_outcomes = adult_abandonments + adult_false_rejections
    higher_friction_adult_adverse_outcomes = hf_abandonments + hf_false_rejections

    check_rate = np.asarray(method["verification_check_rate"], dtype=float)
    adult_verification_checks = (other_processed + hf_processed) * check_rate
    minor_verification_checks = minor_attempts * check_rate
    total_verification_checks = adult_verification_checks + minor_verification_checks

    records_per_check = np.asarray(method["records_per_check"], dtype=float)
    identity_records_created = total_verification_checks * records_per_check
    centralized_identity_records = identity_records_created * np.asarray(
        method["centralized_record_fraction"], dtype=float
    )
    expected_records_exposed = identity_records_created * np.asarray(
        method["annual_breach_probability"], dtype=float
    )
    third_party_disclosures = total_verification_checks * np.asarray(
        method["third_party_disclosures_per_check"], dtype=float
    )
    biometric_scans = total_verification_checks * np.asarray(
        method["biometric_scans_per_check"], dtype=float
    )

    total_annual_cost = (
        total_verification_checks
        * np.asarray(method["variable_cost_per_check"], dtype=float)
        + np.asarray(method["fixed_annual_cost"], dtype=float)
    )

    denominator = np.asarray(minor_purchases_prevented, dtype=float)
    has_prevention = denominator > 0

    def ratio(numerator: float | np.ndarray) -> np.ndarray:
        numerator_array = np.asarray(numerator, dtype=float)
        output = np.full(np.broadcast(numerator_array, denominator).shape, np.nan)
        np.divide(numerator_array, denominator, out=output, where=has_prevention)
        return output

    return {
        "population": population,
        "total_purchase_attempts": total_attempts,
        "minor_purchase_attempts": minor_attempts,
        "adult_purchase_attempts": adult_attempts,
        "minor_purchases_prevented": minor_purchases_prevented,
        "minor_purchases_permitted": minor_purchases_permitted,
        "adult_correctly_permitted": adult_correctly_permitted,
        "adult_false_rejections": adult_false_rejections,
        "adult_abandonments": adult_abandonments,
        "adult_adverse_outcomes": adult_adverse_outcomes,
        "higher_friction_adult_adverse_outcomes": higher_friction_adult_adverse_outcomes,
        "adult_verification_checks": adult_verification_checks,
        "total_verification_checks": total_verification_checks,
        "identity_records_created": identity_records_created,
        "centralized_identity_records": centralized_identity_records,
        "expected_records_exposed": expected_records_exposed,
        "third_party_disclosures": third_party_disclosures,
        "biometric_scans": biometric_scans,
        "total_annual_cost": total_annual_cost,
        "adult_adverse_outcomes_per_minor_purchase_prevented": ratio(
            adult_adverse_outcomes
        ),
        "adult_checks_per_minor_purchase_prevented": ratio(
            adult_verification_checks
        ),
        "records_per_minor_purchase_prevented": ratio(identity_records_created),
        "cost_per_minor_purchase_prevented": ratio(total_annual_cost),
    }


def deterministic_comparison(config: Mapping[str, Any]) -> pd.DataFrame:
    """Run each method at the mode/default value of every assumption."""
    scenario = _mode_values(config["scenario"])
    rows: list[dict[str, Any]] = []
    for method_id, method_config in config["methods"].items():
        method = _mode_values(method_config)
        outcomes = calculate_outcomes(scenario, method)
        row = {
            "method_id": method_id,
            "method": method_config["label"],
            "description": method_config.get("description", ""),
        }
        row.update({key: float(np.asarray(value)) for key, value in outcomes.items()})
        rows.append(row)
    return pd.DataFrame(rows)


def run_monte_carlo(
    config: Mapping[str, Any], simulations: int = 50_000, seed: int = 20260722
) -> dict[str, pd.DataFrame]:
    """Run vectorized Monte Carlo simulations for all methods.

    All methods share the same sampled scenario draws, which makes comparisons
    less noisy. Method-specific assumptions are sampled independently.
    """
    if simulations < 1:
        raise ValueError("simulations must be at least 1")
    rng = np.random.default_rng(seed)
    scenario_samples = _sample_values(config["scenario"], simulations, rng)
    outputs: dict[str, pd.DataFrame] = {}
    for method_id, method_config in config["methods"].items():
        method_samples = _sample_values(method_config, simulations, rng)
        outcomes = calculate_outcomes(scenario_samples, method_samples)
        frame = pd.DataFrame(outcomes)
        for input_name, values in scenario_samples.items():
            frame[f"input__scenario__{input_name}"] = values
        for input_name, values in method_samples.items():
            frame[f"input__method__{input_name}"] = values
        frame.insert(0, "simulation", np.arange(simulations, dtype=int))
        frame.insert(1, "method_id", method_id)
        frame.insert(2, "method", method_config["label"])
        outputs[method_id] = frame
    return outputs


def sensitivity_analysis(
    simulations: Mapping[str, pd.DataFrame],
    metrics: list[str] | None = None,
) -> pd.DataFrame:
    """Estimate monotonic input influence using Spearman rank correlation.

    This is an exploratory global sensitivity diagnostic, not a causal effect.
    Constant inputs are omitted because their correlation is undefined.
    """
    metrics = metrics or [
        "minor_purchases_prevented",
        "adult_adverse_outcomes",
        "higher_friction_adult_adverse_outcomes",
        "identity_records_created",
        "expected_records_exposed",
        "total_annual_cost",
    ]
    rows: list[dict[str, Any]] = []
    for method_id, frame in simulations.items():
        method_label = str(frame["method"].iloc[0])
        input_columns = [column for column in frame if column.startswith("input__")]
        for metric in metrics:
            if metric not in frame or frame[metric].nunique(dropna=True) < 2:
                continue
            output_rank = frame[metric].rank(method="average")
            correlations: list[tuple[str, float]] = []
            for column in input_columns:
                if frame[column].nunique(dropna=True) < 2:
                    continue
                correlation = float(frame[column].rank(method="average").corr(output_rank))
                if np.isfinite(correlation):
                    correlations.append((column, correlation))
            correlations.sort(key=lambda item: abs(item[1]), reverse=True)
            for rank, (column, correlation) in enumerate(correlations, start=1):
                _, source, input_name = column.split("__", maxsplit=2)
                rows.append(
                    {
                        "method_id": method_id,
                        "method": method_label,
                        "output_metric": metric,
                        "rank": rank,
                        "input_source": source,
                        "input": input_name,
                        "spearman_correlation": correlation,
                        "absolute_correlation": abs(correlation),
                    }
                )
    return pd.DataFrame(rows)


def summarize_simulations(
    simulations: Mapping[str, pd.DataFrame],
    metrics: list[str] | None = None,
) -> pd.DataFrame:
    """Summarize simulation outputs using 5th, 50th, and 95th percentiles."""
    metrics = metrics or KEY_METRICS
    rows: list[dict[str, Any]] = []
    for method_id, frame in simulations.items():
        label = str(frame["method"].iloc[0])
        for metric in metrics:
            series = frame[metric].replace([np.inf, -np.inf], np.nan).dropna()
            if series.empty:
                values = {"p05": np.nan, "median": np.nan, "p95": np.nan, "mean": np.nan}
            else:
                values = {
                    "p05": float(series.quantile(0.05)),
                    "median": float(series.quantile(0.50)),
                    "p95": float(series.quantile(0.95)),
                    "mean": float(series.mean()),
                }
            rows.append(
                {
                    "method_id": method_id,
                    "method": label,
                    "metric": metric,
                    **values,
                }
            )
    return pd.DataFrame(rows)
