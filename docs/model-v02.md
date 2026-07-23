# Model v0.2 design note

## Design goals

Version 0.2 addresses five weaknesses in the original demonstration:

1. A blocked purchase was too easily read as prevented consumption.
2. Reusable credentials were not structurally different from per-transaction document checks.
3. Transient image processing and retained records were not separated.
4. Retention and catastrophic compromise were not represented.
5. Sensitivity analysis did not automatically generate an evidence backlog.

## New outcome families

### Behavioural

- `minor_purchases_prevented`
- `minor_substitution_events`
- `minor_consumption_prevented`

### Verification architecture

- `total_verification_checks`
- `identity_proofing_events`
- `credential_assertions`

### Privacy

- `identity_records_created`
- `centralized_identity_records`
- `centralized_records_at_risk`
- `transient_identity_images`
- `biometric_scans`
- `third_party_disclosures`
- `expected_routine_records_exposed`
- `expected_catastrophic_records_exposed`

### Cost

- per-check variable cost;
- per-proofing variable cost;
- fixed annual cost.

## Backward compatibility

Version 0.2 uses new field names and is not configuration-compatible with the original v0.1 YAML without migration. The public Python API remains conceptually similar: load a config, calculate deterministic outcomes, run Monte Carlo simulations, summarize, and analyze sensitivity.

`data/assumptions.yaml` is a copy of the v0.2 Quebec scenario so existing default commands still work.

## Why not add a composite score

A composite score would require normative weights for child-protection benefits, lawful access, privacy, dignity, equity, and costs. The project reports separate metrics so reviewers can see where value judgments enter.

## Why not disaggregate every group yet

Plausible unequal burdens are not sufficient to assign numerical rates. Version 0.2 creates a distributional research registry and keeps a generic higher-friction group until direct or participatory evidence supports disaggregation.

## Why the evidence-priority score is modest

The score is a workflow tool. It can reveal that an assumption strongly drives outputs and lacks direct evidence. It cannot decide whether a burden is morally important, whether an outcome is legally relevant, or whether a source is trustworthy beyond its registry classification.
