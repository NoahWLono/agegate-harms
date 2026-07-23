# Methodology

## Research question

How do alternative age-assurance designs trade off prohibited transaction prevention against lawful-adult access errors, deterrence, behavioural substitution, privacy exposure, distributional burden, and implementation cost?

## Status of version 0.2

Version 0.2 is an executable evidence baseline. Legal facts and contextual sources are registered. Most operational parameters are still explicit analyst-selected ranges and research gaps. The project is not an empirical evaluation of Quebec, an existing retailer, or a named verification vendor.

## Unit of analysis

The model describes annual attempted purchases in a normalized population. A scenario specifies:

- population size;
- annual relevant purchase-attempt rate;
- the share of attempts made by people below the age threshold;
- the share of adult attempts made by people facing elevated verification friction.

The default population of 100,000 is a normalization choice, not an estimate of Quebec's affected market.

## Parameter specifications

A numeric YAML parameter may be fixed:

```yaml
population:
  value: 100000
  evidence_ids:
    - ASSUMP-SCENARIO-POPULATION
    - GAP-QC-RELEVANT-POPULATION
```

Or uncertain:

```yaml
adult_false_rejection_rate:
  low: 0.008
  mode: 0.025
  high: 0.065
  evidence_ids:
    - ASSUMP-METHOD-PHOTO-ID-VISUAL-ADULT-FALSE-REJECTION-RATE
    - GAP-METHOD-PHOTO-ID-VISUAL-ADULT-FALSE-REJECTION-RATE
```

The evidence identifiers point to records that classify the relationship. A parameter can have contextual evidence and still remain an explicit gap.

## Access and behavioural model

Let:

- \(N\) be population;
- \(r_a\) be annual purchase-attempt rate;
- \(s_m\) be the minor share of attempts;
- \(d\) be minor detection rate;
- \(c\) be circumvention rate after initial detection;
- \(s\) be substitution rate after a transaction is prevented.

Total attempts are:

\[
A = N r_a
\]

Minor attempts are:

\[
M = A s_m
\]

Initially blocked minor attempts are:

\[
B_0 = M d
\]

Circumvented attempts are:

\[
C = B_0 c
\]

Covered transactions prevented are:

\[
P_t = B_0 - C
\]

Modeled substitution events are:

\[
S = P_t s
\]

Estimated consumption prevented is:

\[
P_c = P_t - S
\]

`minor_consumption_prevented` remains a behavioural proxy. It is not a dose estimate or health outcome.

## Lawful-adult model

Adults are divided into a general group and a higher-friction group. Each group can abandon before completion. False rejection is then applied to adults who remain in the workflow.

For the higher-friction group, the base abandonment and false-rejection rates are multiplied by explicit factors and capped at 1. The model conserves all adult attempts across:

- correctly permitted;
- falsely rejected;
- abandoned.

The higher-friction category is intentionally aggregate. Version 0.2 does not assign group-specific multipliers without evidence.

## Verification and identity-proofing model

A **verification check** is a transaction-level age-control event. A **full identity-proofing event** is a check that invokes a document, database, biometric process, or in-person identity workflow.

Let:

- \(q\) be the share of attempted transactions checked;
- \(p\) be the share of checks invoking full identity proofing.

Then:

\[
V = A q
\]

\[
I = V p
\]

This separation allows a reusable credential to be presented many times while full identity proofing occurs less often.

## Privacy and data-processing model

The method specifies:

- retained records per identity proof;
- centralized fraction;
- record-retention years;
- routine annual breach probability;
- catastrophic breach probability;
- catastrophic exposure fraction;
- third-party disclosures per identity proof;
- biometric scans per identity proof;
- transient images per identity proof;
- age assertions per routine check.

Annual retained records created are:

\[
R = I r
\]

Centralized records created are:

\[
R_c = R z
\]

A steady-state approximation of centralized records at risk is:

\[
R_{risk} = R_c y
\]

where \(y\) is retention years.

Expected routine exposure is:

\[
E_r = R_{risk} b
\]

Expected catastrophic exposure is:

\[
E_c = R_{risk} b_c f_c
\]

Total expected exposure is:

\[
E = E_r + E_c
\]

These are stress-test expectations. The model does not represent attack dependence, security control maturity, downstream misuse, identity reconstruction, or the social harm of a biometric leak.

## Cost model

Annual implementation cost is:

\[
K = V k_v + I k_i + K_f
\]

where:

- \(k_v\) is variable cost per routine check;
- \(k_i\) is additional variable cost per full identity proof;
- \(K_f\) is fixed annual cost.

This supports comparison of low-marginal-cost reusable credentials with expensive enrollment workflows. It does not yet model queues, lost sales, financing costs, insurance, or heterogeneous retailer scale.

## Uncertainty

Uncertain values use triangular distributions defined by low, mode, and high values. All methods share the same sampled scenario draw in each Monte Carlo iteration. Method-specific parameters are otherwise sampled independently.

The distributions are auditable conveniences, not fitted distributions. Independence is not a claim about the real world.

## Sensitivity analysis

The project calculates Spearman rank correlations between sampled inputs and selected outputs. This is a monotonic global sensitivity diagnostic.

The evidence-priority score is:

\[
priority = \max(|\rho|) \times gap\_weight
\]

Gap weights are documented in `src/agegate_harms/priorities.py`. This score helps decide what to research next. It does not establish causality or normative importance.

## Evidence coverage classes

- `direct_empirical`: direct measured evidence for the modeled parameter.
- `legal_fact`: authoritative legal source attached to the parameter.
- `official_guidance`: regulator or standards guidance attached to the parameter.
- `context_only`: measured or authoritative evidence that informs the topic but does not estimate the parameter directly.
- `explicit_gap`: a research gap is registered.
- `assumption_only`: only an analyst-selected value is registered.
- `unmapped`: no registered evidence identifiers.

## Required next steps before policy use

1. Replace high-sensitivity operational assumptions with direct, implementation-matched evidence.
2. Validate transfer from other jurisdictions and thresholds.
3. Measure challenge policy, false rejection, abandonment, circumvention, and substitution.
4. Map actual data flows and retention contracts.
5. Segment retailer costs.
6. Conduct accessibility and distributional review.
7. Update the legal snapshot after section 4 regulations are adopted.
8. Add health outcomes only through a separate, evidence-supported module.
