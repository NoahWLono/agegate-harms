"""Interactive Streamlit interface for AgeGate Harms."""

from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

from agegate_harms.model import calculate_outcomes, load_config

CONFIG_PATH = Path(__file__).parent / "data" / "assumptions.yaml"


def mode(spec):
    return float(spec["mode"]) if isinstance(spec, dict) else float(spec)


st.set_page_config(page_title="AgeGate Harms", layout="wide")
st.title("AgeGate Harms")
st.caption("A transparent scenario simulator for age-verification policy trade-offs")

config = load_config(CONFIG_PATH)
st.warning(config["metadata"]["evidence_status"])
st.write(
    "The simulator does not determine whether a policy is justified. "
    "It displays outcomes implied by the assumptions selected below."
)

methods = config["methods"]
labels = {method_id: method["label"] for method_id, method in methods.items()}
selected_method_id = st.sidebar.selectbox(
    "Verification method",
    options=list(methods),
    format_func=lambda item: labels[item],
)
selected = methods[selected_method_id]
st.sidebar.caption(selected.get("description", ""))

scenario_config = config["scenario"]
population = st.sidebar.number_input(
    "Population", min_value=1_000, max_value=10_000_000, value=int(mode(scenario_config["population"])), step=1_000
)
attempt_rate = st.sidebar.slider(
    "Annual purchase-attempt rate", 0.0, 1.0, mode(scenario_config["purchase_attempt_rate"]), 0.01
)
minor_share = st.sidebar.slider(
    "Minor share", 0.0, 1.0, mode(scenario_config["minor_share"]), 0.01
)
higher_friction_share = st.sidebar.slider(
    "Adults facing elevated verification friction", 0.0, 0.5, mode(scenario_config["higher_friction_adult_share"]), 0.01
)

st.sidebar.subheader("Method assumptions")
detection = st.sidebar.slider("Minor detection rate", 0.0, 1.0, mode(selected["minor_detection_rate"]), 0.01)
circumvention = st.sidebar.slider("Circumvention after initial block", 0.0, 1.0, mode(selected["minor_circumvention_rate"]), 0.01)
false_rejection = st.sidebar.slider("Adult false-rejection rate", 0.0, 0.5, mode(selected["adult_false_rejection_rate"]), 0.005)
abandonment = st.sidebar.slider("Adult abandonment rate", 0.0, 0.6, mode(selected["adult_abandonment_rate"]), 0.005)
records_per_check = st.sidebar.number_input("Records created per check", min_value=0.0, max_value=5.0, value=mode(selected["records_per_check"]), step=0.05)
breach_probability = st.sidebar.slider("Annual breach probability", 0.0, 0.2, mode(selected["annual_breach_probability"]), 0.001)
variable_cost = st.sidebar.number_input("Variable cost per check", min_value=0.0, max_value=20.0, value=mode(selected["variable_cost_per_check"]), step=0.01)
fixed_cost = st.sidebar.number_input("Fixed annual cost", min_value=0.0, max_value=5_000_000.0, value=mode(selected["fixed_annual_cost"]), step=1_000.0)

scenario = {
    "population": float(population),
    "purchase_attempt_rate": attempt_rate,
    "minor_share": minor_share,
    "higher_friction_adult_share": higher_friction_share,
}
method = {
    key: mode(value)
    for key, value in selected.items()
    if key not in {"label", "description"}
}
method.update(
    {
        "minor_detection_rate": detection,
        "minor_circumvention_rate": circumvention,
        "adult_false_rejection_rate": false_rejection,
        "adult_abandonment_rate": abandonment,
        "records_per_check": records_per_check,
        "annual_breach_probability": breach_probability,
        "variable_cost_per_check": variable_cost,
        "fixed_annual_cost": fixed_cost,
    }
)
outcomes = calculate_outcomes(scenario, method)
flat = {key: float(value) for key, value in outcomes.items()}

col1, col2, col3, col4 = st.columns(4)
col1.metric("Minor purchases prevented", f"{flat['minor_purchases_prevented']:,.0f}")
col2.metric("Adult adverse outcomes", f"{flat['adult_adverse_outcomes']:,.0f}")
col3.metric("Identity records created", f"{flat['identity_records_created']:,.0f}")
col4.metric("Annual implementation cost", f"${flat['total_annual_cost']:,.0f}")

st.subheader("Access outcomes")
access = pd.DataFrame(
    {
        "Outcome": [
            "Minor purchases prevented",
            "Minor purchases permitted",
            "Adults correctly permitted",
            "Adult false rejections",
            "Adult abandonments",
            "Higher-friction adult adverse outcomes",
        ],
        "Count": [
            flat["minor_purchases_prevented"],
            flat["minor_purchases_permitted"],
            flat["adult_correctly_permitted"],
            flat["adult_false_rejections"],
            flat["adult_abandonments"],
            flat["higher_friction_adult_adverse_outcomes"],
        ],
    }
).set_index("Outcome")
st.bar_chart(access)

st.subheader("Data-processing footprint")
privacy = pd.DataFrame(
    {
        "Metric": [
            "Verification checks",
            "Identity records created",
            "Centralized identity records",
            "Expected records exposed",
            "Third-party disclosures",
            "Biometric scans",
        ],
        "Count": [
            flat["total_verification_checks"],
            flat["identity_records_created"],
            flat["centralized_identity_records"],
            flat["expected_records_exposed"],
            flat["third_party_disclosures"],
            flat["biometric_scans"],
        ],
    }
)
st.dataframe(privacy, use_container_width=True, hide_index=True)

st.subheader("Ratio metrics")
ratios = pd.DataFrame(
    {
        "Metric": [
            "Adult adverse outcomes per minor purchase prevented",
            "Adult checks per minor purchase prevented",
            "Records per minor purchase prevented",
            "Cost per minor purchase prevented",
        ],
        "Value": [
            flat["adult_adverse_outcomes_per_minor_purchase_prevented"],
            flat["adult_checks_per_minor_purchase_prevented"],
            flat["records_per_minor_purchase_prevented"],
            flat["cost_per_minor_purchase_prevented"],
        ],
    }
)
st.dataframe(ratios, use_container_width=True, hide_index=True)

with st.expander("Current assumptions as YAML"):
    st.code(yaml.safe_dump({"scenario": scenario, "method": method}, sort_keys=False), language="yaml")
