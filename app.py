"""Interactive Streamlit interface for AgeGate Harms v0.2."""

from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

from agegate_harms.evidence import coverage_report, load_evidence
from agegate_harms.model import calculate_outcomes, load_config, spec_bounds

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "data" / "scenarios" / "quebec_bill9_v02.yaml"
EVIDENCE_PATH = ROOT / "data" / "evidence.csv"


def mode(spec):
    return float(spec_bounds(spec)[1])


st.set_page_config(page_title="AgeGate Harms v0.2", layout="wide")
st.title("AgeGate Harms v0.2")
st.caption("A transparent scenario simulator and evidence map for age-assurance policy trade-offs")

config = load_config(CONFIG_PATH)
evidence = load_evidence(EVIDENCE_PATH)
coverage = coverage_report(config, evidence)
st.warning(config["metadata"]["evidence_status"])
st.write(
    "The interface displays outcomes implied by selected assumptions. It does not determine whether a policy is justified and it does not estimate health benefits."
)

with st.expander("Evidence coverage", expanded=False):
    summary = (
        coverage.groupby("coverage_class", as_index=False)
        .agg(parameters=("parameter_key", "count"))
        .sort_values("parameters", ascending=False)
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.download_button(
        "Download parameter-level coverage CSV",
        coverage.to_csv(index=False),
        file_name="evidence_coverage.csv",
        mime="text/csv",
    )

methods = config["methods"]
labels = {method_id: method["label"] for method_id, method in methods.items()}
selected_method_id = st.sidebar.selectbox(
    "Verification method", options=list(methods), format_func=lambda item: labels[item]
)
selected = methods[selected_method_id]
st.sidebar.caption(selected.get("description", ""))

scenario_config = config["scenario"]
population = st.sidebar.number_input(
    "Normalized population",
    min_value=1_000,
    max_value=20_000_000,
    value=int(mode(scenario_config["population"])),
    step=1_000,
)
attempt_rate = st.sidebar.slider(
    "Annual purchase-attempt rate",
    0.0,
    1.0,
    mode(scenario_config["purchase_attempt_rate"]),
    0.01,
)
minor_share = st.sidebar.slider(
    "Share of attempts made by people under 16",
    0.0,
    1.0,
    mode(scenario_config["minor_share"]),
    0.01,
)
higher_friction_share = st.sidebar.slider(
    "Adults facing elevated verification friction",
    0.0,
    0.5,
    mode(scenario_config["higher_friction_adult_share"]),
    0.01,
)

st.sidebar.subheader("Method assumptions")
detection = st.sidebar.slider("Minor detection rate", 0.0, 1.0, mode(selected["minor_detection_rate"]), 0.01)
circumvention = st.sidebar.slider("Circumvention after block", 0.0, 1.0, mode(selected["minor_circumvention_rate"]), 0.01)
substitution = st.sidebar.slider("Substitution after prevented purchase", 0.0, 1.0, mode(selected["minor_substitution_rate"]), 0.01)
false_rejection = st.sidebar.slider("Adult false-rejection rate", 0.0, 0.5, mode(selected["adult_false_rejection_rate"]), 0.005)
abandonment = st.sidebar.slider("Adult abandonment rate", 0.0, 0.7, mode(selected["adult_abandonment_rate"]), 0.005)
check_rate = st.sidebar.slider("Share of attempts checked", 0.0, 1.0, mode(selected["verification_check_rate"]), 0.01)
proof_rate = st.sidebar.slider("Full identity proofs per check", 0.0, 1.0, mode(selected["identity_proofing_rate"]), 0.01)
retention = st.sidebar.number_input(
    "Record retention years", min_value=0.0, max_value=20.0, value=mode(selected["record_retention_years"]), step=0.25
)
fixed_cost = st.sidebar.number_input(
    "Fixed annual cost", min_value=0.0, max_value=10_000_000.0, value=mode(selected["fixed_annual_cost"]), step=1_000.0
)

scenario = {
    "population": float(population),
    "purchase_attempt_rate": attempt_rate,
    "minor_share": minor_share,
    "higher_friction_adult_share": higher_friction_share,
}
method = {
    key: mode(value)
    for key, value in selected.items()
    if key not in {"label", "description", "policy_family", "channel"}
}
method.update(
    {
        "minor_detection_rate": detection,
        "minor_circumvention_rate": circumvention,
        "minor_substitution_rate": substitution,
        "adult_false_rejection_rate": false_rejection,
        "adult_abandonment_rate": abandonment,
        "verification_check_rate": check_rate,
        "identity_proofing_rate": proof_rate,
        "record_retention_years": retention,
        "fixed_annual_cost": fixed_cost,
    }
)
outcomes = calculate_outcomes(scenario, method)
flat = {key: float(value) for key, value in outcomes.items()}

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Minor transactions prevented", f"{flat['minor_purchases_prevented']:,.0f}")
col2.metric("Minor consumption prevented", f"{flat['minor_consumption_prevented']:,.0f}")
col3.metric("Adult adverse outcomes", f"{flat['adult_adverse_outcomes']:,.0f}")
col4.metric("Centralized records at risk", f"{flat['centralized_records_at_risk']:,.0f}")
col5.metric("Annual implementation cost", f"${flat['total_annual_cost']:,.0f}")

st.subheader("Access and behavioural outcomes")
access = pd.DataFrame(
    {
        "Outcome": [
            "Minor transactions prevented",
            "Minor substitution events",
            "Minor consumption prevented",
            "Minor purchases permitted",
            "Adults correctly permitted",
            "Adult false rejections",
            "Adult abandonments",
            "Higher-friction adult adverse outcomes",
        ],
        "Count": [
            flat["minor_purchases_prevented"],
            flat["minor_substitution_events"],
            flat["minor_consumption_prevented"],
            flat["minor_purchases_permitted"],
            flat["adult_correctly_permitted"],
            flat["adult_false_rejections"],
            flat["adult_abandonments"],
            flat["higher_friction_adult_adverse_outcomes"],
        ],
    }
).set_index("Outcome")
st.bar_chart(access)

st.subheader("Identity-data and privacy footprint")
privacy = pd.DataFrame(
    {
        "Metric": [
            "Verification checks",
            "Full identity-proofing events",
            "Identity records created",
            "Centralized records at risk",
            "Expected routine records exposed",
            "Expected catastrophic records exposed",
            "Third-party disclosures",
            "Credential assertions",
            "Biometric scans",
            "Transient identity images",
        ],
        "Count": [
            flat["total_verification_checks"],
            flat["identity_proofing_events"],
            flat["identity_records_created"],
            flat["centralized_records_at_risk"],
            flat["expected_routine_records_exposed"],
            flat["expected_catastrophic_records_exposed"],
            flat["third_party_disclosures"],
            flat["credential_assertions"],
            flat["biometric_scans"],
            flat["transient_identity_images"],
        ],
    }
)
st.dataframe(privacy, use_container_width=True, hide_index=True)

with st.expander("Current selected assumptions as YAML"):
    st.code(yaml.safe_dump({"scenario": scenario, "method": method}, sort_keys=False), language="yaml")
