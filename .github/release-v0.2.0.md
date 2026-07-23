## Summary

- adds the Quebec evidence-baseline release
- expands behavioural, privacy, distributional, breach, and cost modeling
- adds evidence validation, research protocols, reports, charts, and dashboards
- adds Fish-compatible Momiji installation and end-to-end experiment entry points
- adds a Fish CI job and documented release workflow

## Evidence status

This release is an evidence-governed research scaffold. Most operational parameters remain explicit analyst assumptions or research gaps and must not be presented as measured Quebec estimates.

## Validation

- [ ] `fish scripts/release_preflight.fish`
- [ ] `fish run_experiment.fish --simulations 50000 --seed 20260722`
- [ ] all modeled parameters have evidence or assumption mappings
- [ ] automated tests and Ruff pass
- [ ] generated report and dashboard reviewed
- [ ] staged diff contains no credentials, private interviews, redistributed PDFs, `.venv`, or unintended files
- [ ] GitHub Actions Python matrix passes
- [ ] GitHub Actions Fish job passes
