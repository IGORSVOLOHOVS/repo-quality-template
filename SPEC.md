# Software Requirements Specification — repo-quality-template

Reverse-engineered from the code at commit `d74be72` (`origin/dev`, 2026-09-06)
on 2026-11-18. Every requirement states only behaviour that the cited code
implements. Inferences are labelled. Claims that the code does not back are
listed in §3.8. Questions the code cannot answer are in §9. The documentation
hub is [`docs/README.md`](docs/README.md).

## 1. Purpose and scope

The repository contains:

1. **Text Analyser**, the Python package `quality_template`. It computes
   statistics of a text and shows them through a command-line interface and a
   tkinter window.
2. **A reference repository layout** for that package: CI workflows, policy and
   quality scripts, release packaging, a bill-of-materials generator, and a
   script that copies the layout into another repository.

The package docstring states that the application exists to give the quality
controls "something concrete to act on" (`src/quality_template/__init__.py:1-6`).

In scope:

- text statistics, the CLI and the desktop window (`src/quality_template/`);
- the scripts in `scripts/`;
- the GitHub workflows and repository configuration in `.github/`,
  `pyproject.toml` and `.pre-commit-config.yaml`.

Out of scope, by evidence in the code or in the author's documents:

- network access, persistent storage, configuration files and environment
  variables for the application (`docs/architecture.md:57-58`,
  `docs/quality-iso25010.md:51-52`; no environment reads, file writes or
  network imports under `src/`);
- streaming of large inputs (`docs/architecture.md:61-63`);
- a plugin system and caching (`docs/architecture.md:55-60`);
- internationalisation, two-person review, governance documents, reproducible
  builds, fuzzing and signed binaries (`docs/decisions.md`).

## 2. Context

| Actor / system | Role | Evidence |
| --- | --- | --- |
| End user | Runs `quality-template` on a file or stdin, or opens the window | `README.md:46-63`, `src/quality_template/cli.py` |
| Contributor | Opens issues, works on `<code>-<issue>/<type>/<slug>` branches, opens PRs into `dev` | `CONTRIBUTING.md`, `docs/workflow.md` |
| Maintainer / code owner | Reviews PRs, as declared in `CODEOWNERS`; cuts releases from `release` | `.github/CODEOWNERS`, `docs/branching.md:82-94` |
| GitHub Actions | Runs CI, the policy checks and the release | `.github/workflows/*.yml` |
| GitHub Releases | Receives the artefacts, checksums and SBOM | `.github/workflows/release.yml:79-85` |
| Dependabot | Opens weekly update PRs for pip and for GitHub Actions | `.github/dependabot.yml` |
| git | Queried by the policy scripts, the SBOM script and the hazard audit | `scripts/enforce_*.py`, `scripts/generate_sbom.py:48-51` |
| PyInstaller | Builds the single-file executable | `scripts/build_release_artifact.py:39-85` |
| Playwright / Chromium, Win32 API | Screenshot capture | `scripts/capture_usage_screenshots.py` |

Runtime environment:

| Item | Value | Source |
| --- | --- | --- |
| Language runtime | CPython `>=3.10`; scripts that import `tomllib` need 3.11 or newer | `pyproject.toml:10`; `scripts/enforce_contribution_policy.py:32-35`, `scripts/enforce_branch_policy.py:32`, `scripts/generate_sbom.py:27` |
| GUI toolkit | tkinter/ttk, theme `clam` | `src/quality_template/app.py:9-11,45` |
| Operating systems tested in CI | `ubuntu-latest`, `windows-latest` | `.github/workflows/ci.yml:44` |
| Release build hosts | `windows-latest`, `ubuntu-latest` | `.github/workflows/release.yml:23` |
| Hardware | not specified | — |

## 3. Functional requirements

### 3.1 Text analysis (domain layer, `src/quality_template/core.py`)

**FR-1.** The system shall split text into lower-cased word tokens. A token is
a run of letters with at most one internal apostrophe followed by more letters;
digits, underscores and punctuation are dropped.
Source: `src/quality_template/core.py:15,88-94`.
Verification: `tests/test_core.py::TestTokenise` (5 tests).

**FR-2.** The system shall count sentences as runs of `.`, `!` or `?` followed
by whitespace or the end of the text. Non-blank text with no terminator counts
as 1 sentence, and blank text as 0.
Source: `src/quality_template/core.py:16,97-107`.
Verification: `tests/test_core.py::TestCountSentences::test_counts` (6 cases).

**FR-3.** The system shall return, for a string, a `TextStats` with:

- `characters` = `len(text)`;
- word count and unique word count;
- sentence count;
- mean token length;
- longest token, the first one of maximal length;
- the word-frequency counter.

Source: `src/quality_template/core.py:110-131`.
Verification: `TestAnalyseText::test_basic_counts`, `test_longest_word`, `test_average_word_length`.

**FR-4.** The system shall report, for text with no tokens, zero words, zero
unique words, average length `0.0`, longest word `""` and lexical diversity
`0.0`.
Source: `src/quality_template/core.py:83-84,128-129`.
Verification: `TestAnalyseText::test_empty_text_is_all_zero`.

**FR-5.** The system shall compute lexical diversity as unique words divided by
words.
Source: `src/quality_template/core.py:76-85`.
Verification: `TestAnalyseText::test_lexical_diversity`.

**FR-6.** The system shall raise `TypeError("expected str, got <type>")` when
`analyse_text` receives a non-string.
Source: `src/quality_template/core.py:116-117`.
Verification: `TestAnalyseText::test_rejects_non_string`.

**FR-7.** The system shall make `TextStats` immutable: it is a frozen
dataclass.
Source: `src/quality_template/core.py:64`.
Verification: `TestAnalyseText::test_stats_are_immutable`.

**FR-8.** The system shall return at most `limit` `(word, count)` pairs, most
frequent first. By default it excludes the 39 words in `STOP_WORDS`;
`drop_stop_words=False` keeps them.
Source: `src/quality_template/core.py:19-61,151-170`.
Verification: `TestTopWords::test_orders_by_frequency`, `test_drops_stop_words_by_default`, `test_can_keep_stop_words`, `test_limit_is_respected`, `test_text_of_only_stop_words_yields_nothing`, `test_stop_words_are_lowercase`.

**FR-9.** The system shall raise `ValueError("limit must be positive")` when
`limit <= 0`.
Source: `src/quality_template/core.py:164-165`.
Verification: `TestTopWords::test_rejects_non_positive_limit`.

**FR-10.** The system shall render a `TextStats` as seven label→string pairs:

- average word length with 2 decimals;
- lexical diversity with 3 decimals;
- `-` as the longest word when there is none.

Source: `src/quality_template/core.py:134-148`.
Verification: `tests/test_app.py::TestFormatMetrics` (5 tests).

### 3.2 Command-line interface (`src/quality_template/cli.py`)

**FR-11.** The system shall read the file given as `path` as UTF-8, replacing
undecodable bytes. With no `path` it shall read standard input.
Source: `src/quality_template/cli.py:38-43`.
Verification: `tests/test_cli.py::test_table_output`, `test_reads_stdin_when_no_path`.

**FR-12.** The system shall exit with status 1 and the message
`error: no such file: <path>` when `path` is not an existing file.
Source: `src/quality_template/cli.py:41-42`.
Verification: `test_missing_file_exits_with_message`; exit status 1 observed on 2026-11-18.

**FR-13.** The system shall print, by default, a table of seven metrics, each
label left-aligned in 22 columns. When the word list is not empty, it shall
then print a blank line, `most frequent words`, and one indented row per word.
Source: `src/quality_template/cli.py:46-61,93`.
Verification: `test_table_output`.

**FR-14.** The system shall, with `--json`, print a JSON object instead of the
table (format in §4.2), indented by 2 and with non-ASCII characters unescaped.
Source: `src/quality_template/cli.py:75-91`.
Verification: `test_json_output_is_valid`, `test_empty_file`.

**FR-15.** The system shall limit the word list to `-n/--top N` entries,
default 10.
Source: `src/quality_template/cli.py:22-24,73`.
Verification: `test_top_limit`.

**FR-16.** The system shall keep stop words in the word list when
`--keep-stop-words` is given.
Source: `src/quality_template/cli.py:25-27,73`.
Verification: `test_keep_stop_words_changes_result`.

**FR-17.** The system shall print `quality-template <version>` and exit 0 on
`--version`.
Source: `src/quality_template/cli.py:34`, `src/quality_template/__init__.py:11`.
Verification: `test_version_flag`.

**FR-18.** The system shall, with `--gui`, open the desktop window instead of
printing. The window is pre-filled with the file's content when `path` is an
existing file, and with a built-in sample text otherwise.
Source: `src/quality_template/cli.py:67-70`, `src/quality_template/app.py:154-158`.
Verification: no test.

**FR-19.** The system shall return exit status 0 after a successful analysis.
Source: `src/quality_template/cli.py:94`.
Verification: `test_table_output`, `test_json_output_is_valid`.

### 3.3 Desktop window (`src/quality_template/app.py`)

**FR-20.** The system shall open a window titled `Text Analyser <version>`. Its
initial size is 980×620 and its minimum size 760×480. It has a text input on
the left, and a metrics panel and a word/count table on the right.
Source: `src/quality_template/app.py:31-41,61-125`.
Verification: `tests/test_app.py::TestAnalyserWindow::test_opens_with_the_given_text`.

**FR-21.** The system shall re-analyse the input on every key release. It shall
then show the `format_metrics` values, the top 12 words with stop words
excluded, and the status `<n> words analysed`.
Source: `src/quality_template/app.py:83,127-137`.
Verification: `test_metrics_are_populated`, `test_table_lists_frequent_words`, `test_reanalyses_after_editing`, `test_status_reports_word_count`.

**FR-22.** The system shall, on "Open file...", show a file dialog filtered to
`*.txt *.md`, with an "All files" option. It shall replace the input with the
chosen file read as UTF-8 with replacement, and re-analyse. A cancelled dialog
changes nothing.
Source: `src/quality_template/app.py:122,139-147`.
Verification: no test.

**FR-23.** The system shall, on "Clear", empty the input and re-analyse.
Source: `src/quality_template/app.py:123,149-151`.
Verification: `test_clear_empties_everything`.

### 3.4 Contribution and branch policies

**FR-24.** The system shall classify each branch as one of:

- long-lived: `release`, `dev`, `test`;
- work: `^<code>-\d+/(<branch_types>)/[a-z0-9][a-z0-9-]*$`, with values from `[tool.repo-quality]`;
- stray: anything else.

It shall exit 1 if any branch is stray or a long-lived branch is missing. With
`--remote R`, it shall judge which branches exist from `git ls-remote --heads R`.
Source: `scripts/enforce_branch_policy.py:37-55,136-182`.
Verification: no test; local report run on 2026-11-18 exited 1 with a stray branch named.

**FR-25.** The system shall list local work branches whose tip is already an
ancestor of a local `release`, `dev` or `test`. With `--delete-extra` it shall
delete, with `git branch -d`, every local work or stray branch whose tip is
such an ancestor; branches holding unmerged commits are kept and named.
Source: `scripts/enforce_branch_policy.py:84-124,164-175`.
Verification: no test.

**FR-26.** The system shall reject a branch name that is neither long-lived nor
matches the work-branch pattern. It reads the branch name from `--branch`, then
`GITHUB_HEAD_REF`, then `GITHUB_REF_NAME`, then `git rev-parse`.
Source: `scripts/enforce_contribution_policy.py:60-70,88-103,148`.
Verification: no test; `--branch rqt-1/feat/x --skip-commits` exited 0 and `--branch dependabot/pip/ruff-0.17 --skip-commits` exited 1 on 2026-11-18.

**FR-27.** The system shall check each non-merge commit in
`origin/<base>..HEAD` (falling back to `<base>..HEAD`; base defaults to `dev`).
Each commit must satisfy all of:

- the subject matches `<type>(<scope>): <text>`, with optional scope and types/scopes from `[tool.repo-quality]`;
- the subject is at most 72 characters;
- the subject does not end with `.`;
- the body contains `Signed-off-by:`.

Source: `scripts/enforce_contribution_policy.py:39,73-85,106-126`.
Verification: no test.

**FR-28.** The system shall require the pull-request body, given with
`--pr-body-file`, to contain `closes|fixes|resolves #<n>` (case-insensitive).
Source: `scripts/enforce_contribution_policy.py:129-136,163-165`.
Verification: no test.

**FR-29.** The system shall exit 1 with a list of all problems when any
contribution rule fails. It shall also exit, with a message, when
`pyproject.toml` has no `[tool.repo-quality]` section.
Source: `scripts/enforce_contribution_policy.py:42-48,167-175`.
Verification: no test.

### 3.5 Local pre-push check (`scripts/check_before_push.py`)

**FR-30.** The system shall extract every `ruff`, `mypy` and `pytest`
invocation from `.github/workflows/*.y*ml`. Before matching, it removes the
prefixes `uv run`, `poetry run`, `python -m`, `python3 -m`, `py -m`, `xvfb-run -a`
and `xvfb-run`, and takes only the first command of a chain.
Source: `scripts/check_before_push.py:44-63,87-123`.
Verification: no test.

**FR-31.** The system shall run each extracted command locally, as the console
script next to the interpreter, or on `PATH`, or as `python [-P] -m`. It skips
tools that are not installed, and drops `--cov*` flags when pytest-cov is
missing.
Source: `scripts/check_before_push.py:126-136,206-242`.
Verification: no test.

**FR-32.** The system shall treat pytest exit code 5 (no tests collected) as a
failure. It shall report a pytest failure as "skip" only when the output shows
a cause that the CI install step removes: a module not found during collection,
a missing optional extra, or zero coverage. It shall exit 1 if any check
failed and 0 otherwise, naming the checks that did not run.
Source: `scripts/check_before_push.py:75,181-203,245-277,300-324`.
Verification: no test.

**FR-33.** The system shall, with `--install-hook`, write `.git/hooks/pre-push`.
The hook runs this script with `--quiet`.
Source: `scripts/check_before_push.py:35-40,280-297`.
Verification: no test.

### 3.6 Quality, packaging and SBOM

**FR-34.** The system shall compute four scores from 0 to 100:

- Functional suitability = test pass rate;
- Reliability = coverage percent;
- Maintainability = mean radon maintainability index − 2 × min(ruff findings, 20), clamped to 0..100;
- Portability = 25 × CI operating systems + 25 × CI Python versions, capped at 100.

The overall score is their mean.
Source: `scripts/collect_quality_metrics.py:55-159,180`.
Verification: no test (CI job `quality`).

**FR-35.** The system shall write the metrics report as JSON with `--output`,
and exit 1 when the overall score is below `--fail-under`.
Source: `scripts/collect_quality_metrics.py:162-210`.
Verification: no test.

**FR-36.** The system shall build the release artefact as follows:

1. delete and recreate `release/`;
2. build `text-analyser[.exe]` with PyInstaller (`--onefile --windowed`, entry `app.py`);
3. zip it together with `README.md`, `LICENSE` and `CHANGELOG.md` as `text-analyser-<version>-<system>-<machine>.zip`;
4. write a `<file>.sha256` beside the executable and beside the zip.

It shall exit with install instructions when PyInstaller is not importable.
Source: `scripts/build_release_artifact.py:25-133`.
Verification: no test (release workflow).

**FR-37.** The system shall generate a CycloneDX 1.5 JSON SBOM. The SBOM has
one `library` component per `name==version` line of `requirements-dev.lock`,
with a `pkg:pypi` purl. Its metadata holds the project name, version and
description from `pyproject.toml` and the git `HEAD` revision. The default
output is `dist/sbom.json`; the script prints the component count and the
SHA-256.
Source: `scripts/generate_sbom.py:35-119`.
Verification: no test.

**FR-38.** The system shall profile `analyse_text` + `top_words(…, 20)` over
`--paragraphs` (default 500) × `--repeats` (default 5). It shall print
`--rows` (default 15) lines sorted by `--sort` (`cumtime`, `tottime` or
`ncalls`), and optionally save the pstats data with `--save`.
Source: `scripts/profile_application.py:31-61`.
Verification: no test.

**FR-39.** The system shall install the project in one of four modes:

- default: `pip install -e .`;
- `--dev`: `pip install -e .[dev]`;
- `--from-lock`: the lock file, then `pip install -e . --no-deps`; exits 1 when the lock is missing;
- `--lock`: regenerates `requirements-dev.lock` in a temporary virtual environment from `.[dev,release]`, excluding the project itself.

Source: `scripts/install_dependencies.py:30-104`.
Verification: no test.

### 3.7 Layout transfer, screenshots, workflow audit, CI/CD

**FR-40.** The system shall copy 26 infrastructure files and 4 skeleton
documents into `--target`. Existing files are skipped unless `--force` is
given, and nothing is written unless `--apply` is given. Afterwards it prints
a 24-point compliance report and a list of manual steps.
Source: `scripts/apply_template_to_repo.py:25-92,95-172`.
Verification: no test.

**FR-41.** The system shall regenerate `docs/screenshots/cli-output.png` from
the real CLI output (`docs/sample.txt -n 8`, rendered by rich and Playwright).
It shall regenerate `docs/screenshots/application-window.png` with
`PrintWindow` on Windows, and skip that capture on other platforms. It exits 1
when a capture fails.
Source: `scripts/capture_usage_screenshots.py:128-231`.
Verification: no test.

**FR-42.** The system shall scan the bare repositories in
`scripts/_secret_scan/*.git` for four hazards:

- outdated or dead actions;
- tools invoked but not declared;
- `uv sync` without `pyproject.toml`;
- triggers on branches that do not exist.

When it finds hazards, it shall write them to `scripts/workflow_hazards.json`.
With none, including when `scripts/_secret_scan/` does not exist, it prints
"no hazards found", exits 0 and writes nothing (run on 2026-11-18 on this clone:
"scanned 0 repositories").
Source: `scripts/audit_workflow_hazards.py:26-207`.
Verification: no test.

**FR-43.** The CI workflow shall run on push to `release`, `dev`, `test` and
`*-*/**`, and on pull requests into `release`, `dev` and `test`. Its jobs are:

- lint: ruff check, ruff format check, mypy;
- tests on {Ubuntu, Windows} × {3.10, 3.12};
- a coverage gate;
- a gitleaks scan of the full history;
- ISO 25010 metrics with `--fail-under 70`;
- benchmarks.

Source: `.github/workflows/ci.yml:5-143`.
Verification: no test (CI run status not checked).

**FR-44.** The branch-policy workflow shall run `enforce_branch_policy.py
--remote origin` on every push and pull request, on Mondays at 06:00 UTC, and
on manual dispatch.
Source: `.github/workflows/branch-policy.yml:6-28`.
Verification: no test.

**FR-45.** The contribution-policy workflow shall run on pull requests into
`release`, `dev` and `test` (opened, reopened, edited, synchronize). It passes
the PR body through an environment variable into a file.
Source: `.github/workflows/contribution-policy.yml:12-50`.
Verification: no test.

**FR-46.** The release workflow shall run on tags `v*.*.*`. On Windows and
Ubuntu it runs the tests and builds the artefact. For tag refs only, it
generates `release/sbom.json` with a checksum, collects the `*.zip`, `*.exe`
and `*.sha256` files, and publishes a GitHub Release whose body is
`CHANGELOG.md`.
Source: `.github/workflows/release.yml:5-85`.
Verification: no test.

**FR-47.** The repository shall request weekly (Monday) Dependabot updates for
pip and for GitHub Actions, with at most 5 open PRs each and commit prefixes
`build` and `ci`.
Source: `.github/dependabot.yml:4-26`.
Verification: no test.

### 3.8 Declared but not implemented

| Claim | Where | What the code does |
| --- | --- | --- |
| `apply_template_to_repo.py … --dry-run` | `README.md:189`, `scripts/apply_template_to_repo.py:3` | There is no such option. argparse exits 2 with "unrecognized arguments: --dry-run" (run on 2026-11-18). A dry run is the default without `--apply` (`:125,132`) |
| `--skip-exe`: "package sources only" | `scripts/build_release_artifact.py:105-109` | No files are produced: the zip and checksums are made only from the executable (`:116-128`; read, not run) |
| Manual release run with input `version` | `.github/workflows/release.yml:9-12` | The input is never referenced; the build uses `github.ref_name` (`:46`) |
| "the screenshot step in CI" | `src/quality_template/app.py:3-4` | No workflow runs `capture_usage_screenshots.py` |
| Screenshots "cannot go stale silently" | `README.md:24-25` | Regeneration is manual; nothing checks for staleness |
| "a non-positive `--top` is rejected explicitly" | `docs/quality-iso25010.md:65` | `-n 0` ends in an uncaught `ValueError` traceback, exit 1 (run on 2026-11-18) |
| `.env.example` "carries names only" | `docs/quality-iso25010.md:89`, `SECURITY.md:31` | No `.env.example` is tracked |
| "Tags are signed — `git tag -s`" | `docs/decisions.md:97` | Tags `v1.0.0` and `v1.0.1` carry no signature, and `v1.1.0` is a lightweight tag (`git cat-file`). `README.md:178` uses `git tag -a` |
| README sample output for `docs/sample.txt` | `README.md:49-80` | The CLI prints different numbers for that file (176 characters, 32 words, 2 sentences) |
| Open OpenSSF items: `release_notes_vulns`, `know_secure_design`, `know_common_errors` | `docs/decisions.md:106-119` | Named by the author as not done |

## 4. Interfaces

### 4.1 Command line: `quality-template` (`pyproject.toml:33-34`)

| Argument | Type | Default | Effect | Source |
| --- | --- | --- | --- | --- |
| `path` | file path, optional | stdin | input text | `cli.py:19-21` |
| `-n`, `--top` | int | 10 | number of frequent words | `cli.py:22-24` |
| `--keep-stop-words` | flag | off | keep stop words | `cli.py:25-27` |
| `--json` | flag | off | JSON output | `cli.py:28-30` |
| `--gui` | flag | off | open the window | `cli.py:31-33` |
| `--version` | flag | — | print the version, exit 0 | `cli.py:34` |

Exit status:

| Status | When | Source |
| --- | --- | --- |
| 0 | success | `cli.py:94` |
| 1 | `error: no such file: <path>` | `cli.py:41-42` |
| 1 | `-n` ≤ 0: uncaught `ValueError` with a traceback | `core.py:164-165` |
| 2 | malformed arguments (argparse default; observed on 2026-11-18 with an unknown flag) | — |

### 4.2 JSON output (`src/quality_template/cli.py:76-87`)

| Key | Type | Notes |
| --- | --- | --- |
| `characters` | int | `len(text)` |
| `words` | int | token count |
| `unique_words` | int | distinct tokens |
| `sentences` | int | FR-2 |
| `average_word_length` | float | rounded to 4 decimals |
| `lexical_diversity` | float | rounded to 4 decimals |
| `longest_word` | string | `""` when there are no tokens |
| `top_words` | array of `{"word": str, "count": int}` | FR-8, FR-15, FR-16 |

### 4.3 Python API

| Symbol | Signature | Source |
| --- | --- | --- |
| `analyse_text` | `(text: str) -> TextStats` | `core.py:110` |
| `top_words` | `(stats, limit=10, *, drop_stop_words=True) -> list[tuple[str, int]]` | `core.py:151-153` |
| `tokenise` | `(text: str) -> list[str]` | `core.py:88` |
| `count_sentences` | `(text: str) -> int` | `core.py:97` |
| `format_metrics` | `(stats) -> dict[str, str]` | `core.py:134` |
| `cli.main` | `(argv: list[str] \| None = None) -> int` | `cli.py:64` |
| `app.run_app` | `(path: Path \| None = None) -> int` | `app.py:154` |
| `app.AnalyserWindow` | `(initial: str = SAMPLE)` | `app.py:28-31` |

The package's `__all__` lists `TextStats`, `analyse_text` and `top_words`;
`__version__` is defined beside it (`src/quality_template/__init__.py:8-11`).

### 4.4 Script command lines

| Script | Options | Source |
| --- | --- | --- |
| `install_dependencies.py` | `--dev`, `--lock`, `--from-lock` | `:73-86` |
| `check_before_push.py` | `--install-hook`, `--quiet` | `:327-331` |
| `enforce_branch_policy.py` | `--remote R`, `--delete-extra` | `:136-142` |
| `enforce_contribution_policy.py` | `--base B` (default `dev`), `--branch`, `--pr-body-file`, `--skip-commits` | `:139-145` |
| `collect_quality_metrics.py` | `--output PATH`, `--fail-under N` | `:162-171` |
| `build_release_artifact.py` | `--version` (default `v0.0.0-dev`), `--skip-exe` | `:100-110` |
| `generate_sbom.py` | `--output` (default `dist/sbom.json`) | `:102-105` |
| `profile_application.py` | `--paragraphs`, `--repeats`, `--rows`, `--sort`, `--save` | `:38-45` |
| `apply_template_to_repo.py` | `--target` (required), `--apply`, `--force` | `:122-127` |
| `capture_usage_screenshots.py` | `--skip-gui`, `--skip-cli` | `:202-206` |
| `audit_workflow_hazards.py` | none | `:185-208` |

### 4.5 CI workflow triggers

| Workflow | Triggers | Permissions | Source |
| --- | --- | --- | --- |
| `ci.yml` | push to `release`, `dev`, `test`, `*-*/**`; PR into `release`, `dev`, `test`; manual | `contents: read` | `ci.yml:5-13` |
| `branch-policy.yml` | push, pull_request, cron `0 6 * * 1`, manual | `contents: read` | `branch-policy.yml:6-14` |
| `contribution-policy.yml` | PR opened/reopened/edited/synchronize into `release`, `dev`, `test` | `contents: read` | `contribution-policy.yml:12-18` |
| `release.yml` | tag `v*.*.*`; manual with input `version` | `contents: write` | `release.yml:5-15` |

### 4.6 Files produced or consumed

| File | Format | Producer / consumer | Source |
| --- | --- | --- | --- |
| `requirements-dev.lock` | `#` comments + `name==version` lines | `install_dependencies.py --lock` / CI, `generate_sbom.py` | `install_dependencies.py:58-69`, `generate_sbom.py:35,54-65` |
| `dist/sbom.json`, `release/sbom.json` | CycloneDX 1.5 JSON | `generate_sbom.py` | `generate_sbom.py:78-99` |
| `quality-report.json` | JSON: `standard`, `measured_characteristics`, `assessed_by_hand`, `overall_measured_score`, `note` | `collect_quality_metrics.py` | `:182-194` |
| `release/text-analyser[.exe]`, `release/*.zip`, `release/*.sha256` | binary, zip, `<hex>  <name>` lines | `build_release_artifact.py` | `:81-97,125-128` |
| `coverage.xml`, `benchmark.json` | coverage XML, pytest-benchmark JSON | CI jobs, uploaded as artifacts | `ci.yml:90-94,139-143` |
| `.git/hooks/pre-push` | `/bin/sh` script | `check_before_push.py --install-hook` | `:35-40,280-297` |
| `docs/screenshots/*.png` | PNG | `capture_usage_screenshots.py` | `:36,212-229` |
| `scripts/workflow_hazards.json` | JSON list of `{repo, file, kind, detail}` | `audit_workflow_hazards.py` | `:80-81,204-206` |
| `pr-body.txt` | text | contribution-policy workflow | `contribution-policy.yml:39-44` |

## 5. Data

| Entity | Fields | Storage | Source |
| --- | --- | --- | --- |
| `TextStats` (frozen dataclass) | `characters: int`, `words: int`, `unique_words: int`, `sentences: int`, `average_word_length: float`, `longest_word: str`, `frequencies: Counter[str]`; property `lexical_diversity: float` | memory only | `core.py:64-85` |
| `STOP_WORDS` | 39 lower-case English function words (frozenset) | constant | `core.py:19-61` |
| `[tool.repo-quality]` | `code`, `long_lived_branches`, `branch_types`, `commit_types`, `commit_scopes` | `pyproject.toml:86-97` | read by the policy scripts |
| Metric | `characteristic`, `score`, plus evidence keys per characteristic | memory, optional JSON | `collect_quality_metrics.py:32,55-159` |

The application persists nothing. Input text is held in memory as one string
(`cli.py:43`, `app.py:128`).

## 6. Non-functional requirements

**NFR-1 (platform).** The package shall run on CPython 3.10 or newer. CI tests
3.10 and 3.12 on Ubuntu and Windows; macOS is not tested.
Source: `pyproject.toml:10`, `.github/workflows/ci.yml:44-45`, `docs/quality-iso25010.md:119`.

**NFR-2 (dependencies).** The package shall have no third-party runtime
dependencies. The GUI uses only the tkinter that ships with CPython.
Source: `pyproject.toml:19`, `src/quality_template/app.py:1-5`.

**NFR-3 (coverage).** Coverage of `src/`, statements and branches together
(`branch = true`), shall be at least 85 %. The CI
`coverage` job enforces it; the test matrix disables the threshold.
Source: `pyproject.toml:115-123`, `.github/workflows/ci.yml:64-90`.

**NFR-4 (static checks).** Code shall pass:

- ruff with rule sets E, W, F, I, UP, B, SIM, C90, S and RUF, with `S101` ignored;
- cyclomatic complexity of at most 10;
- line length of at most 100;
- `ruff format`;
- strict mypy over `src/`.

Source: `pyproject.toml:45-80,102-106`, `.github/workflows/ci.yml:31-36`.

**NFR-5 (quality score).** The mean of the four measured ISO 25010 scores shall
be at least 70 in CI.
Source: `.github/workflows/ci.yml:122`.

**NFR-6 (secrets).** Credentials shall be blocked by:

- gitleaks in pre-commit;
- gitleaks over the full git history in CI;
- the pre-commit hook `detect-private-key`;
- `.gitignore` entries for `.env` and `*.env`.

Source: `.pre-commit-config.yaml:14,25-28`, `.github/workflows/ci.yml:96-106`, `.gitignore:1-4`.

**NFR-7 (file size).** pre-commit shall reject added files larger than 2048 KB.
Source: `.pre-commit-config.yaml:12-13`.

**NFR-8 (least privilege in CI).** The CI, branch-policy and
contribution-policy workflows shall have `contents: read`; only the release
workflow has `contents: write`. The PR body shall reach the shell through an
environment variable, not through expression interpolation.
Source: `ci.yml:12-13`, `branch-policy.yml:13-14`, `contribution-policy.yml:17-18,39-44`, `release.yml:14-15`.

**NFR-9 (concurrency).** A newer CI run on the same ref, and a newer
contribution check on the same PR, shall cancel the run in progress.
Source: `ci.yml:15-17`, `contribution-policy.yml:20-22`.

**NFR-10 (artefact integrity).** Every release file, including the SBOM, shall
be published with a SHA-256 file.
Source: `scripts/build_release_artifact.py:125-128`, `.github/workflows/release.yml:77`.

**NFR-11 (reproducible tool versions).** CI shall install the exact versions
in `requirements-dev.lock`.
Source: `.github/workflows/ci.yml:30,53,86,118,137`.

**NFR-12 (input decoding).** File input shall be decoded as UTF-8, with
undecodable bytes replaced rather than raising an error.
Source: `src/quality_template/cli.py:43`, `src/quality_template/app.py:146,156`.

**NFR-13 (timeouts).** The only timeouts in the scripts are in the screenshot
capture: it waits up to 25 s for the window and up to 20 s for `taskkill`.
`check_before_push.py`, the policy scripts and the metrics script set no
timeout on their subprocesses.
Source: `scripts/capture_usage_screenshots.py:138,151`; `subprocess.run` calls in the other scripts.

**NFR-14 (performance).** No timing threshold is enforced. The benchmarks
assert only that the results are correct (`benchmarks/test_performance.py:26-44`).
The CI job publishes `benchmark.json` and does not compare it with a baseline
(`ci.yml:139`). `README.md:126-134` lists measured medians without naming the
machine.

## 7. Constraints and dependencies

| Kind | Name | Version | Source |
| --- | --- | --- | --- |
| Build backend | setuptools, wheel | `setuptools>=68` | `pyproject.toml:1-3` |
| Dev extras | pytest, pytest-cov, pytest-benchmark, ruff, mypy, radon, pre-commit | `>=8.0`, `>=5.0`, `>=4.0`, `>=0.6`, `>=1.11`, `>=6.0`, `>=3.7` | `pyproject.toml:22-30` |
| Release extra | pyinstaller | `>=6.0` | `pyproject.toml:31` |
| Lock (33 pins) | pytest 9.1.1, pytest-cov 7.1.0, pytest-benchmark 5.2.3, coverage 7.15.2, ruff 0.16.1, mypy 1.18.2, radon 6.0.1, pre_commit 4.6.1, pyinstaller 6.21.0, setuptools 83.0.0, … | exact | `requirements-dev.lock:4-36` |
| pre-commit hooks | pre-commit-hooks, ruff-pre-commit, gitleaks | `v4.6.0`, `v0.6.9`, `v8.21.2` | `.pre-commit-config.yaml:5,17,26` |
| GitHub Actions | `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, `gitleaks/gitleaks-action@v2`, `softprops/action-gh-release@v2` | major tags | `.github/workflows/*.yml` |
| Screenshot tooling (undeclared) | pywin32, Pillow, playwright, rich | none pinned | `scripts/capture_usage_screenshots.py:57,83-86,158-160` |
| Scripts using `tomllib` | Python 3.11 or newer | — | `scripts/enforce_branch_policy.py:32`, `scripts/enforce_contribution_policy.py:32-35`, `scripts/generate_sbom.py:27` |
| Licence | MIT | — | `LICENSE`, `pyproject.toml:11` |

Constraint (inference): the ruff hook in pre-commit (`v0.6.9`) and the ruff in
the lock (`0.16.1`) are different versions, so local formatting and CI can
disagree.

## 8. Acceptance

Automated, in the commands the repository uses:

| Check | Command | Source | Status on 2026-11-18 |
| --- | --- | --- | --- |
| Unit tests (FR-1…FR-17, FR-19…FR-21, FR-23) | `pytest` | `CONTRIBUTING.md:44` | core + CLI: 33 passed; `tests/test_app.py` not run |
| Coverage ≥ 85 % (NFR-3) | `pytest --cov` | `README.md:113` | not run (pytest-cov absent) |
| Lint, format, types (NFR-4) | `ruff check . && ruff format --check .`, `python -m mypy` | `ci.yml:32-36` | not run |
| Benchmarks | `pytest benchmarks --benchmark-only` | `README.md:143` | 5 collected, not run |
| Quality score ≥ 70 (NFR-5) | `python scripts/collect_quality_metrics.py --fail-under 70` | `ci.yml:122` | not run |
| Everything CI runs, locally | `python scripts/check_before_push.py` | `CONTRIBUTING.md:38` | not run |
| Contribution policy (FR-26…FR-29) | `python scripts/enforce_contribution_policy.py --base dev` | `contribution-policy.yml:48-50` | branch-name part run (see FR-26) |
| Branch policy (FR-24, FR-25) | `python scripts/enforce_branch_policy.py --remote origin` | `branch-policy.yml:28` | local mode only |

Manual checks for requirements that have no test:

- FR-18, FR-22: `quality-template --gui` opens "Text Analyser 1.0.0" with the
  sample text. "Open file..." loads a `.txt` file, the metrics change, and
  cancelling leaves the text unchanged.
- FR-36, FR-46: `python scripts/build_release_artifact.py --version v0.0.0-test`
  leaves an executable, a zip and two `.sha256` files under `release/`, and
  `sha256sum -c` passes for each of them.
- FR-37: `python scripts/generate_sbom.py` writes `dist/sbom.json`, and its
  component count equals the number of pins in `requirements-dev.lock` (33).
- FR-40: `python scripts/apply_template_to_repo.py --target <empty git repo>`
  prints "DRY RUN - nothing written" and leaves the target unchanged.

## 9. Open questions

1. Who the intended users of the Text Analyser and of the layout are, beyond
   "something concrete to act on" (`src/quality_template/__init__.py:1-6`).
2. Which branch is canonical. `origin/release` contains all of `d74be72` plus
   21 further commits that move `.github/` under `template/`, add `recipe.ps1`
   and `uv.lock` and delete `requirements-dev.lock`. Is `dev` going to be
   brought up to date, or is it abandoned? This specification covers `d74be72`
   only.
3. Which version `d74be72` represents. Code and `pyproject.toml` say `1.0.0`,
   tag `v1.0.1` is in its history, and `CHANGELOG.md` has no 1.0.1 entry.
4. Whether the release `.exe` is meant to include the CLI. It is built
   `--windowed` from `app.py` (inference: GUI only).
5. Whether bot branches (Dependabot) are meant to pass the branch and
   contribution policies. At `d74be72` they do not; the fix sits unmerged on
   `origin/rqt-7/fix/branch-classification`.
6. Which Python runs `generate_sbom.py` in the release `publish` job. That job
   has no `setup-python` step (`release.yml:53-70`), and the script needs 3.11
   or newer for `tomllib`.
7. Whether the pinned lock installs on Python 3.10, which the test matrix uses.
   Evidence in the lock: it holds `colorama`, `pefile` and `pywin32-ctypes` and
   has no `tomli` or `exceptiongroup`, so it was resolved on Windows under
   Python 3.11 or newer (inference). Whether every pin supports 3.10 was not
   checked offline.
8. The branch-protection settings that `docs/branching.md:76-77` and
   `docs/decisions.md:38` rely on (required checks, required review). They live
   in GitHub settings, not in the repository.
9. Target performance and memory limits. The README medians name no machine,
   and the "roughly a hundred megabytes" limit (`docs/architecture.md:61-63`)
   is not measured.
10. Where the `scripts/_secret_scan/*.git` mirrors used by
    `audit_workflow_hazards.py` come from.
11. Whether the Linux release executable is meant to be published on its own.
    The publish job copies only `*.zip`, `*.exe` and `*.sha256`
    (`release.yml:75`), so the bare Linux binary ships only inside its zip,
    while its separate `.sha256` is published (inference from the code).
12. Whether accessibility work is planned. The author calls it the weakest
    area (`docs/quality-iso25010.md:67`).
