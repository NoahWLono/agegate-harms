# AgeGate Harms v0.2.0: Quebec Evidence Baseline

Version 0.2.0 turns the original policy simulator into an evidence-governed research scaffold for age-assurance analysis.

## Highlights

- Adds a 379-record evidence registry with parameter-level mapping and coverage validation.
- Expands behavioural modeling to distinguish blocked transactions, substitution, and estimated consumption prevention.
- Separates routine age checks from full identity proofing, retained records, centralized records at risk, transient images, biometric scans, and credential assertions.
- Adds routine and catastrophic breach-exposure terms, distributional research materials, stakeholder protocols, and regulatory monitoring.
- Generates sensitivity-ranked evidence priorities, four charts, a static dashboard, reports, and a machine-readable run manifest.
- Adds Fish-compatible Momiji installation, experiment, environment-check, issue-creation, and release-preflight entry points.
- Adds Python 3.11 and 3.13 CI plus an Arch Linux native fish end-to-end CI job.

## Evidence status

This is an evidence baseline and executable research framework, not an empirical estimate of Quebec, Bill 9, a retailer, or an age-assurance vendor. Legal and contextual records are sourced. Most operational numerical inputs remain clearly labeled analyst assumptions or research gaps.

## Reproduce on Momiji

```fish
cd ~/Projects/agegate-harms
fish scripts/check_environment.fish
fish run_experiment.fish --simulations 50000 --seed 20260722
```
