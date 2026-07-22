from pathlib import Path

import numpy as np
import pytest

from agegate_harms.model import (
    calculate_outcomes,
    deterministic_comparison,
    load_config,
    run_monte_carlo,
    sensitivity_analysis,
    summarize_simulations,
)

CONFIG_PATH = Path(__file__).parents[1] / "data" / "assumptions.yaml"


def base_scenario():
    return {
        "population": 100_000.0,
        "purchase_attempt_rate": 0.25,
        "minor_share": 0.16,
        "higher_friction_adult_share": 0.10,
    }


def base_method():
    return {
        "minor_detection_rate": 0.80,
        "minor_circumvention_rate": 0.25,
        "adult_false_rejection_rate": 0.03,
        "adult_abandonment_rate": 0.05,
        "higher_friction_false_rejection_multiplier": 2.0,
        "higher_friction_abandonment_multiplier": 2.0,
        "verification_check_rate": 1.0,
        "records_per_check": 1.0,
        "annual_breach_probability": 0.01,
        "third_party_disclosures_per_check": 1.0,
        "biometric_scans_per_check": 0.0,
        "centralized_record_fraction": 0.8,
        "variable_cost_per_check": 0.5,
        "fixed_annual_cost": 10_000.0,
    }


def test_config_loads_and_contains_methods():
    config = load_config(CONFIG_PATH)
    assert "no_verification" in config["methods"]
    assert len(config["methods"]) == 8


def test_minor_population_is_conserved():
    result = calculate_outcomes(base_scenario(), base_method())
    assert result["minor_purchases_prevented"] + result["minor_purchases_permitted"] == pytest.approx(
        result["minor_purchase_attempts"]
    )


def test_adult_population_is_conserved():
    result = calculate_outcomes(base_scenario(), base_method())
    total = (
        result["adult_correctly_permitted"]
        + result["adult_false_rejections"]
        + result["adult_abandonments"]
    )
    assert total == pytest.approx(result["adult_purchase_attempts"])


def test_no_verification_is_true_baseline():
    config = load_config(CONFIG_PATH)
    row = deterministic_comparison(config).set_index("method_id").loc["no_verification"]
    assert row["minor_purchases_prevented"] == 0
    assert row["adult_adverse_outcomes"] == 0
    assert row["identity_records_created"] == 0
    assert row["total_annual_cost"] == 0
    assert np.isnan(row["cost_per_minor_purchase_prevented"])


def test_more_detection_increases_prevention_when_other_inputs_fixed():
    low = base_method()
    high = base_method()
    low["minor_detection_rate"] = 0.2
    high["minor_detection_rate"] = 0.9
    low_result = calculate_outcomes(base_scenario(), low)
    high_result = calculate_outcomes(base_scenario(), high)
    assert high_result["minor_purchases_prevented"] > low_result["minor_purchases_prevented"]


def test_more_circumvention_reduces_prevention():
    low = base_method()
    high = base_method()
    low["minor_circumvention_rate"] = 0.1
    high["minor_circumvention_rate"] = 0.8
    low_result = calculate_outcomes(base_scenario(), low)
    high_result = calculate_outcomes(base_scenario(), high)
    assert high_result["minor_purchases_prevented"] < low_result["minor_purchases_prevented"]


def test_records_and_expected_exposure_formula():
    result = calculate_outcomes(base_scenario(), base_method())
    assert result["identity_records_created"] == pytest.approx(
        result["total_verification_checks"]
    )
    assert result["expected_records_exposed"] == pytest.approx(
        result["identity_records_created"] * 0.01
    )


def test_monte_carlo_is_reproducible():
    config = load_config(CONFIG_PATH)
    first = run_monte_carlo(config, simulations=100, seed=123)
    second = run_monte_carlo(config, simulations=100, seed=123)
    assert first["photo_id_visual"]["minor_purchases_prevented"].equals(
        second["photo_id_visual"]["minor_purchases_prevented"]
    )


def test_summary_has_expected_quantile_order():
    config = load_config(CONFIG_PATH)
    simulations = run_monte_carlo(config, simulations=500, seed=321)
    summary = summarize_simulations(simulations)
    rows = summary.dropna(subset=["p05", "median", "p95"])
    assert (rows["p05"] <= rows["median"]).all()
    assert (rows["median"] <= rows["p95"]).all()


def test_invalid_rate_is_rejected(tmp_path):
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text(
        """
scenario:
  population: 1000
  purchase_attempt_rate: 1.2
  minor_share: 0.2
  higher_friction_adult_share: 0.1
methods:
  x:
    label: X
    minor_detection_rate: 0.5
    minor_circumvention_rate: 0.1
    adult_false_rejection_rate: 0.1
    adult_abandonment_rate: 0.1
    higher_friction_false_rejection_multiplier: 1
    higher_friction_abandonment_multiplier: 1
    verification_check_rate: 1
    records_per_check: 0
    annual_breach_probability: 0
    third_party_disclosures_per_check: 0
    biometric_scans_per_check: 0
    centralized_record_fraction: 0
    variable_cost_per_check: 0
    fixed_annual_cost: 0
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="between 0 and 1"):
        load_config(invalid)


def test_sensitivity_analysis_ranks_variable_inputs():
    config = load_config(CONFIG_PATH)
    simulations = run_monte_carlo(config, simulations=500, seed=456)
    sensitivity = sensitivity_analysis(simulations)
    subset = sensitivity.loc[
        (sensitivity["method_id"] == "photo_id_visual")
        & (sensitivity["output_metric"] == "minor_purchases_prevented")
    ]
    assert not subset.empty
    assert subset["rank"].min() == 1
    assert subset["absolute_correlation"].between(0, 1).all()
