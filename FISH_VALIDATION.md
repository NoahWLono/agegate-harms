# Fish and Momiji validation

## What is implemented

- `run_experiment.fish` implements the complete experiment natively in fish.
- `install-on-momiji.fish` implements backup, overlay, Arch package installation, and experiment execution natively in fish.
- environment checking, release preflight, research-issue creation, and smoke testing have native fish entry points.
- Bash is not required for the fish path.

## Validation layers

1. Python tests verify that every fish entry point is present, executable, native, and contains the required workflow commands.
2. Every full fish run calls `fish -n` on all fish entry points before changing the Python environment or running the model.
3. GitHub Actions contains a `momiji-fish` job in `archlinux:latest`. It installs `fish`, `git`, `python`, and `uv` with `pacman`, syntax-checks all fish files, exercises the installer in copy-only mode, runs a reduced end-to-end experiment through fish, and verifies the outputs.
4. The complete 50,000-draw Python model pipeline and automated tests were rerun in the build VM.
5. Git checks are pinned to the canonical policy `blank-at-eol,blank-at-eof,space-before-tab`, so stricter global indentation settings cannot misclassify valid Fish, Python, YAML, TOML, or Makefile formatting.
6. The first dependency sync is followed by a complete UTF-8 normalization pass, including `uv.lock`.

## Build-VM limitation

The build VM is Debian-based and its outbound package repository access was unavailable, so a fish binary could not be installed there. Native fish runtime validation is therefore deliberately delegated to the included Arch Linux CI job rather than falsely claimed as a local VM result. The first pull-request run provides the platform-specific runtime proof for Momiji.
