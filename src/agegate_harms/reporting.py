"""Report, chart, and static dashboard generation."""

from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any, Mapping

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
    coverage: pd.DataFrame,
    priorities: pd.DataFrame,
    destination: str | Path,
    simulations: int,
    seed: int,
) -> None:
    """Write a policy-facing Markdown report with explicit evidence limits."""
    destination = Path(destination)
    transaction_prevention = _summary_wide(summary, "minor_purchases_prevented")
    consumption_prevention = _summary_wide(summary, "minor_consumption_prevented")
    substitution = _summary_wide(summary, "minor_substitution_events")
    adverse = _summary_wide(summary, "adult_adverse_outcomes")
    records = _summary_wide(summary, "centralized_records_at_risk")
    transient = _summary_wide(summary, "transient_identity_images")
    cost = _summary_wide(summary, "total_annual_cost")

    methods = deterministic.set_index("method_id")
    ranked_ids = (
        consumption_prevention.dropna(subset=["median"])
        .sort_values("median", ascending=False)
        .index.tolist()
    )

    lines = [
        "# AgeGate Harms v0.2 experiment report",
        "",
        f"**Scenario:** {config['metadata']['title']}",
        "",
        f"**Run:** {simulations:,} Monte Carlo draws, random seed `{seed}`.",
        "",
        f"**Evidence status:** {config['metadata']['evidence_status']}",
        "",
        "This report is a transparent stress test of registered evidence and analyst assumptions. It is not a forecast, a health-impact estimate, or a finding about any retailer or vendor.",
        "",
        "## Central comparison",
        "",
        "Transaction prevention and consumption prevention differ because a blocked purchase may be replaced by another product or channel. Substitution inputs remain research gaps in this release.",
        "",
        "| Method | Minor transactions prevented, median [P5-P95] | Estimated minor consumption prevented, median [P5-P95] | Substitution events, median | Adult adverse outcomes, median | Centralized records at risk, median | Transient identity images, median | Annual cost, median |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method_id in ranked_ids:
        label = methods.loc[method_id, "method"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(label),
                    f"{_fmt(transaction_prevention.loc[method_id, 'median'])} [{_fmt(transaction_prevention.loc[method_id, 'p05'])}-{_fmt(transaction_prevention.loc[method_id, 'p95'])}]",
                    f"{_fmt(consumption_prevention.loc[method_id, 'median'])} [{_fmt(consumption_prevention.loc[method_id, 'p05'])}-{_fmt(consumption_prevention.loc[method_id, 'p95'])}]",
                    _fmt(substitution.loc[method_id, "median"]),
                    _fmt(adverse.loc[method_id, "median"]),
                    _fmt(records.loc[method_id, "median"]),
                    _fmt(transient.loc[method_id, "median"]),
                    f"${_fmt(cost.loc[method_id, 'median'])}",
                ]
            )
            + " |"
        )

    coverage_counts = (
        coverage.groupby("coverage_class")["parameter_key"].count().sort_values(ascending=False)
    )
    direct_empirical_count = int((coverage["coverage_class"] == "direct_empirical").sum())
    lines.extend(
        [
            "",
            "## Evidence coverage",
            "",
            "The configuration attaches evidence identifiers to every modeled input. Coverage classes describe the relationship of that evidence to the parameter, not the importance of the source.",
            "",
            f"**Direct empirical coverage:** {direct_empirical_count} of {len(coverage)} modeled inputs.",
            "",
            "| Coverage class | Parameters |",
            "|---|---:|",
        ]
    )
    for coverage_class, count in coverage_counts.items():
        lines.append(f"| `{coverage_class}` | {int(count)} |")

    lines.extend(
        [
            "",
            "Legal facts, official guidance, and contextual studies do not directly estimate operational error, abandonment, circumvention, cost, or retention parameters. Those parameters stay visibly marked as assumptions or gaps.",
            "",
            "## Sensitivity-ranked research priorities",
            "",
            "The priority score multiplies the largest absolute Spearman correlation observed for a parameter by a documented evidence-gap weight. It is a triage device, not a measure of causal importance.",
            "",
            "| Priority | Parameter | Method | Coverage | Maximum |rho| | Score | Research question |",
            "|---|---|---|---|---:|---:|---|",
        ]
    )
    if priorities.empty:
        lines.append("| N/A | N/A | N/A | N/A | N/A | N/A | Sensitivity analysis produced no variable inputs. |")
    else:
        for row in priorities.head(20).itertuples(index=False):
            method_label = "all methods" if row.method_id == "ALL" else row.method_id
            lines.append(
                f"| {row.priority} | `{row.parameter}` | `{method_label}` | `{row.coverage_class}` | {row.max_absolute_correlation:.2f} | {row.priority_score:.2f} | {row.research_question} |"
            )

    top_sensitivity = (
        sensitivity.loc[sensitivity["method_id"] != "no_verification"]
        .sort_values("absolute_correlation", ascending=False)
        .head(20)
    )
    lines.extend(
        [
            "",
            "## Strongest modeled associations",
            "",
            "| Method | Output | Input | Spearman rho |",
            "|---|---|---|---:|",
        ]
    )
    for row in top_sensitivity.itertuples(index=False):
        lines.append(
            f"| {row.method} | `{row.output_metric}` | `{row.input_source}.{row.input}` | {row.spearman_correlation:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation limits",
            "",
            "1. Most operational inputs are still analyst-selected ranges. Contextual evidence is included to discipline future research, not to convert those ranges into measured facts.",
            "2. Triangular distributions are convenience assumptions, not fitted probability distributions.",
            "3. Method-specific inputs are sampled independently. Real-world error, friction, cost, and circumvention may be correlated.",
            "4. Substitution is represented as a rate applied to blocked minor transactions. Product choice, proxy purchase, cross-border travel, and informal markets should eventually be modeled separately.",
            "5. Reusable credentials are represented by separating routine verification checks from full identity-proofing events. The proofing rate must be measured for a concrete implementation.",
            "6. Records at risk equal centralized records created in a year multiplied by retention years. This steady-state approximation does not model cohort aging, deletion failures, or record duplication.",
            "7. Expected breach exposure combines routine and catastrophic expectation terms. It is not a prediction of any specific incident.",
            "8. Higher-friction adults remain an aggregate category. The distributional research files list groups that require separate evidence before disaggregation.",
            "9. The model does not estimate health benefits. Transaction prevention and consumption prevention are not health outcomes.",
            "10. The Quebec remote-sales provisions depend on future regulations. The regulatory watcher can identify source changes but cannot interpret them automatically.",
            "",
            "## Reproduction",
            "",
            "```fish",
            f"fish run_experiment.fish --simulations {simulations} --seed {seed}",
            "uv run streamlit run app.py",
            "```",
        ]
    )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_tradeoff_chart(summary: pd.DataFrame, destination: str | Path) -> None:
    """Plot consumption prevention against lawful-adult adverse outcomes."""
    prevented = summary.loc[
        summary["metric"] == "minor_consumption_prevented",
        ["method_id", "method", "p05", "median", "p95"],
    ].rename(columns={"p05": "x_p05", "median": "x_median", "p95": "x_p95"})
    adverse = summary.loc[
        summary["metric"] == "adult_adverse_outcomes",
        ["method_id", "p05", "median", "p95"],
    ].rename(columns={"p05": "y_p05", "median": "y_median", "p95": "y_p95"})
    frame = prevented.merge(adverse, on="method_id")
    frame = frame.loc[frame["method_id"] != "no_verification"].copy()

    label_offsets = {
        "self_declaration": (8, 10),
        "visual_estimation": (8, 8),
        "facial_age_estimation": (8, 8),
        "document_upload": (8, 8),
        "photo_id_visual": (8, 24),
        "reusable_age_token": (8, -18),
        "in_person_enrolment": (8, 8),
    }
    fig, ax = plt.subplots(figsize=(12, 7))
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
            xytext=label_offsets.get(row.method_id, (6, 6)),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_xlabel("Estimated minor consumption prevented, median with P5-P95")
    ax.set_ylabel("Adult false rejections plus abandonments")
    ax.set_title("Illustrative effectiveness and lawful-access trade-off")
    ax.grid(True, alpha=0.25)
    ax.margins(x=0.12, y=0.12)
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def create_privacy_chart(summary: pd.DataFrame, destination: str | Path) -> None:
    """Compare retained risk and transient identity processing."""
    metrics = {
        "centralized_records_at_risk": "Centralized records at risk",
        "transient_identity_images": "Transient identity images",
        "biometric_scans": "Biometric scans",
    }
    frames = []
    for metric, label in metrics.items():
        part = summary.loc[
            summary["metric"] == metric, ["method_id", "method", "median"]
        ].copy()
        part["processing_type"] = label
        frames.append(part)
    frame = pd.concat(frames, ignore_index=True)
    pivot = frame.pivot(index="method", columns="processing_type", values="median").fillna(0)
    pivot = pivot.sort_values("Centralized records at risk")

    x = np.arange(len(pivot))
    width = 0.26
    fig, ax = plt.subplots(figsize=(13, 7))
    for index, column in enumerate(metrics.values()):
        ax.bar(x + (index - 1) * width, pivot[column], width, label=column)
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=35, ha="right")
    ax.set_ylabel("Annual events or steady-state records, Monte Carlo median")
    ax.set_title("Illustrative identity-data footprint")
    ax.legend()
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def create_substitution_chart(summary: pd.DataFrame, destination: str | Path) -> None:
    """Show the difference between transaction and consumption prevention."""
    transaction = summary.loc[
        summary["metric"] == "minor_purchases_prevented", ["method_id", "method", "median"]
    ].rename(columns={"median": "transactions_prevented"})
    consumption = summary.loc[
        summary["metric"] == "minor_consumption_prevented", ["method_id", "median"]
    ].rename(columns={"median": "consumption_prevented"})
    frame = transaction.merge(consumption, on="method_id")
    frame = frame.loc[frame["method_id"] != "no_verification"].sort_values(
        "transactions_prevented"
    )
    x = np.arange(len(frame))
    width = 0.38
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(x - width / 2, frame["transactions_prevented"], width, label="Transactions prevented")
    ax.bar(x + width / 2, frame["consumption_prevented"], width, label="Consumption prevented after substitution")
    ax.set_xticks(x)
    ax.set_xticklabels(frame["method"], rotation=35, ha="right")
    ax.set_ylabel("Annual modeled events, Monte Carlo median")
    ax.set_title("Why blocked transactions are not the same as prevented consumption")
    ax.legend()
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def create_priority_chart(priorities: pd.DataFrame, destination: str | Path) -> None:
    """Plot the highest sensitivity-weighted evidence gaps."""
    frame = priorities.loc[priorities["needs_research"]].head(15).copy()
    fig, ax = plt.subplots(figsize=(12, 8))
    if frame.empty:
        ax.text(0.5, 0.5, "No research gaps were ranked", ha="center", va="center")
        ax.set_axis_off()
    else:
        labels = [
            f"{row.parameter} ({'all' if row.method_id == 'ALL' else row.method_id})"
            for row in frame.itertuples(index=False)
        ]
        positions = np.arange(len(frame))
        ax.barh(positions, frame["priority_score"])
        ax.set_yticks(positions)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_xlabel("Sensitivity x evidence-gap weight")
        ax.set_title("Highest-priority evidence gaps")
        ax.grid(True, axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def write_html_dashboard(
    config: Mapping[str, Any],
    summary: pd.DataFrame,
    coverage: pd.DataFrame,
    priorities: pd.DataFrame,
    images: Mapping[str, str | Path],
    destination: str | Path,
    simulations: int,
    seed: int,
) -> None:
    """Write a self-contained HTML dashboard."""
    destination = Path(destination)

    def data_uri(path: str | Path) -> str:
        raw = Path(path).read_bytes()
        return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")

    selected_metrics = [
        "minor_purchases_prevented",
        "minor_consumption_prevented",
        "adult_adverse_outcomes",
        "centralized_records_at_risk",
        "transient_identity_images",
        "total_annual_cost",
    ]
    labels = {
        "minor_purchases_prevented": "Transactions prevented",
        "minor_consumption_prevented": "Consumption prevented",
        "adult_adverse_outcomes": "Adult adverse outcomes",
        "centralized_records_at_risk": "Centralized records at risk",
        "transient_identity_images": "Transient identity images",
        "total_annual_cost": "Annual cost",
    }
    filtered = summary[summary["metric"].isin(selected_metrics)].copy()
    medians = filtered.pivot(index="method", columns="metric", values="median")
    p05 = filtered.pivot(index="method", columns="metric", values="p05")
    p95 = filtered.pivot(index="method", columns="metric", values="p95")
    medians = medians.sort_values("minor_consumption_prevented", ascending=False)

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
            else:
                value = f"{median:,.0f}<small>{low:,.0f} to {high:,.0f}</small>"
            cells.append(f"<td>{value}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    coverage_rows = "".join(
        f"<tr><th>{html.escape(str(row.coverage_class))}</th><td>{int(row.parameters)}</td></tr>"
        for row in (
            coverage.groupby("coverage_class", as_index=False)
            .agg(parameters=("parameter_key", "count"))
            .sort_values("parameters", ascending=False)
            .itertuples(index=False)
        )
    )
    priority_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(row.priority))}</td>"
        f"<td><code>{html.escape(str(row.parameter))}</code></td>"
        f"<td><code>{html.escape(str(row.method_id))}</code></td>"
        f"<td>{row.max_absolute_correlation:.2f}</td>"
        f"<td>{row.priority_score:.2f}</td>"
        f"<td>{html.escape(str(row.research_question))}</td>"
        "</tr>"
        for row in priorities.head(15).itertuples(index=False)
    )
    header_cells = "".join(
        f"<th scope='col'>{html.escape(labels[metric])}</th>" for metric in selected_metrics
    )
    title = html.escape(str(config["metadata"]["title"]))
    evidence_status = html.escape(str(config["metadata"]["evidence_status"]))
    direct_empirical_count = int((coverage["coverage_class"] == "direct_empirical").sum())
    cards = "".join(
        f"<section class='card'><h2>{html.escape(label)}</h2><img alt='{html.escape(label)}' src='{data_uri(path)}'></section>"
        for label, path in images.items()
    )

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AgeGate Harms v0.2</title>
<style>
:root {{ color-scheme: light dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
body {{ margin: 0; background: Canvas; color: CanvasText; }}
main {{ max-width: 1500px; margin: auto; padding: 2rem; }}
h1 {{ margin-bottom: .25rem; }}
.subtitle {{ font-size: 1.1rem; opacity: .8; margin-top: 0; }}
.notice {{ border: 2px solid currentColor; padding: 1rem; border-radius: .6rem; margin: 1.5rem 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 1rem; }}
.card {{ border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .6rem; padding: 1rem; overflow: auto; }}
img {{ width: 100%; height: auto; display: block; }}
table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: right; padding: .65rem; border-bottom: 1px solid color-mix(in srgb, CanvasText 18%, transparent); vertical-align: top; }}
th:first-child, td:first-child {{ text-align: left; }}
small {{ display: block; opacity: .65; white-space: nowrap; margin-top: .15rem; }}
code {{ font-family: ui-monospace, monospace; }}
footer {{ margin-top: 2rem; opacity: .75; }}
</style>
</head>
<body><main>
<h1>AgeGate Harms v0.2</h1>
<p class="subtitle">{title}</p>
<div class="notice"><strong>Evidence warning:</strong> {evidence_status}<br>
Direct empirical coverage: <strong>{direct_empirical_count} of {len(coverage)}</strong> modeled inputs.<br>
Legal facts and contextual sources are registered separately from operational parameters that remain analyst assumptions.</div>
<p>Monte Carlo run: <strong>{simulations:,}</strong> draws. Seed: <code>{seed}</code>. Table cells show median, then P5 to P95.</p>
<div class="grid">{cards}</div>
<section class="card" style="margin-top:1rem"><h2>Simulation summary</h2>
<table><thead><tr><th scope="col">Method</th>{header_cells}</tr></thead><tbody>{''.join(rows)}</tbody></table>
</section>
<div class="grid" style="margin-top:1rem">
<section class="card"><h2>Evidence coverage</h2><table><thead><tr><th>Class</th><th>Parameters</th></tr></thead><tbody>{coverage_rows}</tbody></table></section>
<section class="card"><h2>Top evidence priorities</h2><table><thead><tr><th>Priority</th><th>Parameter</th><th>Method</th><th>Max |rho|</th><th>Score</th><th>Question</th></tr></thead><tbody>{priority_rows}</tbody></table></section>
</div>
<footer>Generated by AgeGate Harms v0.2. This is a research prototype, not legal, medical, regulatory, or vendor advice.</footer>
</main></body></html>
"""
    destination.write_text(document, encoding="utf-8")
