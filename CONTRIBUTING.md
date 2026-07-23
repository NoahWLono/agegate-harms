# Contributing

Contributions are welcome, especially empirical evidence, source review, accessibility research, privacy threat models, retailer-cost data, test coverage, bilingual documentation, and reproducibility improvements.

## Contribution types

Every pull request should identify its primary type:

- **Code:** changes calculations, validation, reporting, tests, or interfaces.
- **Empirical evidence:** adds or revises a measured estimate.
- **Legal fact:** updates a statute, regulation, official decision, or dated legal status.
- **Official guidance:** adds a regulator, standards body, or government recommendation.
- **Analyst assumption:** changes an illustrative scenario range.
- **Normative analysis:** argues how values should be weighed without presenting that judgment as a measured fact.

## Evidence contribution checklist

An evidence record should include:

1. A stable evidence identifier.
2. The exact parameter and method relationship.
3. Whether the relationship is direct, contextual, legal, guidance, assumption, or gap.
4. Estimate, uncertainty, and unit where applicable.
5. Source title and URL.
6. Jurisdiction, population, and measurement dates.
7. Source type and independence.
8. Confidence and transferability.
9. Limitations, conflicts of interest, and known measurement problems.
10. A note explaining how the source may and may not be used.

Do not average studies automatically when they differ in threshold, population, channel, implementation, or outcome definition.

## Code quality

Run:

```fish
uv sync --extra dev --extra ui
uv run agegate-evidence \
  --config data/scenarios/quebec_bill9_v02.yaml \
  --evidence data/evidence.csv \
  --output results/evidence_coverage.csv
uv run pytest
uv run ruff check .
fish -n run_experiment.fish
for script in scripts/*.fish
    fish -n $script
end
bash -n run_experiment.sh
for script in scripts/*.sh
    bash -n $script
end
```

New model behaviour requires tests for conservation, bounds, reproducibility, and interpretation.

## Human-subject material

Do not commit identifiable interview notes, recordings, consent forms, or participant contact data. The ignored path `research/interviews/private/` is only a convenience and is not a security control. Use an approved encrypted research-data environment and an appropriate ethics process.
