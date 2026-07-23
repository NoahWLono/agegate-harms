# AgeGate Harms v0.2 experiment report

**Scenario:** Quebec Bill 9 energy-drink age-assurance evidence baseline

**Run:** 50,000 Monte Carlo draws, random seed `20260722`.

**Evidence status:** Legal facts and contextual evidence are sourced. Most operational model parameters remain explicit analyst assumptions or research gaps.

This report is a transparent stress test of registered evidence and analyst assumptions. It is not a forecast, a health-impact estimate, or a finding about any retailer or vendor.

## Central comparison

Transaction prevention and consumption prevention differ because a blocked purchase may be replaced by another product or channel. Substitution inputs remain research gaps in this release.

| Method | Minor transactions prevented, median [P5-P95] | Estimated minor consumption prevented, median [P5-P95] | Substitution events, median | Adult adverse outcomes, median | Centralized records at risk, median | Transient identity images, median | Annual cost, median |
|---|---:|---:|---:|---:|---:|---:|---:|
| In-person enrolment for later online access | 3,537 [2,663-4,601] | 1,918 [1,138-2,947] | 1,573 | 7,977 | 7,014 | 2,321 | $244,314 |
| Government photo ID, visual inspection | 3,057 [2,268-4,040] | 1,900 [1,213-2,784] | 1,117 | 3,031 | 0 | 0 | $37,705 |
| Document upload | 3,090 [2,292-4,094] | 1,788 [1,107-2,676] | 1,265 | 5,453 | 41,192 | 30,501 | $99,166 |
| Reusable third-party age token | 2,948 [2,163-3,936] | 1,703 [1,046-2,571] | 1,207 | 2,882 | 6,984 | 3,876 | $137,206 |
| Facial age estimation | 2,366 [1,657-3,294] | 1,364 [816-2,128] | 966 | 3,920 | 1,978 | 23,880 | $68,647 |
| Visual age estimation by staff | 1,231 [781-1,875] | 835 [501-1,344] | 378 | 1,930 | 0 | 0 | $17,820 |
| Self-declared age | 86 [38-163] | 58 [25-115] | 26 | 182 | 0 | 0 | $3,687 |
| No verification | 0 [0-0] | 0 [0-0] | 0 | 0 | 0 | 0 | $0 |

## Evidence coverage

The configuration attaches evidence identifiers to every modeled input. Coverage classes describe the relationship of that evidence to the parameter, not the importance of the source.

**Direct empirical coverage:** 0 of 180 modeled inputs.

| Coverage class | Parameters |
|---|---:|
| `explicit_gap` | 81 |
| `official_guidance` | 56 |
| `context_only` | 32 |
| `legal_fact` | 11 |

Legal facts, official guidance, and contextual studies do not directly estimate operational error, abandonment, circumvention, cost, or retention parameters. Those parameters stay visibly marked as assumptions or gaps.

## Sensitivity-ranked research priorities

The priority score multiplies the largest absolute Spearman correlation observed for a parameter by a documented evidence-gap weight. It is a triage device, not a measure of causal importance.

| Priority | Parameter | Method | Coverage | Maximum |rho| | Score | Research question |
|---|---|---|---|---:|---:|---|
| P0-critical | `fixed_annual_cost` | `reusable_age_token` | `explicit_gap` | 1.00 | 1.25 | Estimate implementation and compliance costs by retailer size and channel. |
| P0-critical | `fixed_annual_cost` | `self_declaration` | `explicit_gap` | 1.00 | 1.25 | Estimate implementation and compliance costs by retailer size and channel. |
| P0-critical | `fixed_annual_cost` | `visual_estimation` | `explicit_gap` | 0.99 | 1.24 | Estimate implementation and compliance costs by retailer size and channel. |
| P0-critical | `fixed_annual_cost` | `photo_id_visual` | `explicit_gap` | 0.99 | 1.24 | Estimate implementation and compliance costs by retailer size and channel. |
| P0-critical | `fixed_annual_cost` | `facial_age_estimation` | `explicit_gap` | 0.98 | 1.23 | Estimate implementation and compliance costs by retailer size and channel. |
| P0-critical | `fixed_annual_cost` | `document_upload` | `explicit_gap` | 0.98 | 1.22 | Estimate implementation and compliance costs by retailer size and channel. |
| P0-critical | `fixed_annual_cost` | `in_person_enrolment` | `explicit_gap` | 0.96 | 1.19 | Estimate implementation and compliance costs by retailer size and channel. |
| P0-critical | `adult_false_rejection_rate` | `visual_estimation` | `explicit_gap` | 0.83 | 1.04 | Measure lawful-adult false rejection using the actual threshold, devices, images, documents, and appeal process. |
| P0-critical | `minor_substitution_rate` | `in_person_enrolment` | `context_only` | 0.80 | 0.80 | Measure substitution from a blocked energy-drink purchase to other caffeinated, sugary, or informal products. |
| P0-critical | `purchase_attempt_rate` | `all methods` | `context_only` | 0.77 | 0.77 | Estimate annual relevant purchase attempts per person and by retail channel. |
| P0-critical | `minor_substitution_rate` | `document_upload` | `context_only` | 0.73 | 0.73 | Measure substitution from a blocked energy-drink purchase to other caffeinated, sugary, or informal products. |
| P0-critical | `records_per_identity_proof` | `facial_age_estimation` | `official_guidance` | 0.97 | 0.73 | Document each retained record created by the end-to-end verification data flow. |
| P0-critical | `minor_substitution_rate` | `reusable_age_token` | `context_only` | 0.73 | 0.73 | Measure substitution from a blocked energy-drink purchase to other caffeinated, sugary, or informal products. |
| P0-critical | `minor_substitution_rate` | `photo_id_visual` | `context_only` | 0.70 | 0.70 | Measure substitution from a blocked energy-drink purchase to other caffeinated, sugary, or informal products. |
| P0-critical | `minor_circumvention_rate` | `visual_estimation` | `explicit_gap` | 0.56 | 0.70 | Measure successful proxy purchase, document borrowing, cross-border, or channel switching after a block. |
| P0-critical | `minor_detection_rate` | `visual_estimation` | `explicit_gap` | 0.56 | 0.69 | Measure initial underage detection under a defined policy and operating workflow. |
| P0-critical | `minor_circumvention_rate` | `self_declaration` | `context_only` | 0.69 | 0.69 | Measure successful proxy purchase, document borrowing, cross-border, or channel switching after a block. |
| P0-critical | `annual_breach_probability` | `document_upload` | `explicit_gap` | 0.55 | 0.69 | Estimate routine breach likelihood using comparable systems and security architecture. |
| P0-critical | `minor_substitution_rate` | `facial_age_estimation` | `context_only` | 0.68 | 0.68 | Measure substitution from a blocked energy-drink purchase to other caffeinated, sugary, or informal products. |
| P0-critical | `annual_breach_probability` | `reusable_age_token` | `explicit_gap` | 0.54 | 0.68 | Estimate routine breach likelihood using comparable systems and security architecture. |

## Strongest modeled associations

| Method | Output | Input | Spearman rho |
|---|---|---|---:|
| Reusable third-party age token | `total_annual_cost` | `method.fixed_annual_cost` | 1.00 |
| Self-declared age | `total_annual_cost` | `method.fixed_annual_cost` | 1.00 |
| Visual age estimation by staff | `total_annual_cost` | `method.fixed_annual_cost` | 0.99 |
| Government photo ID, visual inspection | `total_annual_cost` | `method.fixed_annual_cost` | 0.99 |
| Facial age estimation | `total_annual_cost` | `method.fixed_annual_cost` | 0.98 |
| Document upload | `total_annual_cost` | `method.fixed_annual_cost` | 0.98 |
| Facial age estimation | `identity_records_created` | `method.records_per_identity_proof` | 0.97 |
| In-person enrolment for later online access | `total_annual_cost` | `method.fixed_annual_cost` | 0.96 |
| Self-declared age | `adult_adverse_outcomes` | `method.adult_abandonment_rate` | 0.90 |
| Document upload | `identity_records_created` | `method.records_per_identity_proof` | 0.89 |
| Document upload | `centralized_records_at_risk` | `method.record_retention_years` | 0.86 |
| Visual age estimation by staff | `adult_adverse_outcomes` | `method.adult_false_rejection_rate` | 0.83 |
| In-person enrolment for later online access | `identity_records_created` | `method.identity_proofing_rate` | 0.81 |
| Reusable third-party age token | `identity_records_created` | `method.identity_proofing_rate` | 0.81 |
| In-person enrolment for later online access | `adult_adverse_outcomes` | `method.adult_abandonment_rate` | 0.80 |
| Reusable third-party age token | `adult_adverse_outcomes` | `method.adult_abandonment_rate` | 0.80 |
| In-person enrolment for later online access | `minor_consumption_prevented` | `method.minor_substitution_rate` | -0.80 |
| Self-declared age | `higher_friction_adult_adverse_outcomes` | `method.adult_abandonment_rate` | 0.79 |
| Government photo ID, visual inspection | `adult_adverse_outcomes` | `method.adult_abandonment_rate` | 0.79 |
| In-person enrolment for later online access | `minor_purchases_prevented` | `scenario.purchase_attempt_rate` | 0.77 |

## Interpretation limits

1. Most operational inputs are still analyst-selected ranges. Contextual evidence is included to discipline future research, not to convert those ranges into measured facts.
2. Triangular distributions are convenience assumptions, not fitted probability distributions.
3. Method-specific inputs are sampled independently. Real-world error, friction, cost, and circumvention may be correlated.
4. Substitution is represented as a rate applied to blocked minor transactions. Product choice, proxy purchase, cross-border travel, and informal markets should eventually be modeled separately.
5. Reusable credentials are represented by separating routine verification checks from full identity-proofing events. The proofing rate must be measured for a concrete implementation.
6. Records at risk equal centralized records created in a year multiplied by retention years. This steady-state approximation does not model cohort aging, deletion failures, or record duplication.
7. Expected breach exposure combines routine and catastrophic expectation terms. It is not a prediction of any specific incident.
8. Higher-friction adults remain an aggregate category. The distributional research files list groups that require separate evidence before disaggregation.
9. The model does not estimate health benefits. Transaction prevention and consumption prevention are not health outcomes.
10. The Quebec remote-sales provisions depend on future regulations. The regulatory watcher can identify source changes but cannot interpret them automatically.

## Reproduction

```fish
fish run_experiment.fish --simulations 50000 --seed 20260722
uv run streamlit run app.py
```
