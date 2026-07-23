from pathlib import Path

import numpy as np
import pytest

from agegate_harms.evidence import coverage_report, load_evidence, validate_evidence_registry
from agegate_harms.model import (
    calculate_outcomes,
    deterministic_comparison,
    load_config,
    run_monte_carlo,
    sensitivity_analysis,
    summarize_simulations,
)
from agegate_harms.priorities import build_evidence_priorities

ROOT = Path(__file__).parents[1]
CONFIG_PATH = ROOT / "data" / "scenarios" / "quebec_bill9_v02.yaml"
EVIDENCE_PATH = ROOT / "data" / "evidence.csv"


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
        "minor_substitution_rate": 0.20,
        "adult_false_rejection_rate": 0.03,
        "adult_abandonment_rate": 0.05,
        "higher_friction_false_rejection_multiplier": 2.0,
        "higher_friction_abandonment_multiplier": 2.0,
        "verification_check_rate": 1.0,
        "identity_proofing_rate": 0.5,
        "records_per_identity_proof": 1.0,
        "annual_breach_probability": 0.01,
        "catastrophic_breach_probability": 0.001,
        "catastrophic_exposure_fraction": 0.5,
        "third_party_disclosures_per_identity_proof": 1.0,
        "biometric_scans_per_identity_proof": 0.5,
        "transient_images_per_identity_proof": 1.0,
        "age_assertions_per_check": 0.5,
        "centralized_record_fraction": 0.8,
        "record_retention_years": 2.0,
        "variable_cost_per_check": 0.1,
        "variable_cost_per_identity_proof": 0.5,
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
    total = result["adult_correctly_permitted"] + result["adult_false_rejections"] + result["adult_abandonments"]
    assert total == pytest.approx(result["adult_purchase_attempts"])


def test_substitution_separates_transaction_from_consumption_prevention():
    result = calculate_outcomes(base_scenario(), base_method())
    assert result["minor_substitution_events"] == pytest.approx(
        result["minor_purchases_prevented"] * 0.20
    )
    assert result["minor_consumption_prevented"] == pytest.approx(
        result["minor_purchases_prevented"] - result["minor_substitution_events"]
    )


def test_identity_proofing_is_distinct_from_routine_checks():
    result = calculate_outcomes(base_scenario(), base_method())
    assert result["identity_proofing_events"] == pytest.approx(
        result["total_verification_checks"] * 0.5
    )
    assert result["credential_assertions"] == pytest.approx(
        result["total_verification_checks"] * 0.5
    )


def test_retention_and_breach_formulas():
    result = calculate_outcomes(base_scenario(), base_method())
    assert result["identity_records_created"] == pytest.approx(result["identity_proofing_events"])
    assert result["centralized_records_at_risk"] == pytest.approx(
        result["identity_records_created"] * 0.8 * 2.0
    )
    assert result["expected_routine_records_exposed"] == pytest.approx(
        result["centralized_records_at_risk"] * 0.01
    )
    assert result["expected_catastrophic_records_exposed"] == pytest.approx(
        result["centralized_records_at_risk"] * 0.001 * 0.5
    )


def test_cost_includes_checks_proofing_and_fixed_cost():
    result = calculate_outcomes(base_scenario(), base_method())
    expected = (
        result["total_verification_checks"] * 0.1
        + result["identity_proofing_events"] * 0.5
        + 10_000
    )
    assert result["total_annual_cost"] == pytest.approx(expected)


def test_no_verification_is_true_baseline():
    config = load_config(CONFIG_PATH)
    row = deterministic_comparison(config).set_index("method_id").loc["no_verification"]
    assert row["minor_purchases_prevented"] == 0
    assert row["minor_consumption_prevented"] == 0
    assert row["adult_adverse_outcomes"] == 0
    assert row["identity_records_created"] == 0
    assert row["total_annual_cost"] == 0
    assert np.isnan(row["cost_per_minor_purchase_prevented"])


def test_monte_carlo_is_reproducible():
    config = load_config(CONFIG_PATH)
    first = run_monte_carlo(config, simulations=100, seed=123)
    second = run_monte_carlo(config, simulations=100, seed=123)
    assert first["photo_id_visual"]["minor_consumption_prevented"].equals(
        second["photo_id_visual"]["minor_consumption_prevented"]
    )


def test_summary_has_expected_quantile_order():
    config = load_config(CONFIG_PATH)
    simulations = run_monte_carlo(config, simulations=400, seed=321)
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
  x: {}
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="between 0 and 1"):
        load_config(invalid)


def test_evidence_registry_is_valid_and_fully_mapped():
    config = load_config(CONFIG_PATH)
    evidence = load_evidence(EVIDENCE_PATH)
    assert validate_evidence_registry(evidence) == []
    coverage = coverage_report(config, evidence)
    assert len(coverage) == 180
    assert (coverage["missing_evidence_ids"] == "").all()
    assert coverage["direct_empirical_count"].sum() == 0
    assert coverage["needs_research"].all()


def test_sensitivity_and_priorities_are_generated():
    config = load_config(CONFIG_PATH)
    evidence = load_evidence(EVIDENCE_PATH)
    coverage = coverage_report(config, evidence)
    simulations = run_monte_carlo(config, simulations=400, seed=456)
    sensitivity = sensitivity_analysis(simulations)
    priorities = build_evidence_priorities(sensitivity, coverage)
    assert not sensitivity.empty
    assert not priorities.empty
    assert priorities["max_absolute_correlation"].between(0, 1).all()
    assert priorities["research_question"].str.len().gt(10).all()


def test_deterministic_results_are_finite_where_expected():
    config = load_config(CONFIG_PATH)
    frame = deterministic_comparison(config)
    nonbaseline = frame[frame["method_id"] != "no_verification"]
    numeric = nonbaseline[["minor_purchases_prevented", "adult_adverse_outcomes", "total_annual_cost"]]
    assert np.isfinite(numeric.to_numpy()).all()
    assert (numeric >= 0).all().all()
