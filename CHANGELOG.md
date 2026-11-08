# Changelog

## v1.1.0 (2026-11-08)

### Commits since v1.0.1

- 8e325bb docs(docs): name revision 4.0.0 and its exceptions in the README
- e2376d1 ci(ci): add the five lab workflows and the issue and pull request templates
- 8470b85 chore(core): add the AI environment, its hooks and the lab-ai-env skill
- 1712cc4 docs(docs): add the README, licence, rules and manual
- 3aabdc5 build(build): add recipe.ps1 and the test suites it runs
- 74eb107 refactor(scripts): keep the shipped .github under template/ and settle the sources
- f5ba6c9 build(build): pin the toolchain, and decide line endings and ignores
- b954f63 docs(docs): add the BEST_REQUIREMENTS 4.0.0 gap report
- 5729766 fix(scripts): say bot branches are allowed in the success message
- f120872 test(scripts): skip the branch tests where tomllib does not exist
- cdcc7b2 fix(scripts): let a bot open a branch, and judge point 14 once
- 0b2af6f docs(docs): say who closes the issue, since dev merges do not
- 6ee11b3 ci(ci): rename the branch job to match the rule it now checks
- 77e7d8d docs(docs): record where the standard came from and what it skips
- f2ec9d1 feat(release): attach an SBOM, check types, and watch dependencies
- ea80e12 feat(ci): check branch, commits and the issue link on every pull request
- 3df35c0 chore: bring the pre-push check up to date
- b06eb8c chore: add the pre-push check that mirrors CI
- 16a0bec chore: add the pre-push check that mirrors CI
- 31189f8 fix: run the checks the way CI runs them, and stop excusing real failures
- c0dc694 docs: put the benchmark numbers in the README
- 7f6982c chore: stop tracking benchmark output
- 0acfff4 fix: recognise more than one collection error, and skip publish without a tag
- f8bcdeb fix: recognise more than one collection error, and skip publish without a tag
- fb176e4 chore: add the pre-push check that mirrors CI
- 7958aaa chore: add the pre-push check that mirrors CI
- 299c18d fix: make subprocess check= explicit in the pre-push script
- 900ff93 fix: lint the hazard audit before shipping it, and stop shipping unlinted code
- 4c752b3 feat: add a workflow hazard audit, from the four faults that broke CI today
- b9dbf99 fix: type the quality metrics script for mypy --strict
- b9b59d8 ci: survive a runner whose Tcl/Tk install is incomplete

### Issues

- #1 Bring the branch-classification fix from GitHub into test (open)
- #3 Add the BEST_REQUIREMENTS 4.0.0 gap report under docs (open)
- #6 Pin the toolchain, and decide line endings and ignores in repo-quality-template (open)
- #7 Bring the sources of repo-quality-template under the pinned tools (open)
- #8 Add recipe.ps1 and its test suites to repo-quality-template (open)
- #9 Add the README, licence, rules and manual to repo-quality-template (open)
- #10 Add the AI environment to repo-quality-template (open)
- #11 Add the gates and templates to repo-quality-template (open)
- #12 State the revision 4.0.0 compliance line in repo-quality-template (open)

### Pull requests

- #2 fix(core): bring the branch-classification fix in from GitHub (closed)
- #4 docs(docs): add the BEST_REQUIREMENTS 4.0.0 gap report (closed)
- #18 build(build): pin the toolchain, and decide line endings and ignores (closed)
- #19 refactor(scripts): keep the shipped .github under template/ and settle the sources (closed)
- #20 build(build): add recipe.ps1 and the test suites it runs (closed)
- #21 docs(docs): add the README, licence, rules and manual (closed)
- #22 chore(core): add the AI environment, its hooks and the lab-ai-env skill (closed)
- #23 ci(ci): add the five lab workflows and the issue and pull request templates (closed)
- #24 docs(docs): name revision 4.0.0 and its exceptions in the README (closed)

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Issue templates with mandatory acceptance criteria, a pull-request template,
  and `CODEOWNERS` - the shape of a contribution, in the place GitHub reads it.
- `scripts/enforce_contribution_policy.py` and `contribution-policy.yml`:
  branch grammar, commit format, sign-off and the issue link, checked before a
  human is asked to read the diff.
- `scripts/generate_sbom.py`: a CycloneDX bill of materials, attached to every
  release with its own checksum.
- Strict `mypy` over `src/`, in the lint job.
- `.github/dependabot.yml`, weekly, for pip and for actions.
- `CODE_OF_CONDUCT.md`.
- `docs/workflow.md` - issue to release, six steps.
- `docs/decisions.md` - the OpenSSF criteria this project deliberately does not
  meet, each with its reason.
- `docs/standards-comparison.md` - where the points came from, measured against
  the OpenSSF Best Practices Badge and Scorecard.

### Fixed

- The branch policy rejected every branch Dependabot opened. Point 21 asks for
  a bot that watches the dependencies and point 14 asks every branch to carry
  an issue number; a bot can do neither, so switching Dependabot on turned
  every pull request in the repository red. Bot prefixes are now a configured,
  opt-in class, with tests for all four classifications.
- `scripts/apply_template_to_repo.py` did not copy `check_before_push.py`, so a
  target repository was told to run a file it had not been given.
- The same script judged point 14 with its own copy of the rule, reading
  `git branch -a` without pruning, and reported stray branches that had been
  deleted when their pull request merged. It now calls
  `enforce_branch_policy.py`, so there is one implementation.

### Changed

- The standard is twenty-four points, not fourteen.
- Point 14 is now "three long-lived branches" rather than "three branches":
  work happens on a short-lived `<code>-<issue>/<type>/<slug>` branch that is
  deleted when its pull request merges. The old rule made a pull request
  impossible, and with it the review gate.
- `scripts/apply_template_to_repo.py` copies the new infrastructure and reports
  all twenty-four points.


## [1.0.0] - 2026-08-01

### Added

- Text analysis domain layer (`quality_template.core`): tokenising, sentence
  counting, word frequencies, lexical diversity.
- Command line interface with table and JSON output.
- tkinter desktop window with live analysis as you type.
- Test suite covering the domain layer and the CLI, with a coverage floor of 85
  percent enforced by the build.
- Benchmarks for `analyse_text`, `tokenise` and `top_words`.
- CI on Ubuntu and Windows across Python 3.10 and 3.12: lint, format check,
  tests, secret scan, quality metrics, benchmarks.
- Release workflow producing a single-file executable, a zip and a SHA-256
  checksum for each, published as a GitHub Release on a `v*.*.*` tag.
- ISO/IEC 25010 assessment, with four characteristics measured automatically by
  `scripts/collect_quality_metrics.py`.
- Branch policy of exactly `release`, `dev` and `test`, enforced by CI.
- Secret scanning with `gitleaks` both in pre-commit and over full history in CI.
- `scripts/apply_template_to_repo.py` to roll this layout onto another project.

[Unreleased]: https://github.com/IGORSVOLOHOVS/repo-quality-template/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/IGORSVOLOHOVS/repo-quality-template/releases/tag/v1.0.0
