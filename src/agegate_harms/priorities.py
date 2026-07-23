"""Turn model sensitivity and evidence coverage into a research backlog."""

from __future__ import annotations

from typing import Any

import pandas as pd

GAP_WEIGHTS = {
    "unmapped": 1.30,
    "explicit_gap": 1.25,
    "assumption_only": 1.15,
    "context_only": 1.00,
    "official_guidance": 0.75,
    "legal_fact": 0.55,
    "direct_empirical": 0.35,
}

QUESTION_TEMPLATES = {
    "purchase_attempt_rate": "Estimate annual relevant purchase attempts per person and by retail channel.",
    "minor_share": "Estimate the share of relevant purchase attempts made by people under 16.",
    "higher_friction_adult_share": "Estimate how many lawful adult buyers face elevated identification or digital-access friction.",
    "minor_detection_rate": "Measure initial underage detection under a defined policy and operating workflow.",
    "minor_circumvention_rate": "Measure successful proxy purchase, document borrowing, cross-border, or channel switching after a block.",
    "minor_substitution_rate": "Measure substitution from a blocked energy-drink purchase to other caffeinated, sugary, or informal products.",
    "adult_false_rejection_rate": "Measure lawful-adult false rejection using the actual threshold, devices, images, documents, and appeal process.",
    "adult_abandonment_rate": "Measure lawful-adult abandonment before and during the verification workflow.",
    "verification_check_rate": "Measure how often sellers challenge customers under the actual challenge policy.",
    "identity_proofing_rate": "Measure how often a transaction invokes full identity proofing rather than a reusable age assertion.",
    "records_per_identity_proof": "Document each retained record created by the end-to-end verification data flow.",
    "annual_breach_probability": "Estimate routine breach likelihood using comparable systems and security architecture.",
    "catastrophic_breach_probability": "Stress-test correlated or catastrophic compromise separately from routine exposure.",
    "catastrophic_exposure_fraction": "Estimate the fraction of centralized records exposed in a severe incident.",
    "third_party_disclosures_per_identity_proof": "Map every organization receiving identity information during proofing.",
    "biometric_scans_per_identity_proof": "Verify whether biometric templates or inferences are generated and how often.",
    "transient_images_per_identity_proof": "Document whether identity or face images are processed transiently even when not retained.",
    "age_assertions_per_check": "Measure unlinkable or linkable age-token presentations per transaction.",
    "centralized_record_fraction": "Measure what fraction of records are centralized or linkable across relying parties.",
    "record_retention_years": "Document contractual, technical, and legal retention periods.",
    "variable_cost_per_check": "Measure transaction-level labour, delay, support, and service fees.",
    "variable_cost_per_identity_proof": "Measure incremental cost of document, biometric, or in-person proofing.",
    "fixed_annual_cost": "Estimate implementation and compliance costs by retailer size and channel.",
}


def build_evidence_priorities(
    sensitivity: pd.DataFrame, coverage: pd.DataFrame
) -> pd.DataFrame:
    """Combine sensitivity with evidence gaps using a transparent heuristic."""
    if sensitivity.empty:
        return pd.DataFrame()
    influence = (
        sensitivity.groupby(["parameter_key", "input"], as_index=False)
        .agg(
            max_absolute_correlation=("absolute_correlation", "max"),
            median_absolute_correlation=("absolute_correlation", "median"),
            affected_methods=("method_id", "nunique"),
            affected_outputs=("output_metric", "nunique"),
        )
    )
    frame = influence.merge(
        coverage[
            [
                "parameter_key",
                "scope",
                "method_id",
                "parameter",
                "coverage_class",
                "evidence_ids",
                "needs_research",
            ]
        ],
        on="parameter_key",
        how="left",
    )
    frame["gap_weight"] = frame["coverage_class"].map(GAP_WEIGHTS).fillna(1.30)
    frame["priority_score"] = frame["max_absolute_correlation"] * frame["gap_weight"]

    def priority(score: float, needs_research: Any) -> str:
        if not bool(needs_research):
            return "P3-monitor"
        if score >= 0.65:
            return "P0-critical"
        if score >= 0.40:
            return "P1-high"
        if score >= 0.20:
            return "P2-medium"
        return "P3-low"

    frame["priority"] = [
        priority(score, gap)
        for score, gap in zip(frame["priority_score"], frame["needs_research"], strict=False)
    ]
    frame["research_question"] = frame["parameter"].map(QUESTION_TEMPLATES).fillna(
        "Find direct, jurisdiction-matched evidence for this modeled parameter."
    )
    return frame.sort_values(
        ["needs_research", "priority_score", "max_absolute_correlation"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
