# Evidence registry schema

`data/evidence.csv` is the source of truth for evidence relationships. It is intentionally a flat CSV so that reviewers can inspect and edit it without a database.

## Required columns

| Column | Meaning |
|---|---|
| `evidence_id` | Stable unique identifier used by YAML parameters. |
| `parameter` | Parameter or policy concept informed by the record. |
| `method` | Method identifier or `ALL`. |
| `relationship` | `direct`, `contextual`, `legal`, `guidance`, `assumption`, or `gap`. |
| `estimate_low` | Lower bound, when numeric. |
| `estimate_central` | Central estimate, when numeric. |
| `estimate_high` | Upper bound, when numeric. |
| `unit` | Unit of the estimate. |
| `source_title` | Full source title. |
| `source_url` | Stable source location. |
| `source_type` | Statute, official statistics, technical evaluation, vendor study, and so on. |
| `jurisdiction` | Geographic or legal context. |
| `population` | Population, systems, or transactions measured. |
| `measurement_start` | Start date or year. |
| `measurement_end` | End date or year. |
| `retrieved_on` | Date the source was checked. |
| `independence` | Relationship of source to the system or policy evaluated. |
| `status` | `empirical`, `legal_fact`, `official_guidance`, `derived`, `analyst_assumption`, or `research_gap`. |
| `confidence` | `high`, `moderate`, `low`, `illustrative`, or `not_applicable`. |
| `transferability` | `high`, `moderate`, `low`, or `not_applicable`. |
| `limitations` | Reasons the evidence may not support direct use. |
| `notes` | Interpretation and intended use. |

## Relationship is not quality

A high-quality study can be only contextual. For example, a careful survey of energy-drink consumption does not directly estimate the share of retail purchase attempts made by people under 16. A statute can be authoritative for the legal threshold and useless for estimating abandonment.

## Direct evidence standard

A record should be labeled `direct` only when its outcome, population, threshold, channel, and implementation are sufficiently aligned with the modeled parameter. Reviewers should consider:

- age threshold;
- challenge policy;
- transaction channel;
- accepted documents;
- device and image quality;
- appeal process;
- repeat versus first-time users;
- population composition;
- measurement date;
- whether the source is vendor-supplied;
- whether uncertainty and failures are reported.

## Vendor evidence

Vendor evidence may be registered, but `source_type`, `independence`, and limitations must identify it. Do not replace independent estimates with vendor headline accuracy claims. Register threshold-specific false-positive and false-negative results where available.

## Derived values

A derived record must identify inputs and transformation in `notes`. Prefer a reproducible script over a hand calculation.

## Assumptions and gaps

Every assumption should have its own record. Every unsupported operational parameter should also have an explicit gap record. This makes the absence of evidence machine-readable.

## Validation

Run:

```bash
uv run agegate-evidence \
  --config data/scenarios/quebec_bill9_v02.yaml \
  --evidence data/evidence.csv \
  --output results/evidence_coverage.csv
```

Strict mode intentionally fails until every modeled parameter has direct empirical evidence:

```bash
uv run agegate-run --strict-evidence --validate-only
```
