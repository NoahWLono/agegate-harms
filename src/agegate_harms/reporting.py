"""Report and chart generation for the AgeGate Harms experiment."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import base64
import html

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _fmt(value: float, decimals: int = 0) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def _summary_wide(summary: pd.DataFrame, metric: str) -> pd.DataFrame:
    return summary.loc[summary["metric"] == metric].set_index("method_id")


def write_report(
    config: Mapping[str, Any],
    deterministic: pd.DataFrame,
    summary: pd.DataFrame,
    sensitivity: pd.DataFrame,
    destination: str | Path,
    simulations: int,
    seed: int,
) -> None:
    destination = Path(destination)
    blocked = _summary_wide(summary, "minor_purchases_prevented")
    adverse = _summary_wide(summary, "adult_adverse_outcomes")
    ratio = _summary_wide(
        summary, "adult_adverse_outcomes_per_minor_purchase_prevented"
    )
    records = _summary_wide(summary, "identity_records_created")
    cost = _summary_wide(summary, "total_annual_cost")

    methods = deterministic.set_index("method_id")
    ranked_ids = (
        blocked.dropna(subset=["median"])
        .sort_values("median", ascending=False)
        .index.tolist()
    )

    lines = [
        "# AgeGate Harms experiment report",
        "",
        f"**Scenario:** {config['metadata']['title']}",
        "",
        f"**Run:** {simulations:,} Monte Carlo draws, random seed `{seed}`.",
        "",
        f"**Evidence status:** {config['metadata']['evidence_status']}",
        "",
        "This is a transparent stress-test of assumptions, not a forecast and not a finding about any existing law or vendor.",
        "",
        "## Central comparison",
        "",
        "| Method | Minor purchases prevented, median [P5–P95] | Adult adverse outcomes, median [P5–P95] | Adult adverse outcomes per minor purchase prevented | Identity records created, median | Annual cost, median |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for method_id in ranked_ids:
        label = methods.loc[method_id, "method"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(label),
                    f"{_fmt(blocked.loc[method_id, 'median'])} [{_fmt(blocked.loc[method_id, 'p05'])}–{_fmt(blocked.loc[method_id, 'p95'])}]",
                    f"{_fmt(adverse.loc[method_id, 'median'])} [{_fmt(adverse.loc[method_id, 'p05'])}–{_fmt(adverse.loc[method_id, 'p95'])}]",
                    _fmt(ratio.loc[method_id, "median"], 2),
                    _fmt(records.loc[method_id, "median"]),
                    f"${_fmt(cost.loc[method_id, 'median'])}",
                ]
            )
            + " |"
        )

    mode_rank = deterministic.loc[
        deterministic["minor_purchases_prevented"] > 0
    ].copy()
    mode_rank["privacy_records_per_prevented"] = (
        mode_rank["identity_records_created"]
        / mode_rank["minor_purchases_prevented"]
    )
    most_effective = mode_rank.sort_values(
        "minor_purchases_prevented", ascending=False
    ).iloc[0]
    lowest_adverse_ratio = mode_rank.sort_values(
        "adult_adverse_outcomes_per_minor_purchase_prevented"
    ).iloc[0]
    minimum_records = mode_rank["identity_records_created"].min()
    least_records = (
        mode_rank.loc[mode_rank["identity_records_created"] == minimum_records]
        .sort_values("minor_purchases_prevented", ascending=False)
        .iloc[0]
    )

    sensitivity_labels = {
        "minor_purchases_prevented": "Minor-purchase prevention",
        "adult_adverse_outcomes": "Adult adverse outcomes",
        "higher_friction_adult_adverse_outcomes": "Higher-friction adult adverse outcomes",
        "identity_records_created": "Identity records created",
        "expected_records_exposed": "Expected records exposed",
        "total_annual_cost": "Annual cost",
    }
    sensitivity_lines = [
        "Spearman rank correlations identify assumptions with the strongest monotonic association to each output. They are evidence-priority signals, not causal effects.",
        "",
    ]
    nonbaseline_sensitivity = sensitivity.loc[
        sensitivity["method_id"] != "no_verification"
    ]
    for output_metric, output_label in sensitivity_labels.items():
        subset = nonbaseline_sensitivity.loc[
            nonbaseline_sensitivity["output_metric"] == output_metric
        ]
        if subset.empty:
            continue
        grouped = (
            subset.groupby(["input_source", "input"], as_index=False)
            .agg(
                median_absolute_correlation=("absolute_correlation", "median"),
                methods=("method_id", "nunique"),
            )
            .sort_values("median_absolute_correlation", ascending=False)
            .head(4)
        )
        drivers = []
        for row in grouped.itertuples(index=False):
            name = str(row.input).replace("_", " ")
            drivers.append(
                f"`{row.input_source}.{name}` (median |ρ| {row.median_absolute_correlation:.2f}; {row.methods} methods)"
            )
        sensitivity_lines.extend([f"**{output_label}:** " + "; ".join(drivers), ""])

    lines.extend(
        [
            "",
            "## What the illustrative run exposes",
            "",
            f"At modal inputs, **{most_effective['method']}** prevents the largest number of minor purchases, but that statement alone says nothing about proportionality, exclusion, privacy, or cost.",
            "",
            f"At modal inputs, **{lowest_adverse_ratio['method']}** has the lowest modeled count of adult denials or abandonments per minor purchase prevented among non-baseline methods.",
            "",
            f"At modal inputs, **{least_records['method']}** is the most effective of the methods configured to create no retained identity record. This illustrates why an in-person visual check and a document-upload system can have similar access-control results but radically different data footprints.",
            "",
            "The uncertainty ranges overlap substantially for several methods. The model therefore does not support a single universal ranking. A policy choice requires explicit weighting of child-protection benefits, adult access burdens, privacy exposure, distributional effects, and implementation cost.",
            "",
            "## Sensitivity and evidence priorities",
            "",
            *sensitivity_lines,
            "## Interpretation limits",
            "",
            "1. Every numerical input is illustrative and must be replaced or bounded using evidence before policy use.",
            "2. Triangular distributions are convenience assumptions. They are not fitted probability distributions.",
            "3. Inputs are sampled independently except that all methods share the same scenario draws. Real-world parameters may be correlated.",
            "4. “Expected records exposed” is records created multiplied by an annual breach probability. It does not capture correlated catastrophic breaches or downstream misuse.",
            "5. “Adult adverse outcomes” includes false rejection and abandonment. It does not assign a moral weight to routine checks, stigma, chilling effects, or surveillance.",
            "6. Circumvention is simplified to a single rate and does not model substitution to other products or markets.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "uv sync --extra dev",
            f"uv run agegate-run --simulations {simulations} --seed {seed}",
            "uv run pytest",
            "uv sync --extra ui",
            "uv run streamlit run app.py",
            "```",
        ]
    )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_tradeoff_chart(summary: pd.DataFrame, destination: str | Path) -> None:
    """Create an uncertainty-aware effectiveness-versus-adult-burden plot."""
    blocked = summary.loc[
        summary["metric"] == "minor_purchases_prevented",
        ["method_id", "method", "p05", "median", "p95"],
    ].rename(columns={"p05": "x_p05", "median": "x_median", "p95": "x_p95"})
    adverse = summary.loc[
        summary["metric"] == "adult_adverse_outcomes",
        ["method_id", "p05", "median", "p95"],
    ].rename(columns={"p05": "y_p05", "median": "y_median", "p95": "y_p95"})
    frame = blocked.merge(adverse, on="method_id")
    frame = frame.loc[frame["method_id"] != "no_verification"].copy()

    fig, ax = plt.subplots(figsize=(11, 7))
    label_offsets = {
        "self_declaration": (5, 6),
        "visual_estimation": (5, 8),
        "facial_age_estimation": (5, 8),
        "photo_id_visual": (8, 13),
        "reusable_age_token": (8, -13),
        "document_upload": (5, 7),
        "in_person_enrolment": (5, 7),
    }
    for row in frame.itertuples(index=False):
        ax.errorbar(
            row.x_median,
            row.y_median,
            xerr=[[row.x_median - row.x_p05], [row.x_p95 - row.x_median]],
            yerr=[[row.y_median - row.y_p05], [row.y_p95 - row.y_median]],
            fmt="o",
            capsize=3,
        )
        ax.annotate(
            row.method,
            (row.x_median, row.y_median),
            xytext=label_offsets.get(row.method_id, (5, 5)),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_xlabel("Minor purchases prevented, median with P5 to P95")
    ax.set_ylabel("Adult false rejections plus abandonments")
    ax.set_title("Illustrative access-control trade-off under uncertainty")
    ax.grid(True, alpha=0.25)
    ax.margins(x=0.12, y=0.12)
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def create_privacy_chart(summary: pd.DataFrame, destination: str | Path) -> None:
    """Create a bar chart of median records and biometric processing."""
    records = summary.loc[
        summary["metric"] == "identity_records_created",
        ["method_id", "method", "median"],
    ].rename(columns={"median": "identity_records_created"})
    biometric = summary.loc[
        summary["metric"] == "biometric_scans",
        ["method_id", "median"],
    ].rename(columns={"median": "biometric_scans"})
    frame = records.merge(biometric, on="method_id").sort_values(
        "identity_records_created"
    )
    x = np.arange(len(frame))
    width = 0.38
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(
        x - width / 2,
        frame["identity_records_created"],
        width,
        label="Identity records",
    )
    ax.bar(
        x + width / 2,
        frame["biometric_scans"],
        width,
        label="Biometric scans",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(frame["method"], rotation=35, ha="right")
    ax.set_ylabel("Annual processing events, Monte Carlo median")
    ax.set_title("Illustrative median data-processing footprint")
    ax.legend()
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def write_html_dashboard(
    config: Mapping[str, Any],
    summary: pd.DataFrame,
    tradeoff_image: str | Path,
    privacy_image: str | Path,
    destination: str | Path,
    simulations: int,
    seed: int,
) -> None:
    """Write a self-contained static HTML dashboard."""
    destination = Path(destination)

    def data_uri(path: str | Path) -> str:
        raw = Path(path).read_bytes()
        return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")

    selected_metrics = [
        "minor_purchases_prevented",
        "adult_adverse_outcomes",
        "adult_adverse_outcomes_per_minor_purchase_prevented",
        "identity_records_created",
        "expected_records_exposed",
        "total_annual_cost",
    ]
    labels = {
        "minor_purchases_prevented": "Minor purchases prevented",
        "adult_adverse_outcomes": "Adult adverse outcomes",
        "adult_adverse_outcomes_per_minor_purchase_prevented": "Adult adverse outcomes per prevention",
        "identity_records_created": "Identity records created",
        "expected_records_exposed": "Expected records exposed",
        "total_annual_cost": "Annual cost",
    }
    filtered = summary[summary["metric"].isin(selected_metrics)].copy()
    medians = filtered.pivot(index="method", columns="metric", values="median")
    p05 = filtered.pivot(index="method", columns="metric", values="p05")
    p95 = filtered.pivot(index="method", columns="metric", values="p95")
    medians = medians.sort_values("minor_purchases_prevented", ascending=False)

    rows = []
    for method_name in medians.index:
        cells = [f"<th scope='row'>{html.escape(str(method_name))}</th>"]
        for metric in selected_metrics:
            median = medians.loc[method_name, metric]
            low = p05.loc[method_name, metric]
            high = p95.loc[method_name, metric]
            if pd.isna(median):
                value = "N/A"
            elif metric == "total_annual_cost":
                value = f"${median:,.0f}<small>${low:,.0f} to ${high:,.0f}</small>"
            elif metric == "adult_adverse_outcomes_per_minor_purchase_prevented":
                value = f"{median:,.2f}<small>{low:,.2f} to {high:,.2f}</small>"
            else:
                value = f"{median:,.0f}<small>{low:,.0f} to {high:,.0f}</small>"
            cells.append(f"<td>{value}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    header_cells = "".join(
        f"<th scope='col'>{html.escape(labels[metric])}</th>" for metric in selected_metrics
    )
    title = html.escape(str(config["metadata"]["title"]))
    evidence = html.escape(str(config["metadata"]["evidence_status"]))
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AgeGate Harms experiment</title>
<style>
:root {{ color-scheme: light dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
body {{ margin: 0; background: Canvas; color: CanvasText; }}
main {{ max-width: 1500px; margin: auto; padding: 2rem; }}
h1 {{ margin-bottom: .25rem; }}
.subtitle {{ font-size: 1.1rem; opacity: .8; margin-top: 0; }}
.notice {{ border: 2px solid currentColor; padding: 1rem; border-radius: .6rem; margin: 1.5rem 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 1rem; }}
.card {{ border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .6rem; padding: 1rem; overflow: auto; }}
img {{ width: 100%; height: auto; display: block; }}
table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: right; padding: .7rem; border-bottom: 1px solid color-mix(in srgb, CanvasText 18%, transparent); vertical-align: top; }}
th:first-child {{ text-align: left; position: sticky; left: 0; background: Canvas; }}
thead th {{ position: sticky; top: 0; background: Canvas; }}
small {{ display: block; opacity: .65; white-space: nowrap; margin-top: .15rem; }}
footer {{ margin-top: 2rem; opacity: .75; }}
code {{ font-family: ui-monospace, monospace; }}
</style>
</head>
<body>
<main>
<h1>AgeGate Harms experiment</h1>
<p class="subtitle">{title}</p>
<div class="notice"><strong>Evidence warning:</strong> {evidence}<br>
This is an assumption stress-test, not a forecast or finding about an existing law, retailer, or vendor.</div>
<p>Monte Carlo run: <strong>{simulations:,}</strong> draws. Seed: <code>{seed}</code>. Table cells show median, then P5 to P95.</p>
<div class="grid">
<section class="card"><h2>Access-control trade-off</h2><img alt="Scatter plot comparing minor purchases prevented with adult false rejections and abandonments" src="{data_uri(tradeoff_image)}"></section>
<section class="card"><h2>Data-processing footprint</h2><img alt="Bar chart comparing identity records and biometric scans" src="{data_uri(privacy_image)}"></section>
</div>
<section class="card" style="margin-top:1rem"><h2>Simulation summary</h2>
<table><thead><tr><th scope="col">Method</th>{header_cells}</tr></thead><tbody>{''.join(rows)}</tbody></table>
</section>
<footer>Generated by AgeGate Harms v0.1. Replace illustrative assumptions with a documented evidence registry before policy use.</footer>
</main>
</body>
</html>
"""
    destination.write_text(document, encoding="utf-8")
