# Publishing AgeGate Harms v0.2.0 from Momiji using fish

The package version is `0.2.0`, so the Git tag is `v0.2.0`. Publish through a release branch and pull request, then tag the exact merged commit.

## 1. Enter the installed repository and inspect it

```fish
cd ~/Projects/agegate-harms
fish scripts/check_environment.fish
git status -sb
git remote -v
git diff --stat
```

The expected remote is `NoahWLono/agegate-harms`. The installer overlays v0.2 as uncommitted files while preserving `.git`, so review the working tree before staging anything.

## 2. Put the overlay on a release branch immediately

Do this before pulling or rebasing, so the uncommitted overlay is not left on `main`:

```fish
git switch -c release/v0.2.0
```

When the branch already exists:

```fish
git switch release/v0.2.0
```

## 3. Install and authenticate GitHub CLI

```fish
sudo pacman -S --needed github-cli
gh auth login
gh auth status
gh repo view --json nameWithOwner --jq .nameWithOwner
```

The final command must print `NoahWLono/agegate-harms`. Stop if it names another repository.

## 4. Run the release checks

```fish
fish scripts/release_preflight.fish
fish run_experiment.fish --simulations 50000 --seed 20260722
```

The first successful dependency synchronization creates `uv.lock` if necessary. Confirm that it is present before staging:

```fish
test -s uv.lock; and echo "uv.lock is ready"
```

The preflight syntax-checks the fish entry points, validates evidence mappings, runs tests and Ruff, performs a reduced reproducibility run, checks Git whitespace errors, and does not publish anything. The second command regenerates the complete reference results.

## 5. Stage only the v0.2 release

First inspect everything:

```fish
git status -sb
git diff --stat
git diff
```

After confirming that the entire working tree belongs to v0.2:

```fish
git config --local core.whitespace "blank-at-eol,blank-at-eof,space-before-tab"
git add --renormalize -- .
git add --all
git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab diff --cached --check
git diff --cached --stat
git diff --cached
```

Do not continue if the staged diff contains credentials, private interview material, `.venv`, caches, unrelated personal files, or raw Monte Carlo draws that are not intended for publication.

## 6. Commit locally, then rebase onto the current remote `main`

```fish
git commit -m "Release AgeGate Harms v0.2.0"
git fetch origin
git rebase origin/main
fish scripts/release_preflight.fish
```

Committing before rebasing protects the installer overlay from being lost. Resolve any conflict deliberately, then rerun the preflight.

## 7. Push the branch and open a draft pull request

```fish
git push --set-upstream origin release/v0.2.0

gh pr create \
    --base main \
    --head release/v0.2.0 \
    --draft \
    --title "Release AgeGate Harms v0.2.0" \
    --body-file .github/release-v0.2.0.md
```

Inspect the pull request in the browser:

```fish
gh pr view --web
```

The workflow runs a Python 3.11 and 3.13 matrix plus a `momiji-fish` job inside `archlinux:latest`. That job installs Arch packages, syntax-checks every fish entry point, exercises the installer in copy-only mode, runs the complete workflow through fish, and verifies the generated outputs.

Mark the pull request ready only after reviewing the rendered documentation and all checks:

```fish
gh pr ready
```

Merge through GitHub after the checks pass. A squash merge is suitable for this release branch:

```fish
gh pr merge --squash --delete-branch
```

## 8. Tag the exact merged commit

```fish
git switch main
git pull --ff-only origin main
git tag -a v0.2.0 -m "AgeGate Harms v0.2.0: Quebec Evidence Baseline"
git push origin v0.2.0
```

Verify the tag points at the checked-out `main` commit:

```fish
test (git rev-parse HEAD) = (git rev-parse 'v0.2.0^{commit}'); and echo "Tag verified"
```

## 9. Create the GitHub release

```fish
gh release create v0.2.0 \
    --verify-tag \
    --title "AgeGate Harms v0.2.0: Quebec Evidence Baseline" \
    --notes-file RELEASE_NOTES_v0.2.0.md
```

GitHub automatically provides source archives. To attach the fish-ready Momiji bundle and checksum too:

```fish
gh release upload v0.2.0 \
    ~/Downloads/agegate-harms-momiji-fish-v0.2.0.tar.gz \
    ~/Downloads/agegate-harms-momiji-fish-v0.2.0.tar.gz.sha256
```

## Verify the published release

```fish
gh release view v0.2.0 --web
git status -sb
git log -1 --oneline
git tag --points-at HEAD
```

The final local branch should be `main`, the working tree should be clean, and `v0.2.0` should point at `HEAD`.

## Abort before pushing

Before the branch is pushed, the timestamped installer backup remains available beside the project. To discard the local release branch, first preserve any work you still need, switch back to `main`, then delete the branch. Do not use `git reset --hard` unless you have independently verified the backup.
