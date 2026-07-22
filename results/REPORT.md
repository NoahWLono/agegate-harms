# AgeGate Harms experiment report

**Scenario:** Illustrative Quebec-style energy-drink retail age-check scenario

**Run:** 50,000 Monte Carlo draws, random seed `20260722`.

**Evidence status:** All numerical inputs are illustrative assumptions, not empirical estimates.

This is a transparent stress-test of assumptions, not a forecast and not a finding about any existing law or vendor.

## Central comparison

| Method | Minor purchases prevented, median [P5–P95] | Adult adverse outcomes, median [P5–P95] | Adult adverse outcomes per minor purchase prevented | Identity records created, median | Annual cost, median |
|---|---:|---:|---:|---:|---:|
| In-person enrolment for online access | 3,535 [2,670–4,602] | 7,947 [5,146–11,417] | 2.26 | 10,258 | $253,438 |
| Document upload | 3,088 [2,279–4,088] | 5,463 [3,544–8,042] | 1.78 | 22,899 | $93,823 |
| Government photo ID, visual inspection | 3,057 [2,274–4,034] | 3,025 [1,841–4,595] | 0.99 | 0 | $36,426 |
| Reusable third-party age token | 2,946 [2,162–3,931] | 2,879 [1,692–4,608] | 0.98 | 6,902 | $134,358 |
| Facial age estimation | 2,367 [1,659–3,294] | 3,918 [2,444–5,823] | 1.66 | 6,687 | $66,634 |
| Visual age estimation | 1,236 [783–1,877] | 1,938 [1,133–2,984] | 1.57 | 0 | $17,766 |
| Self-declared age | 86 [38–163] | 183 [88–326] | 2.12 | 360 | $3,671 |
| No verification | 0 [0–0] | 0 [0–0] | N/A | 0 | $0 |

## What the illustrative run exposes

At modal inputs, **In-person enrolment for online access** prevents the largest number of minor purchases, but that statement alone says nothing about proportionality, exclusion, privacy, or cost.

At modal inputs, **Reusable third-party age token** has the lowest modeled count of adult denials or abandonments per minor purchase prevented among non-baseline methods.

At modal inputs, **Government photo ID, visual inspection** is the most effective of the methods configured to create no retained identity record. This illustrates why an in-person visual check and a document-upload system can have similar access-control results but radically different data footprints.

The uncertainty ranges overlap substantially for several methods. The model therefore does not support a single universal ranking. A policy choice requires explicit weighting of child-protection benefits, adult access burdens, privacy exposure, distributional effects, and implementation cost.

## Sensitivity and evidence priorities

Spearman rank correlations identify assumptions with the strongest monotonic association to each output. They are evidence-priority signals, not causal effects.

**Minor-purchase prevention:** `scenario.purchase attempt rate` (median |ρ| 0.70; 7 methods); `method.minor circumvention rate` (median |ρ| 0.47; 7 methods); `scenario.minor share` (median |ρ| 0.47; 7 methods); `method.minor detection rate` (median |ρ| 0.16; 7 methods)

**Adult adverse outcomes:** `method.adult abandonment rate` (median |ρ| 0.78; 7 methods); `scenario.purchase attempt rate` (median |ρ| 0.45; 7 methods); `method.adult false rejection rate` (median |ρ| 0.32; 7 methods); `scenario.higher friction adult share` (median |ρ| 0.11; 7 methods)

**Higher-friction adult adverse outcomes:** `scenario.higher friction adult share` (median |ρ| 0.54; 7 methods); `method.adult abandonment rate` (median |ρ| 0.50; 7 methods); `scenario.purchase attempt rate` (median |ρ| 0.35; 7 methods); `method.higher friction abandonment multiplier` (median |ρ| 0.34; 7 methods)

**Identity records created:** `method.records per check` (median |ρ| 0.96; 5 methods); `scenario.purchase attempt rate` (median |ρ| 0.24; 5 methods); `method.verification check rate` (median |ρ| 0.07; 5 methods); `method.adult abandonment rate` (median |ρ| 0.06; 5 methods)

**Expected records exposed:** `method.annual breach probability` (median |ρ| 0.71; 5 methods); `method.records per check` (median |ρ| 0.65; 5 methods); `scenario.purchase attempt rate` (median |ρ| 0.17; 5 methods); `method.verification check rate` (median |ρ| 0.04; 5 methods)

**Annual cost:** `method.fixed annual cost` (median |ρ| 0.99; 7 methods); `method.variable cost per check` (median |ρ| 0.09; 7 methods); `scenario.purchase attempt rate` (median |ρ| 0.03; 7 methods); `method.verification check rate` (median |ρ| 0.01; 7 methods)

## Interpretation limits

1. Every numerical input is illustrative and must be replaced or bounded using evidence before policy use.
2. Triangular distributions are convenience assumptions. They are not fitted probability distributions.
3. Inputs are sampled independently except that all methods share the same scenario draws. Real-world parameters may be correlated.
4. “Expected records exposed” is records created multiplied by an annual breach probability. It does not capture correlated catastrophic breaches or downstream misuse.
5. “Adult adverse outcomes” includes false rejection and abandonment. It does not assign a moral weight to routine checks, stigma, chilling effects, or surveillance.
6. Circumvention is simplified to a single rate and does not model substitution to other products or markets.

## Reproduction

```bash
uv sync --extra dev
uv run agegate-run --simulations 50000 --seed 20260722
uv run pytest
uv sync --extra ui
uv run streamlit run app.py
```
