# Running AgeGate Harms on Momiji with fish

Use this project location:

```text
~/Projects/agegate-harms
```

`~/Downloads` is temporary storage. `~/Projects` better reflects a repository containing source code, evidence data, tests, reports, and generated outputs.

## Install from the fish-ready Momiji bundle

Place the archive and checksum in `~/Downloads`, then run:

```fish
cd ~/Downloads
sha256sum -c agegate-harms-momiji-fish-v0.2.0.tar.gz.sha256
tar -xzf agegate-harms-momiji-fish-v0.2.0.tar.gz
cd agegate-harms-momiji-bundle-v0.2.0
fish install-on-momiji.fish --yes --with-gh
```

The installer and experiment runner are native Fish scripts. Because the installer itself runs under Fish, Fish must already be available on Momiji. It preserves an existing `.git` directory, creates a timestamped backup, installs missing Git, Python, `uv`, and optional GitHub CLI packages when needed, and invokes the native Fish experiment runner. It never commits, pushes, tags, opens a pull request, or creates a release.

The default run includes the Streamlit dependency and performs:

1. fish syntax validation;
2. dependency synchronization with `uv`;
3. evidence-registry validation;
4. the complete test suite;
5. Ruff checks;
6. the 50,000-draw reference experiment;
7. parameter-catalog export.

## Verify the local installation

```fish
cd ~/Projects/agegate-harms
fish scripts/check_environment.fish
fish scripts/momiji_smoke_test.fish
fish run_experiment.fish --simulations 50000 --seed 20260722
xdg-open results/dashboard.html
```

The first successful `uv sync` creates `uv.lock` when it is absent. Later runs use `--locked` and call `uv lock --check`. Keep the generated lock file in the v0.2.0 commit so Momiji and CI resolve the same dependency set.

Launch the interactive interface:

```fish
cd ~/Projects/agegate-harms
uv run streamlit run app.py
```

## Useful fish commands

Run a smaller exploratory experiment in a separate output directory:

```fish
fish run_experiment.fish \
    --simulations 5000 \
    --seed 12345 \
    --output results/exploratory-12345
```

Run without installing the optional Streamlit dependency:

```fish
fish run_experiment.fish --skip-ui
```

Inspect prepared research issues without creating them:

```fish
uv run python scripts/create_research_issues.py --dry-run
```

Create missing issues after reviewing the dry run and authenticating GitHub CLI:

```fish
gh auth login
fish scripts/create_research_issues.fish
```

## Manual Arch prerequisites

Fish must already be installed to launch the native installer. To install or refresh all Momiji prerequisites explicitly:

```fish
sudo pacman -S --needed fish git github-cli python uv
```

Bash is not required for the fish workflow. The Bash scripts remain only as an optional compatibility path.

## Publish v0.2.0

Run:

```fish
fish scripts/release_preflight.fish
```

Then follow `PUBLISHING.md`. It uses a release branch and draft pull request, waits for the Python and Momiji Arch fish CI jobs, and tags the merged `main` commit as `v0.2.0`.
## Git whitespace policy

The Fish workflows set the repository-local Git policy to `blank-at-eol,blank-at-eof,space-before-tab`. This prevents a stricter user-level `core.whitespace` setting from misclassifying valid Python, YAML, TOML, or Makefile indentation as release errors. The setting is local to this repository and does not alter your global Git configuration.
