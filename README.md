# AgeGate Harms

**Created and maintained by Noah Weinberger.**

AgeGate Harms is an independent research project examining the privacy, accessibility, civil-liberties, distributional, behavioural, and implementation costs of age-assurance mandates.

> A transparent policy simulator and evidence registry for measuring what age-assurance systems prevent, whom they burden, what data they process, and how much they cost.

## Research status

Version 0.2 is a local release candidate dated **2026-07-22**. It contains:

- a sourced legal snapshot of Quebec's 2026 Bill 9;
- a structured evidence registry with 379 records;
- a parameter-level evidence coverage report;
- a sensitivity-ranked research backlog;
- an expanded behavioural, identity-processing, retention, breach, and cost model;
- a stakeholder interview and validation package;
- English and French executive summaries;
- a regulation-source change watcher;
- reproducible tests, reports, charts, dashboard, and run manifest.

Legal facts and contextual evidence are sourced. Most operational numerical parameters remain explicit analyst assumptions or research gaps. Version 0.2 is therefore an **evidence baseline**, not an empirical evaluation of Quebec, Bill 9, a retailer, or a vendor.

## Why the distinction matters

Age restrictions are often discussed as though enforcement were binary: verify age, block minors, problem solved. Real systems create interacting effects:

- some prohibited transactions are prevented;
- some blocked users circumvent the system;
- some users substitute another product or channel;
- some lawful adults are falsely rejected or abandon the transaction;
- some users face much higher friction than others;
- identity documents, face images, biometric inferences, and age assertions may be processed or retained;
- implementation costs differ by retailer size, sales channel, and technical design.

AgeGate Harms makes those trade-offs explicit without collapsing them into a single ethical score.

## Quebec Bill 9 case study

Quebec's *Loi visant à prévenir les effets nocifs de la boisson énergisante sur la santé des jeunes*, 2026, chapter 11, prohibits covered energy-drink sales to people under 16. When a seller asks for proof, the law specifies government or public-body photo identification showing the buyer's name and date of birth. Most provisions enter into force on December 11, 2026. The provisions for Internet, vending-machine, and other non-co-present sales depend on the first regulation made under section 4.

The authoritative legal text is registered in `data/evidence.csv` and summarized in `research/legal/bill-9.md`.

## What changed in v0.2

### Behavioural outcomes

The model now separates:

- **transactions prevented**, meaning a covered purchase did not occur through the evaluated channel;
- **substitution events**, meaning the blocked attempt is modeled as shifting to another product or channel;
- **consumption prevented**, meaning transaction prevention after the modeled substitution adjustment.

This prevents a blocked checkout from being treated automatically as a health benefit.

### Identity processing

The model separates routine verification checks from full identity-proofing events. This matters for reusable credentials. A token may be presented on many transactions while full document or biometric proofing happens less frequently.

The model separately reports:

- identity-proofing events;
- retained identity records;
- centralized records at risk after retention;
- transient identity images;
- biometric scans;
- credential assertions;
- third-party disclosures.

### Breach exposure

Routine and catastrophic exposure terms are modeled separately. Both remain transparent stress-test inputs, not breach forecasts.

### Evidence governance

Every modeled parameter carries one or more evidence identifiers. The evidence registry records whether each item is:

- direct empirical evidence;
- contextual evidence;
- a legal fact;
- official guidance;
- an analyst assumption;
- an explicit research gap.

The model does not treat contextual evidence as a direct estimate.

## Quick start

### Requirements

- Python 3.11 or newer
- `uv`

### Install and run from fish on Arch Linux

```fish
sudo pacman -S --needed fish git python uv
fish run_experiment.fish
```

`run_experiment.fish` is a native fish implementation. It does not delegate to Bash. It syntax-checks the fish entry points, synchronizes development and Streamlit dependencies, validates evidence mappings, runs tests and Ruff, executes the 50,000-draw experiment, and exports the parameter catalog.

A custom run from fish:

```fish
fish run_experiment.fish --simulations 50000 --seed 20260722
```

The Bash runner remains available as an optional compatibility path for non-fish environments:

```bash
./run_experiment.sh
```

Open the static dashboard or interactive interface from fish:

```fish
xdg-open results/dashboard.html
uv run streamlit run app.py
```

See `MOMIJI.md` for installation and `PUBLISHING.md` for the reviewed GitHub release workflow.

## Main outputs

The experiment writes:

```text
results/
├── REPORT.md
├── dashboard.html
├── deterministic_results.csv
├── monte_carlo_summary.csv
├── sensitivity.csv
├── evidence_coverage.csv
├── evidence_priorities.csv
├── tradeoff.png
├── privacy_footprint.png
├── substitution.png
├── evidence_priorities.png
└── run_manifest.json
```

## Evidence-first workflow

1. Register a source in `data/evidence.csv`.
2. Record its population, jurisdiction, date, estimate, uncertainty, independence, limitations, and relationship to the model parameter.
3. Attach its `evidence_id` to the relevant YAML parameter.
4. Run `agegate-evidence`.
5. Run the simulation and inspect `results/evidence_priorities.csv`.
6. Research the highest-sensitivity parameters with the weakest direct evidence first.
7. Preserve conflicting studies rather than averaging incompatible results automatically.
8. Update assumptions only through a documented change with a citation and rationale.

## Research files

```text
research/
├── legal/
│   ├── bill-9.md
│   └── regulations-watch.md
├── notes/
│   ├── abandonment.md
│   ├── accessibility.md
│   ├── circumvention.md
│   ├── data-flows.md
│   ├── false-rejection.md
│   ├── id-access.md
│   ├── retailer-costs.md
│   ├── sensitivity-plan.md
│   └── substitution.md
├── interviews/
│   ├── consent-script.md
│   ├── interview-protocol.md
│   ├── note-template.md
│   └── stakeholder-matrix.csv
└── sources/
    ├── README.md
    └── bibliography.bib
```

## Distributional research

`data/distributional_groups.csv` lists candidate groups and mechanisms to study. These groups are not assigned numerical multipliers merely because a burden is plausible. Disaggregation should occur only when direct evidence, participatory review, or a clearly labeled scenario assumption supports it.

## Regulatory monitoring

The remote-sales design is not settled in the sanctioned statute. The watcher records hashes of authoritative source pages and flags changes for human review:

```fish
python scripts/watch_regulations.py --initialize
uv run python scripts/watch_regulations.py
```

A hash change is not legal interpretation. It is a prompt to review the official text and update `research/legal/regulations-watch.md`.

## GitHub research backlog

The repository includes issue templates and a scripted backlog. After authenticating `gh` with write access:

```fish
python scripts/create_research_issues.py --dry-run
fish scripts/create_research_issues.fish
```

The script is idempotent by title and creates only missing issues.

## Methodological principles

1. **Separate evidence from assumptions.** A number does not become evidence because software can calculate with it.
2. **Report uncertainty.** Weak inputs should not produce falsely precise conclusions.
3. **Preserve competing values.** Prevention, lawful access, privacy, accessibility, equity, and cost are distinct objectives.
4. **Model behavioural response.** Detection accuracy is not real-world effectiveness.
5. **Distinguish transient processing from retention.** A system can create privacy risk without storing a permanent image.
6. **Distinguish repeated checks from identity proofing.** Reusable credentials change the data and cost architecture.
7. **Do not infer health benefits from blocked transactions.** Consumption, substitution, dose, and health outcomes require separate evidence.
8. **Keep legal status dated.** Regulations and guidance can change.

## What the project does not claim

AgeGate Harms does not:

- determine whether an age restriction is constitutionally valid;
- provide legal, medical, regulatory, or security advice;
- estimate the health benefit of Bill 9;
- validate a commercial age-assurance vendor;
- assume every identity check stores an ID;
- assume every biometric process retains a face image;
- prove one verification method is universally best;
- treat contextual evidence as a direct parameter estimate;
- treat illustrative results as measured facts.

## Contributing

See `CONTRIBUTING.md`. Contributions should distinguish code changes, empirical claims, legal facts, normative arguments, and analyst assumptions.

## Publishing v0.2.0

Run the non-publishing release validation first:

```fish
fish scripts/release_preflight.fish
```

Then follow `PUBLISHING.md` for the reviewed branch, draft pull request, tag, and GitHub release workflow.

## License

The software is released under the MIT License. Research reports, datasets, and third-party materials may require separate attribution where indicated.
