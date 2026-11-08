# `repo-quality-template` against `BEST_REQUIREMENTS.md` revision 4.0.0

A gap report, written 2026-10-05. The subject is this repository; the yardstick
is revision **4.0.0** of `additive-lab`'s `BEST_REQUIREMENTS.md` — 6138 lines,
42 rules `R-01`…`R-42`, dated 2026-09-26.

Nothing here has been applied. Every number below was read out of the files it
describes, not out of the document that claims it.

---

## 0. The headline

`docs/standards-comparison.md` compares this repository against
**revision 2.0.0** — it describes the other document as *"2214 lines, 36
numbered rules R-01…R-36, 23 required files"*. The current revision is 4.0.0.
That alone would be ordinary staleness. The problem is that the same file is
also **wrong about this repository**, in the one document a reader is sent to
by `README.md:210` to find out what the standard is.

| `docs/standards-comparison.md` | claims | actually | checked by |
| --- | ---: | ---: | --- |
| `:3`, `:18`, `:146` | 14 points | **24** | `grep -c '^    ("' scripts/apply_template_to_repo.py` → 24; `README.md:196,210`; `CHANGELOG.md:43` |
| `:18` | 35 files | **50** | `git ls-files \| wc -l` |
| `:18` | 3 GitHub workflows | **4** | `ls .github/workflows/` |
| `:65` | "C does not produce an SBOM" | it does | `release.yml:70`, `:77` |
| `:102` | no dependency monitoring | there is | `.github/dependabot.yml` |
| `:103` | tags not signed | documented as signed | `docs/branching.md:104`, `docs/workflow.md:136` |
| `:107` | no code of conduct | there is one | `CODE_OF_CONDUCT.md` |
| `:146` | "C's fourteen points do not mention [mypy]" | point 19 *is* type checking | `apply_template_to_repo.py:88`, `pyproject.toml:107-111`, `ci.yml:36` |

Eleven false lines, four of them about this repository. This is the exact
failure `R-34`/`R-35` exist to prevent, and it is the strongest argument in the
report for the ideas in §3.

**One finding is no longer a finding.** `:120-126` reports a committed 40-hex
Gitea token as a defect — a breach of that document's own `R-02`. In 4.0.0,
`R-02` is **reversed**: keys now live in `.claude/.env`, *committed on purpose*,
and §17 records the decision. The paragraph must be rewritten as a divergence
between two defensible positions, not left standing as a bug report. (In the
copy received, the line is redacted and a 40-hex scan over all 6138 lines
returns nothing.)

---

## 1. Defects in this repository, found while comparing

These are not imports. They are things already broken or already contradictory,
surfaced by holding the two documents side by side. Ranked by cost of being
wrong.

### 1.1 `check_before_push.py` says "all clear - safe to push" while skipping four CI jobs

The script discovers what CI runs by reading `.github/workflows/*` as text, and
`_command_on()` only recognises a token in `TOOLS = ("ruff", "mypy", "pytest")`.
Every `python scripts/*.py` step is dropped **in silence**:

| CI job / step | mirrored locally |
| --- | --- |
| `ci.yml` → `lint`, `test`, `coverage`, `benchmark` | yes |
| `ci.yml` → `security` (gitleaks, full history) | **no** |
| `ci.yml` → `quality` (`collect_quality_metrics.py --fail-under 70`) | **no** |
| `branch-policy.yml:28` (runs on every push) | **no** |
| `contribution-policy.yml:48` | **no** — and `:9` promises *"Everything here also runs locally"* |

A live run prints `all clear - safe to push` having verified two of six `ci.yml`
jobs and neither policy workflow. Per the workspace rule — *a check that is
easier than the one it mirrors is worse than no check* — this is the most
expensive defect in the repository, because it is the one that says "safe".

The machinery for an honest partial verdict already exists at
`check_before_push.py:300-324` (`verdict_of` refuses to print "all clear" when
checks were skipped). It is simply not being fed. Add a `REPO_SCRIPTS` tuple
beside `TOOLS`, match it in `_command_on`, pass CI's own flags through, and let
anything genuinely unrunnable land in the existing `skipped` list.

Two smaller faults in the same file: only the first command of an `&&` chain is
read (`:95`), and `git` is probed at `:363-364` with the result discarded.

### 1.2 Two "NOT CHECKED" paths return 0

`check_before_push.py:309-310` and `:338-342` both print an honest message and
then `return 0`. The pre-push hook reads only the exit code, so a clone where
no tool is importable gets a green gate having run nothing. 4.0.0's `R-28` is
the rule this breaks: *an empty list is a passed list, not a skipped one* — a
gate may pass on a **declared** nothing, never on an **undetermined** one.

Same shape elsewhere:

- `capture_usage_screenshots.py` — the non-Windows GUI skip never sets `failed`,
  so it exits 0 having produced no window screenshot. `README.md:24-25` asserts
  both images *"cannot go stale silently"*; no workflow runs this script, so
  that sentence is currently false.
- `collect_quality_metrics.py:125-127` — `except json.JSONDecodeError:
  violations = 0`. Unparseable ruff output scores as **zero lint debt**,
  inflating the Maintainability figure that `ci.yml:122` gates on. Missing
  input, best-case outcome.

### 1.3 Ruff is unpinned and has already drifted three ways

| file | says |
| --- | --- |
| `pyproject.toml:26` | `ruff>=0.6` |
| `.pre-commit-config.yaml` | `rev: v0.6.9` |
| `requirements-dev.lock:32` | `ruff==0.16.1` |

`[tool.ruff]` carries no `required-version`. Ten minor versions of formatter
changes sit between the commit hook and the runner: pre-commit formats a file
with 0.6.9, then `ci.yml:34` runs `ruff format --check .` under 0.16.1 and fails
on formatting nobody wrote. This is precisely what `R-14` — *drift refuses to
run* — is for.

Also unpinned: `[build-system] requires = ["setuptools>=68", "wheel"]`
(`pyproject.toml:1-3`). A floor and a bare name. `pip install -e .` builds in an
isolated environment that ignores `requirements-dev.lock` entirely.

### 1.4 The release command in the README is unsigned

| file | command |
| --- | --- |
| `README.md:178` | `git tag -a v1.2.0` |
| `docs/branching.md:104` | `git tag -s -a v1.2.0` |
| `docs/workflow.md:136` | `git tag -s -a v1.2.0` |
| `docs/decisions.md:97` | claims tags are signed |

Three documents say signed; the one a person copy-pastes does not. Two
characters.

### 1.5 Nothing checks the tag against the version

`pyproject.toml:7` is `1.0.0`, `src/quality_template/__init__.py:11` is
`1.0.0`, and `release.yml:46` passes `--version "${{ github.ref_name }}"`
which is never compared with either. `git tag v9.9.9` publishes artefacts
named 9.9.9 containing a binary whose `--version` prints 1.0.0.

Worse, `softprops/action-gh-release@v2` **updates an existing release in
place**, and `release.yml` has no `concurrency` block (`ci.yml:15` and
`contribution-policy.yml:20` do). Two tags pushed close together race, and the
loser silently overwrites the winner's assets. 4.0.0's `R-23` guard — *an
existing tag publishes nothing and warns* — is the missing half.

### 1.6 `${{ }}` reaches a shell

`release.yml:46` interpolates `github.ref_name` into a `run:` string in a job
holding `contents: write`. A git ref may legally contain backtick, `$`, `;`,
`"`, `|` and `&`, and `v1.0.0";id;"` matches the `v*.*.*` filter at `:7`.
4.0.0's rule is flat: **values reach a script through `env:`, never through its
text.** `contribution-policy.yml:42-44` already does it correctly, with a
comment explaining why — then `:48-50` does not.

### 1.7 Every release body is the entire changelog

`release.yml:83-84` sets both `generate_release_notes: true` and
`body_path: CHANGELOG.md`. By v1.5.0, the release page for v1.5.0 describes
v1.0.0 through v1.5.0 with no indication of which part is new.

### 1.8 The commit scope is optional in the checker and mandatory in every document

`enforce_contribution_policy.py:114` wraps the scope in `(...)?`, so `feat: x`
passes. `CONTRIBUTING.md:75`, `docs/workflow.md:53` and the script's own
docstring all write `<type>(<scope>): <subject>`. One character.

Same file, `:123`: the sign-off test is `"Signed-off-by:" not in body` — a
substring test. A body reading *"I keep forgetting the Signed-off-by: line"*
passes. `git interpret-trailers --parse` is the correct test.

### 1.9 The rollout manifest cannot deliver three of its own files

`apply_template_to_repo.py` never copies `.gitignore`, `requirements-dev.lock`
or `audit_workflow_hazards.py` — grep for them in `INFRASTRUCTURE`/`SKELETONS`
returns nothing. So `--apply` gives a target ruff config, CI and a pre-commit
hook **and no ignore file**, after which its first `git add -A` commits
`__pycache__/` and `.ruff_cache/` and `ruff format` dirties the tree on every
run forever.

Related: `copy()` returns `"exists, skipped"` for every file the target already
has, so **a repository adopted once never receives a fix**. There is no drift
mode.

### 1.10 `audit_workflow_hazards.py` is run by nothing

Its only mention anywhere is `docs/standards-comparison.md:82`. Grep over
`.github/` finds no workflow that calls it. Its check 1 (a floating action major
gone stale) and check 3 (a workflow watching a branch that does not exist,
which *"reads as no CI rather than CI is broken"*) are drift detectors already
written and never fired. Its `CURRENT_MAJOR` table is dated *"as of 2026-08"*
and is now fourteen months old.

### 1.11 Prose asserting checks that do not exist

- `docs/quality-iso25010.md:97` — *"**Known limit:** no signed commits and no
  SBOM."* The SBOM half is false (`release.yml:70`). The commits half conflates
  DCO sign-off with a cryptographic signature.
- `docs/quality-iso25010.md:28-30` — *"the README documents exactly the flags
  `cli.py` implements … so documentation drift fails the build."* Nothing in
  `tests/` references the README at all.
- `README.md:24-25` — the screenshots *"cannot go stale silently."* No workflow
  regenerates or diffs them.

### 1.12 The documented release procedure contradicts the documented protection

`README.md:177`, `docs/workflow.md:133` and `docs/branching.md:102` all do
`git checkout release && git merge --ff-only test && git push origin release`.
`docs/branching.md:95` instructs *"protect all three in repository settings:
require CI to pass, require pull requests, forbid force-push."* Do step 5 of
that file and the release procedure in all three fails.

### 1.13 `docs/workflow.md:82` recommends a setting that would brick the repo

*"Nothing merges itself: the gate is green checks plus a human clicking"*, with
`.github/CODEOWNERS:3-5` advertising *"Require review from Code Owners"*. There
is one owner. GitHub refuses self-approval, so switching that on produces a
gate nobody can ever pass. 4.0.0 hit this exactly and documented the answer —
*"a whitelist of one is a lock, not a review"* — setting approvals to 0 and
restricting the **merge** instead.

### 1.14 Nothing enforces which branch may be proposed into which

`contribution-policy.yml:15` accepts PRs to `[release, dev, test]` and passes
`--base` through purely as a compare point. A work branch can open a PR straight
into `release` and every check goes green. `docs/workflow.md:7` draws the
intended path and nothing holds it. This is the rule the three-branch model
rests on.

### 1.15 Smaller, verified

- **No `.gitattributes`** at all, with a `[ubuntu-latest, windows-latest]`
  matrix. `check_before_push.py:286-292` already hard-codes `newline="\n"` by
  hand to defend against exactly what the file prevents.
- `.gitignore` is **unanchored** (`build/`, `dist/`, `release/` with no leading
  `/`) and **omits `.mypy_cache/`** — present in the tree right now, ignored
  only because mypy writes its own `.mypy_cache/.gitignore`. Verified:
  `git check-ignore -v .mypy_cache/` answers `.mypy_cache/.gitignore:2`.
- **No `CLAUDE.md`**, and no `.claude/` — see §3.5.
- **No `schedule:` in `ci.yml`.** The only cron in the repository is
  `branch-policy.yml:10`.
- **`branch-policy.yml` reports but never sweeps.** `:28` runs
  `enforce_branch_policy.py --remote origin` — report only. Worse, the
  stale-branch list reads `work_local`, and the script's own comment at `:176`
  says *"A CI checkout creates exactly one local branch"* — so in CI that list
  is structurally empty. `--delete-extra` only ever touches local branches.
  Right now `origin/rqt-1/...` and `origin/rqt-5/...` are both merged and still
  there.
- **`.env.example` is asserted by two files and does not exist.**
  `SECURITY.md:31` requires it, `.gitignore:4` un-ignores it,
  `docs/quality-iso25010.md:89` cites it as an existing control.
- **No `hotfix` or `experiment` in `branch_types`** (`pyproject.toml:94-97`),
  while `docs/branching.md:14` draws a hotfix arrow. `rqt-9/hotfix/crash` fails
  CI today.
- **Eight public symbols have no docstring**: `cli.py:14,38,46,64` and
  `app.py:127,139,149,154`. `core.py` is 7 of 7. Ruff's `D` ruleset is not
  selected.
- **`git config user.name/email` is never checked**, while sign-off is hard
  required — a guaranteed first-run failure for a fresh clone.
- **`.git/hooks/` in this clone has a `pre-push` and no `pre-commit`**, so
  `.pre-commit-config.yaml` — ruff, ruff-format, gitleaks — is not running
  here, despite `CONTRIBUTING.md:12-13` calling it *"not optional"*.
  `default_install_hook_types` is the fix.

---

## 2. The one number worth re-reading: the benchmark table

`README.md:126-140` publishes five medians as measured fact. `.gitignore:34`
ignores `benchmark.json`, so the repository holds **no source at all** for
them. Against the newest local `benchmark.json`:

| `README.md` | says | measured | drift |
| --- | ---: | ---: | ---: |
| `:130` `top_words` | 3.8 µs | 3.50 µs | +8.6 % |
| `:131` `analyse_text`, 1 para | 20.4 µs | 18.50 µs | +10.3 % |
| `:132` `analyse_text`, 50 para | 836.4 µs | 759.0 µs | +10.2 % |
| `:133` `tokenise`, 500 para | 5.92 ms | 5.26 ms | +12.5 % |
| `:134` `analyse_text`, 500 para | 8.37 ms | 7.47 ms | +12.0 % |
| `:139` "Tokenising is 71 % of the total" | 71 % | 70.4 % | — |

Every figure is stale in the same direction by roughly the same amount, which
is what a faster runner looks like. The claim is not wrong by much; it is wrong
by construction, because nothing ties it to a source.

---

## 3. Worth importing from 4.0.0

Ranked by value per unit of work. Each names the rule, what this repository has
instead, and the file to add or edit.

### 3.1 A version for this standard, and one README line that states it — `R-42`

**The single highest-value import.** 4.0.0 requires that a complying
repository say, in one README line, which revision it meets, **linking that
revision's tag**, with partial compliance written as `except R-nn (#issue)`.

This repository states no version of its own standard at all. Across ~109
repositories, *"is this one compliant?"* is therefore unanswerable — and `§0`
above is what that costs.

- the version lives in `pyproject.toml`, `[tool.repo-quality]` (line 86, beside
  `code = "rqt"`), as `standard_version = "1.0.0"`;
- the 24 points need a versioned home. **There is no human-readable list of
  them anywhere** — `grep "1\. CI/CD" **/*.md` finds nothing; the only
  enumeration is a Python literal at `apply_template_to_repo.py:69-94`. Add
  `docs/standard.md`, points numbered `P-01`…`P-24` so they can be cited the
  way `R-nn` is, with a revision table at the bottom;
- the README line, replacing `README.md:208-214`:

  ```markdown
  This repository complies with [revision 1.0.0](https://github.com/IGORSVOLOHOVS/repo-quality-template/blob/v1.0.0/docs/standard.md) of the repo-quality standard, except P-11 (#34).
  ```

  Link the **tag**, never a branch — a line that links `release` claims
  whatever the document says tomorrow;
- `apply_template_to_repo.py` prints that line for a target to paste, with
  `except P-nn` auto-filled from every point it reported `NO`. It already
  computes that list at `:165-177` and throws it away;
- and a check, because otherwise the import arrives with 4.0.0's own `—`
  against it: grep the README for the line, compare its revision against
  `standard_version`, require every `except P-nn` to carry a `(#issue)`.
  ~15 lines in `enforce_contribution_policy.py`.

### 3.2 The "checked by" column — `§16`

Every rule in 4.0.0 names the mechanism that actually holds it up, **addressed
by workflow step or hook name, never by line number**, and the document states
plainly that twelve of its forty-two rules have nothing.

This repository's audit surface is `README.md:111-122`: ten rows, a binary
*"Enforced in CI: yes/no"*, nine of ten saying yes. It lists **controls**, not
points, so a point with nothing behind it does not appear at all.

Proposed taxonomy (4.0.0's **C** renamed **P**, so it does not collide with
"CI"):

| key | what it means |
| --- | --- |
| **G** | a named step in `ci.yml` / `branch-policy.yml` / `contribution-policy.yml` fails the build |
| **H** | a hook on the machine refuses it — a `.pre-commit-config.yaml` hook id, or `check_before_push.py` |
| **T** | the pinned tool itself refuses — `requires-python`, ruff's `required-version` |
| **P** | GitHub's own settings, invisible in the repository — branch protection, required checks, CODEOWNERS, Dependabot |
| **W** | a workflow does it, or records it, **after** the change landed, and never blocks it |
| **S** | a script a human must choose to run |
| **—** | nothing |

Filled in honestly, **nine of twenty-four points come out at `—`**: 2
(documentation), 4 (architecture), 5 (licence), 10 (install script — no
workflow ever executes `install_dependencies.py`), 11 (screenshots), 12
(English — already admitted at `apply_template_to_repo.py:81`), 22 (security
policy), 23 (code of conduct), 24 (divergences). Three of those nine currently
carry prose asserting a check that does not exist (§1.11). Two more are
partials whose probe is weaker than the point: point 20 only checks that
`generate_sbom.py` *exists*, so deleting the release step leaves it green.

Copy 4.0.0's two rules verbatim with the table: never a line number, and
**adding a check for a point is always a legitimate change; removing the last
check for one needs an issue that says why.**

### 3.3 The recorded override — `R-39`

4.0.0's best idea, and this repository has no equivalent of any kind. An
override phrase on a line of its own plus a mandatory `Why:` line sets a gate
aside; only a declared reviewer may write one; and **every use is listed by the
release pipeline**, which publishes that version as a pre-release and opens an
issue for an override with no `Why:`.

Today a blocked solo maintainer has two options: `git push --no-verify`
(`check_before_push.py:19`, leaves no trace) or untick a box in GitHub settings
(leaves no trace). 4.0.0 is explicit that the phrase *"authenticates
nothing"* — which is the right expectation for a one-person repository. The
value is entirely in the record.

Strip it to its useful half: a `## Bypass` block in
`.github/PULL_REQUEST_TEMPLATE.md` requiring a written reason, and a
`release.yml` step that collects them into the release notes. The full version —
an `issue_comment` workflow reading the phrase from the default branch, posting
an `override/verdict` commit status — is in the appendix of this report's
working notes if it is ever wanted.

### 3.4 Branch protection applied by a script, and read back — `§8`

4.0.0 applies protection with a script that defaults to a dry run, reads the
reviewer list from one place, and then **reads every rule back**, failing when
the server's answer differs from what was sent.

`docs/branching.md:94` is *"protect all three in repository settings"* —
manual clicking. Nothing reads the state back, nothing fails when it drifts,
and `apply_template_to_repo.py:189` still lists it as by-hand. This is
server-side drift that nothing in the repository detects.

`scripts/apply_branch_protection.py`, `gh api`, same two-stage shape. GitHub's
`PUT` is idempotent, so the payload is simpler than 4.0.0's. Two things matter
more here than there:

- `enforce_admins: false` on purpose — the admin's merge past a red check *is*
  the override, and §3.3 is what makes it recorded;
- `required_pull_request_reviews: null` — see §1.13;
- the stage 1 / stage 2 split matters **more** on GitHub: a `contexts` entry
  naming a check that has never reported **blocks the branch forever**, and the
  UI gives no reason.

Then run it in dry-run mode from the weekly job, so a hand-edited setting is
reported rather than discovered.

### 3.5 One stable aggregate check as the required context

Not from 4.0.0 directly — it is the GitHub-specific hazard that 4.0.0's
*"Where Gitea is not GitHub"* subsection implies. This repository's CI jobs
expand through a matrix into context strings like
`Tests (ubuntu-latest, Python 3.12)`. Adding Python 3.13 adds a context nothing
requires; renaming `Coverage gate` silently un-requires it and the branch is
unprotected with no signal.

A single `gate` job with `needs: [lint, test, coverage, security, quality,
benchmark]` and `if: always()`, failing when any `needs.*.result != 'success'`,
becomes the one required context forever. Cheapest change in the report and
every item above hangs off it.

**Related trap, worth writing down:** `release.yml:59` and `ci.yml:111` both
produce a **skipped** check-run when their condition is false, and GitHub
treats a skipped required check as *satisfied*. Any future gate copied from
those two is bypassable by making its condition false.

### 3.6 `CLAUDE.md`, the single rules file — `R-31`

There is no `CLAUDE.md` and no `.claude/` here. `docs/standards-comparison.md:62`
catalogues `R-31`…`R-33` as *"invented here; no standard has caught up"* — the
rule was documented and none of it implemented.

It is also the **only** part of 4.0.0's §10 with a working delivery mechanism
on this machine. `C:\Users\igors\Projects\CLAUDE.md` records that a project's
own `.claude/settings.json` never loads, because every session starts in the
workspace root — `WeldingSoftware/.claude/settings.json` has sat on disk for
months doing nothing. A subdirectory's `CLAUDE.md`, by contrast, *is* picked up
once files in that folder are touched. So copying 4.0.0's `settings.json` and
hooks into this repository would produce files that gate nothing — the same
*"a hook on an event that never fires"* failure `R-32` warns about, arriving by
a different route.

What the file should hold: the vocabulary pointer (`[tool.repo-quality]`, read
there, never restated), the branch and commit grammar, the pre-push rule, the
secret rule, and — adopting 4.0.0's *"Where this repository is deliberately
relaxed"* — the **agent-facing** relaxations, which are written nowhere today:
that commit wording is checked only after the push, that the scope group is
optional in the checker, that `check_before_push.py` fails open, that nothing
gates a destructive command.

`R-31` as literally written ("one rules file, never two") is unachievable here:
three files already govern a session touching this repository (`~/.claude/`,
the workspace, and this one). The importable form is **one rules file per
scope, and the narrower file never restates the wider one** — which is this
repository's own strongest habit, the vocabulary written once in
`pyproject.toml` and read.

### 3.7 A `commit-msg` hook, so wording is judged before the commit

Wording is checked in CI only, after the push. What that loses: the bad commit
is already in history, so fixing it means `--amend` plus a force-push on a
branch whose PR is open and whose red build already emailed you. And three edge
cases are checked nowhere:

- **a BOM.** A message written by PowerShell `Set-Content -Encoding utf8` and
  passed with `git commit -F` keeps its BOM, and CI then fails the regex with a
  message naming no cause. This is a Windows machine.
- **a revert.** `git revert` writes `Revert "feat(core): x"`, which fails the
  grammar and is only discovered on the runner. Nothing documents the rewording.
- **a sign-off that is not a trailer** — see §1.8.

`default_install_hook_types: [pre-commit, commit-msg]` plus a local hook
running `scripts/check_commit_message.py`, which reuses `load_settings()`
rather than duplicating the vocabulary. **Note the hook-owner collision:**
`.git/hooks/pre-push` here was written by `--install-hook`;
`pre-commit install --hook-type pre-push` will not overwrite a foreign hook, it
moves it aside as `pre-push.legacy` and chains it. Pick one owner — letting
pre-commit own every hook type also makes `--install-hook` and its `HOOK`
template redundant.

### 3.8 A decision table for the contribution policy

`tests/test_branch_policy.py` is already 4.0.0's *"Proving the gate"* pattern,
arrived at independently — four `parametrize` blocks over `classify()`, plus a
test that the vocabulary really comes from `pyproject.toml`, and a docstring
giving the reason (*"the rule that has been wrong twice"*). It is good.

The gap is scope: `enforce_contribution_policy.py` — branch grammar, commit
subject, sign-off, PR body — has **no test file at all**. The one function that
decides whether a contribution is acceptable is the one with no table. Add
`tests/test_contribution_policy.py` with the rows from §3.7 and §1.8, and put
the *reason* on the row rather than in a block docstring, so a failure prints
the rule and not just an input.

### 3.9 `R-27` — the nightly rebuild that catches environment drift

`ci.yml` has no `schedule:`. Nothing re-runs the suite against a changed runner
image, a re-resolved lockfile, or a floating action major that moved. 4.0.0
pairs the cron with a **runner-health step** so a red nightly is diagnosable:
*"a red nightly is environment drift by definition — nothing changed but the
machine."* Name the job that way, have it print `python -VV` and every tool
version, and run `audit_workflow_hazards.py` there — which also gives §1.10 a
caller.

### 3.10 `R-26` — the weekly sweep actually sweeping

See §1.15. `sweep_repository.py` + the existing Monday cron: delete work
branches whose tip is merged (via `gh api -X DELETE`, not `git branch -d`),
nudge PRs stale beyond 30 days, close at 60. 4.0.0's detail worth keeping:
measure idleness from the last push or the last comment **by a human**, not
from `updated_at`, which every comment moves.

Two GitHub facts for the file's header: scheduled workflows are disabled after
60 days of repository inactivity, and `schedule` fires from the default branch
only.

### 3.11 `R-40` — `test` contains everything `release` does

`docs/branching.md:14` draws `└── hotfix merged back ──┘` and there is no
automation, no check and no issue. Nothing notices when `release` holds a commit
`test` does not.

A `release-sync.yml` on push to `release`: merge forward, or `--abort`, warn,
and open-or-comment the single issue `test is behind release`. Two GitHub
facts: a push made with `GITHUB_TOKEN` does not trigger further workflows (so
it cannot loop, but CI will not re-run on the synced branch either), and `test`
must list `github-actions[bot]` as a bypass actor or §3.4's protection refuses
the push.

### 3.12 `R-24` — the pipeline closes the issues it ships

`docs/workflow.md:117` is *"merged into `dev` → close it by hand"*, because
GitHub honours closing keywords only on the default branch. 4.0.0 closes them
from the release instead, by the issue number in each merged branch name.

The `Closes #N` trailer that `enforce_contribution_policy.py` already enforces
is the machine-readable link this needs. It exists and is unused. A
`write_release_notes.py` that walks `--first-parent` since the last `v*` tag,
resolves each merge to its PR via `gh api .../commits/<sha>/pulls`, writes
`release-body.md` for **this version's range** (fixing §1.7) and emits the
issue list to close.

Note the adaptation: 4.0.0 parses `Merge … from <code>-<n>/` subjects, which
requires merge commits. This repository merges `--ff-only`, which is the better
history — so resolve through the API instead. 4.0.0's merge-commit requirement
is a workaround for Gitea's weaker commit→PR lookup, not a principle.

### 3.13 `R-23` — the expensive proof runs *before* the merge into `release`

4.0.0 is blunt: *"after hours of manual testing, making the release must not be
the moment something turns out to be broken."* Its two gates are deliberately
different — a fast one into the integration branch, an expensive one into
`release` that builds, installs, checks, uninstalls and checks again.

Here, the only thing that ever builds the artefact is `release.yml`, triggered
by a tag — i.e. **after** the merge and after the tag exists. A PyInstaller
failure is discovered with the tag already pushed. A `release-gate.yml` on PRs
into `release` that builds the artefact on both platforms and runs
`--version` from a directory that is not the repository would catch it one step
earlier.

### 3.14 The required-file table, with a `copy` column — `§7`, `R-18`

4.0.0's §7 is a table: every required file, a **copy** column
(`verbatim` / `seed` / `generated` / `yours`), and a **no program** column
marking the subset a docs-only repository needs.

Here the manifest is three Python lists inside a script, with two of the four
copy classes missing: nothing is marked *generated* (`requirements-dev.lock`
and `CHANGELOG.md` both are, and `CHANGELOG.md` is filed as a `SKELETON`), and
nothing is marked *yours*. Downstream, nobody knows that editing `ci.yml`
locally **forks** it while editing `docs/architecture.md` locally is expected.

Move it to `[[tool.repo-quality.files]]` in `pyproject.toml` — one array, three
readers: the apply script copies only `verbatim` and `seed` rows,
`audit_required_files.py` fails on a missing row **and on a `verbatim` row whose
bytes differ** (which is what makes `verbatim` mean anything), and
`--render` writes the human-readable table so it cannot drift from the data.

Keep 4.0.0's phrasing: a difference in a `verbatim` file *"is a defect: of the
copy, or of this document — and then it is filed against this document, not
patched in one repository and forgotten."*

### 3.15 "A repository that ships no program" — the second profile

4.0.0 has a whole second profile: no `$App`, the build verbs print
*"nothing to build"* and exit 0, **no coverage floor and no mypy** — *"both
measure a program, and a coverage floor over a repository of documents exits 1
at 0 %"* — pytest's exit 5 is a pass, no changelog, no lockfile.

Every seam here assumes a program: `fail_under = 85` unconditional,
`[tool.mypy] files = ["src"]` (a docs repo has no `src/`, and mypy exits
non-zero on a missing path), every release builds an artefact, and the 24
`CHECKS` have no way to mark a row inapplicable — so a docs-only repository is
reported as failing points 3, 6, 7, 8, 11, 13, 19 and 20. Eight red lines, all
correct, all useless.

**At ~109 repositories this is the highest-leverage item in §7.** A standard
that scores a notes-or-skills repository 16/24 is a standard that gets ignored
on every such repository, and the eight red lines are also why a rollout
stalls: nobody can tell which of the eight are real.

`ships = "program" | "library" | "none"` in `[tool.repo-quality]`; a third
element on each `CHECKS` row naming the profiles it applies to; and — the part
a flag alone would not do — make the `none` profile actually runnable: guard
the `coverage` and `quality` jobs on the profile, and let pytest's exit 5 pass
**only** under `ships = "none"`.

### 3.16 Vendoring provenance — `§11`

Every vendored copy in 4.0.0 carries a first line naming where it came from and
when, because *"waam-manipulator took its copy from waam-monitoring and got
waam-monitoring's folder names with it."*

`copy()` here is a bare `shutil.copy2`. Nothing in a target repository records
which template revision it received. At ~109 repositories, repository 60
holding a two-revisions-old `check_before_push.py` with no way to tell is the
certain outcome — and that file has already been fixed repeatedly
(`:56-62`, `:68-74`, `:142-145`, `:193-198`, `:236-241` are each a recorded
field fix).

One stamped line per copied file, plus `check_vendored_drift.py` run from the
workspace — not per repository, since that is the only scope that loads.

### 3.17 `§12` — the merge order of a compliance batch

An old repository arrives as a **batch** of pull requests merged in a fixed
order, each judged by what already stands: pins first, then scripts and tests,
then `.gitignore`, then content, **gates last** — so the target is never red
for work not yet merged. And: **"floors are measured, not wished"** — the
coverage floor starts at the value measured on adoption and only rises.

`apply_template_to_repo.py` copies everything in one undifferentiated pass and
prints a flat `still to do by hand:` list. A target whose coverage is 40 %
receives `fail_under = 85` and goes permanently red, which is *floors are
wished* in one line.

`--plan` emitting the ordered groups, and `--measure-floors` running coverage
and mypy against the target *before* writing, emitting a floor sized to what it
actually counts with a comment saying the number moves one way only. This is
process knowledge that maps directly onto the `apply-repo-quality-standard`
skill.

### 3.18 `§12` — "How to review, fast"

4.0.0 gives a reviewer a fixed order, a time budget and permission to stop:
`test → release` ≈ five minutes, work → integration ≈ twenty, **never review
style** (the formatter already did), *read signatures and tests, not bodies*,
and one literal command — `git diff --stat origin/release...origin/test` —
to prove no build output crept in.

Here, `docs/workflow.md:80-105` names what the machine checks and leaves the
reviewer a single sentence. `.github/PULL_REQUEST_TEMPLATE.md:50-58` is a
checklist for the **author**. No order, no budget, nothing saying what to skip.

### 3.19 `§14` — what compliance buys you

4.0.0 devotes a section to arguing the standard's **value** to its reader.
Nothing here does. `README.md:101-144` is a control table; `CONTRIBUTING.md`
is rules; `docs/workflow.md` is procedure. The closest thing to an argument is
one clause about why an issue comes first.

This matters at scale, not aesthetically: repository 60 of 109 gets the
standard applied by a skill that must be worth invoking, and a 24-row control
table is a cost sheet with no benefit column. `docs/why.md`, one screen, each
bullet naming the file that delivers it.

### 3.20 `§15` — what the standard does not answer

4.0.0 keeps an explicit section for unanswered questions. `docs/decisions.md`
is adjacent but different: it records divergences **already decided**, each
with a reopen trigger, and `:106-119` honestly separates *"we chose this"* from
*"we did not get to this"* — which is better than 4.0.0's equivalent in three
ways and should not change.

What it lacks is questions nobody has answered yet, and there are several live
ones: how a repository declares which revision it meets (§3.1); whether a repo
that ships no program must still carry benchmarks and screenshots (§3.15); what
the ISO threshold of 70 means and who may lower it; whether 85 % is a floor or
a target.

### 3.21 Manual tests — `R-28`…`R-30`, the registry without the web app

`docs/standards-comparison.md:61` already concedes this repository *"has
nothing at all on tests a human has to perform"*, and `docs/branching.md:8`
asserts `test` gets *"full CI plus manual checks"* with no registry, no
recorded verdict and no override. The entire audit trail of every manual check
ever performed here is the bash comment `# manual checks on test` at
`docs/workflow.md:134`.

**Adopt the registry and the rule; skip the page.** 4.0.0's `index.html` and
`serve.py` are ~450 lines of hand-written DOM plus a local HTTP proxy with its
own threat model (DNS rebinding, header CSRF, Windows port reuse) existing
solely to keep a token out of a browser that `gh` never involves. Unreachable
from a phone, too.

| | file | ~lines | why |
| --- | --- | ---: | --- |
| 1 | `tests/manual/tests.json` | 25 | the registry; the only artefact the other 108 repos need |
| 2 | `tests/test_manual_registry.py` | 90 | validation riding the existing suite — no new CI job, and mirrored locally for free |
| 3 | `scripts/record_manual_verdict.py` | 150 | `--list` / `<id> pass` / `--done`; evidence upload |
| 4 | `.github/workflows/manual-verdict.yml` | 25 | `on: status`, the re-check that makes `R-29` real |

Two seeds for the registry, both things only a person can judge here: the
window legible at 100 % and 150 % DPI (`docs/quality-iso25010.md:68` already
admits accessibility is the weakest area — the registry is where that admission
becomes a row with a verdict), and the screenshots still matching the program.

Three details worth carrying faithfully:

- **`R-30`, evidence keyed by commit sha.** Forty lines inside a script that
  has to exist anyway, and it converts an unprovable claim into an audit trail.
  Keep 4.0.0's rule that **an upload failure does not cost the verdict** — a
  tester's result is worth more than the photo of it — because that is the rule
  most likely to be dropped as an edge case and the one that keeps a tester
  from giving up on the tool.
- **`verdict` is a reserved id** — an entry so named posts to the aggregate
  context and passes the whole gate on its own. On GitHub there is a second
  reason: the re-check workflow keys on the context name, so it would
  retrigger itself.
- **Use a commit status, not a job.** A conditional job produces a *skipped*
  check-run, which protection treats as satisfied (§3.5). A status for a
  context nobody has posted stays `pending` and blocks the merge. That
  asymmetry is the whole reason to pay for a script.

**Where this meets the `scenario-testing` skill:** the registry is the holding
pen, `scenario-testing` is the drain. 4.0.0 says so itself — a visual judgement
*can* leave the manual list, as a deterministic screenshot-against-baseline
diff in the automated suite, with a person approving a new baseline once, when
the picture is meant to change. The one §9 rule that skill lacks is per-sha
retention: its runs land under a timestamp, not a commit. Keying those folders
by `git rev-parse HEAD` would make `R-30` hold for the automated half too.

### 3.22 Generated documentation — `R-34`, `R-35`, scoped

4.0.0: documentation generated on every push, so a hand edit is overwritten; a
generation failure **fails the build**; a publish failure is only a warning.
That split is the transplantable part — a build that goes red for a reason
having nothing to do with the code teaches everyone to ignore a red build.

But the import has to be **scoped**, and 4.0.0 does not draw the line because
its generator only ever emits API pages. The most valuable documents here
cannot be generated from anything: `docs/architecture.md:25-41` ("Why this
way"), `:53-63` ("Deliberate omissions"), `docs/decisions.md` entire,
`docs/branching.md:52-65` (the history of a rule that was wrong twice). An
overwrite-on-push regime over those would destroy the only content a generator
cannot replace.

So: **generate every table of numbers and the API reference; never touch the
prose.** `<!-- generated:… -->` markers as the mechanism, `--check` mode in CI
as the enforcement, and §2 is the bill for not having it. Add `"D"` to ruff's
select first — eight public symbols have no docstring, so a generator would
emit eight empty entries today.

This repository already owns the precedent and says so:
`scripts/capture_usage_screenshots.py`, and `README.md:24-25`. The principle is
established; it is applied to exactly one artefact.

### 3.23 Smaller imports, cheap

- **`.gitattributes`** with `* text=auto eol=lf` and explicit `binary` rows;
  plus `fix-byte-order-marker` and `mixed-line-ending --fix=lf` in pre-commit.
  Name `docs/sample.txt` explicitly — `capture_usage_screenshots.py` reads it
  and the README quotes its character counts, so a CRLF checkout changes a
  number the README asserts.
- **`R-41`'s issue fields**: a `Priority/*` label, an assignee, and the
  **milestone** — which is what makes *"what shipped in v1.2.0"* answerable
  without reading a diff. `grep -rni 'milestone\|assignee\|priority'` returns
  nothing but two prose mentions. Note 4.0.0 only gets **S** (an advisory
  skill) for this rule, so a CI check here would be stronger than the original.
- **`gh issue develop`** is GitHub's exact equivalent of 4.0.0's branch-ref
  link, and creates a real linked branch in the issue's Development panel.
  Today the link is one-way: the issue number is in the branch name, but from
  issue #12 there is no pointer to its branch until a PR exists.
- **`Issue: #N` as a PR's first line**, accepted alongside `Closes #N`.
  `.github/PULL_REQUEST_TEMPLATE.md:16-18` currently requires a keyword and
  then explains in its own comment that the keyword does nothing and the work
  must be done by hand. Keep `Closes` (it populates GitHub's linked-issues
  panel, which 4.0.0's bespoke line does not get for free), but put the
  machine-readable link on line 1 so it survives on a PR where the keyword is
  inert.
- **"Facts only, not one adjective: numbers, and links to the artefacts"** —
  one line added to the `description:` of each issue and PR textarea. Free, and
  it is the difference between an issue a test can be written from and an issue
  a reviewer has to interview someone about.
- **An anti-list** — 4.0.0's *"Not required, and better left out"*: no
  `Makefile`, no second rules file, no launcher script, no task-runner sections
  in `pyproject.toml`. Verified: all absent today, which makes **now the
  cheapest possible moment to write it**, because the test enforcing it passes
  on the first run.
- **A glossary.** `release` here is simultaneously a branch, a directory, a
  commit scope, an optional-dependency group, a workflow and the published
  object. 4.0.0 devotes a table to exactly this.
- **`hotfix` and `experiment` in `branch_types`**, plus `R-22` written down as
  a rule — *`test` stays releasable at all times* — which is what makes the
  hotfix route safe.
- **`.claude/logs/` and `.claude/settings.local.json` in `.gitignore`.**
  Harmless today; a leak the first time a session writes a log in a repository
  copied from this template.
- **The onboarding route for a repository with a past.** `docs/branching.md:82-98`
  offers `git log --oneline origin/dev.."$b" | wc -l`. After a history rewrite —
  which this standard mandates implicitly, since sign-off is required on commits
  predating the rule — that count never reaches 0 and the documented procedure
  dead-ends. 4.0.0 gives both routes and the right command:
  `git rev-list --count --cherry-pick --right-only`.
- **`R-32`'s honesty**: a dated note saying when an external product's surface
  was last checked. This repository already owns the idiom —
  `audit_workflow_hazards.py:29`, *"as of 2026-08. Anything below is a time
  bomb."* It is now fourteen months old; re-date it in the same change.

---

## 4. Reject, and write down why

Five places where the two documents require **opposite** things. Each needs a
line in `docs/decisions.md`, because an unexplained difference gets
re-litigated every six months.

### 4.1 Keys in the repository — `R-02`. **Reject, unconditionally.**

4.0.0: *"Where it lives: `.claude/.env`, committed with the repository."* §7
goes further — a copy of the `.gitignore` seed *must not* add a `.env` line,
because that would hide the keys.

Here: `.gitignore:1-4` ignores `.env` and `*.env`; `gitleaks` runs in
pre-commit **and** over full history in `ci.yml:99-106`; `detect-private-key`
too. Igor's own global rule is stricter still — secrets live only in
`~/.claude/igor.env`, outside every repository.

These are not merely opposite, they are **mechanically incompatible**: a
committed `.claude/.env` with a real token would be caught by the pre-commit
hook, and if forced through, would fail the `security` job on every subsequent
push forever. `R-02` is sound only inside its stated premise — a LAN server
where reading needs no account, so the key is already readable by anyone who
can read the code. This repository is public on github.com; the premise is
false, and the rule inverts from *"no worse than the code"* to *"a live
credential published to the internet"*.

**Import `R-02`'s good half instead**, which this repository asserts and does
not deliver: one declared file per repository listing every key its scripts use.
See `.env.example` in §1.15.

### 4.2 Two long-lived branches, or three. **Keep three.**

4.0.0: `release` + `test` only — *"a third is a second answer to what is
current."* Here: three, argued from an audit of real repositories
(`docs/branching.md:52-65`), enforced by a script, and covered by a test.

But 4.0.0 names a real cost that this repository has already paid in writing:
`docs/workflow.md:109-111` concedes `Closes #12` will not fire on a merge into
`dev`. That is a symptom of the third branch, not of GitHub — and §3.12 is how
to pay it off. Import the two pieces that are branch-count-independent: `R-22`
and the base/head pairing check (§1.14).

### 4.3 Merge commits, or `--ff-only`. **Keep `--ff-only`.**

4.0.0 *requires* merge commits and forbids every other style, because its
release notes and its override record both walk `--first-parent` and parse
`Merge … from <code>-<n>/` subjects. That is a workaround for Gitea's weaker
commit→PR lookup, not a principle. `--ff-only` plus
`required_linear_history: true` is the cleaner history; adapt the parsers
(§3.12).

### 4.4 Who writes `CHANGELOG.md`. **Keep it hand-written.**

`R-24`: the pipeline writes it, *"nobody edits `CHANGELOG.md`"* — and 4.0.0's
own column marks that half `—`. Here it is Keep-a-Changelog prose with an
`[Unreleased]` section, and it is **better because it is hand-written**: the
`Fixed` entries at `:29-39` explain *why* the branch policy rejected every
Dependabot branch, a cause no generator can know. `docs/branching.md:111` is
right that a fixed vulnerability must be *named* there by a person.

The defect is narrower and real — §1.7. §3.12's split resolves both:
`release-body.md` generated for this version's range, `CHANGELOG.md` left
curated and shipped inside the zip, as `build_release_artifact.py:93` already
does.

### 4.5 Fail open, or fail closed. **Both — split by object.**

The sharpest opposition in the two documents, and the resolution is a
distinction neither draws on its own.

`R-33`: the gate hook may only **deny or stay silent** — never `allow` — and a
payload it cannot parse is **denied**, because *"an empty payload parsed to
nothing, the gate printed nothing, and the call went ahead."*

`check_before_push.py` does the exact opposite and argues for it:
*"A hook that cries wolf gets bypassed with `--no-verify` until it stops being
read at all."*

Both are right about different objects:

- **a check that judges code fails open** — CI will judge it again, so blocking
  on an unjudgeable local environment is a false alarm;
- **a gate that judges an irreversible action fails closed** — nothing
  downstream repeats the judgement, and the two error costs are not
  comparable. A false deny costs a retyped command; a false allow costs work no
  later command recovers.

This repository implements only the open half, and even that one wrongly — see
§1.2, where a check that *cannot* judge still says "safe to push". Write the
distinction into `CLAUDE.md` rather than picking a winner.

Note also that a deny-only hook is bounded **by construction**: it can only
ever be more restrictive than the human's own policy, so its worst failure mode
is friction, not an unauthorised action. That is the property that makes
`R-33` a security rule and not a style preference.

### 4.6 One rules file, or none. **One per scope.**

`R-31` forbids `AGENTS.md`, `GEMINI.md`, `.cursorrules`, `.claude/rules/`, and
even a `CLAUDE.md` that points to one. All of those are absent here — so there
is nothing to delete, and §3.23's anti-list is what to write.

Drop the last clause. On a repository with no committed AI environment, a short
`CLAUDE.md` pointing at `CONTRIBUTING.md` and `docs/workflow.md` is cheaper
than duplicating them — and duplicating them is what `R-31` would otherwise
force.

### 4.7 Not applicable, and why

Worth recording so it is not re-examined: `recipe.ps1` and its eight verbs
(this repository's single interface is `scripts/*.py`, which the workspace rules
require and which cannot run on five of its six CI jobs); `$env:LAB_SHARE` and
`$Needs` pinning `name@tag` (pip plus a lockfile is the same idea);
`R-38`, every command valid in PowerShell 5.1 (cross-platform CI here); `R-13`
(ctest/clang-tidy); the generated Gitea wiki and its bootstrap; `lab-bot`, the
org team, `LAB_BOT_TOKEN` (`GITHUB_TOKEN` is minted per run with per-job
`permissions:`); the act_runner registration and its timeouts; Git LFS (two
small PNGs); the literal override phrase as a shared constant; and `§7`'s
*"No `.github/` either"*, which inverts entirely here and is why *"copy
`SECURITY.md` into B"* is a §7 table row, not a file copy.

---

## 5. The two self-distribution strategies

4.0.0's claim: *"Every file this document requires is written out inside it.
Copy it into a bare project and that project is a lab project."* This
repository's opposite claim: it **is** a working project, distributed by
`apply_template_to_repo.py`.

**Where the inline document is more robust.** It needs git and a text editor —
no Python, no network, no server. It is readable end to end by a person or an
AI session with nothing else loaded, which is a real property when the consumer
*is* a session handed one file. And it answers two questions this repository
cannot: which revision am I on, and in what order do I move to the next one.

**Where it rots, and it rots hard.** Every embedded listing is a fork of a real
file, so a bug in one is an N-repository manual migration. The document proves
this against itself: §17's 4.0.0 entry contains roughly forty *"Fixed in the
copied code"* items, and the class is diagnostic — *"BOM-free step outputs,
which had been silently skipping the install proof"*, *"no `${{ }}` in a `run:`
block"*, *"a commit check that failed open"*, *"every read of a commit's
statuses takes every page, not the server's first 50"*. Every one is a listing
that was copied and **never executed by the document**. Three consecutive
revisions each shipped a batch. And the migration guide opens by admitting the
trap closes behind you: *"Replace `gate.ps1` first — by hand, or from a shell
outside Claude Code if the old gate refuses the command."*

**Where this repository is more robust.** The file in the repository *is* the
file that runs, so an entire class of those bugs cannot exist: `ci.yml` cannot
be a listing that stopped parsing, because it parsed this morning. That is the
bigger win.

**Where it rots.** No version, no revision, no migration list, and `copy()`
silently skips every file the target already has — so a repository adopted in
August is frozen in August and **nothing can tell you that**. The inline
document's rot is visible in a diff; this one's is invisible by construction.

**Verdict.** This repository's strategy is right and should not change. Take
the three *bookkeeping* artefacts the other document got from inlining and this
one never needed to invent — the **revision plus README line** (§3.1), the
**copy-class manifest plus drift check** (§3.14, §3.16), and the **ordered
migration list** (§3.17). Those are not consequences of writing files out
inline. They are consequences of taking seriously that copies exist. This
repository has copies and pretends it does not.

---

## 6. Suggested order

Gates last, in every case, so nothing is red for work not yet merged.

**Now — defects, and the report you are reading is about to be wrong again**

1. Fix `docs/standards-comparison.md` against 4.0.0 and against the real
   numbers (§0). Rewrite the `R-02` finding as a divergence.
2. `check_before_push.py`: add `REPO_SCRIPTS`, and make both `NOT CHECKED`
   paths non-zero (§1.1, §1.2).
3. Pin ruff three ways and add `required-version`; pin the build backend
   (§1.3).
4. `README.md:178` → `git tag -s -a` (§1.4).
5. `release.yml`: tag-vs-version check, `concurrency`, the `${{ }}` out of the
   `run:` string, and the release body sliced to this version (§1.5-§1.7).
6. The scope `?` and the sign-off substring test in
   `enforce_contribution_policy.py` (§1.8).
7. The three files `apply_template_to_repo.py` cannot deliver (§1.9).
8. The four false prose claims (§1.11) and the two contradictory procedures
   (§1.12, §1.13).

**Next — the bookkeeping that makes 109 repositories tractable**

9. `docs/standard.md` with `P-01`…`P-24`, `standard_version`, the README line,
   and the check behind it (§3.1).
10. The "checked by" column, filled in honestly — nine `—` and two weak probes
    (§3.2).
11. `[[tool.repo-quality.files]]` with the copy column, plus `--check` drift
    mode and a provenance stamp (§3.14, §3.16).
12. `ships = program | library | none` (§3.15).
13. `--plan` and `--measure-floors` (§3.17).

**Then — the gates**

14. The aggregate `gate` job (§3.5) — everything below depends on it.
15. `apply_branch_protection.py`, dry run by default, read back (§3.4).
16. The base/head pairing check (§1.14).
17. The recorded override (§3.3).
18. `release-gate.yml`, so the artefact is proved before the merge (§3.13).
19. The nightly environment job, which also gives `audit_workflow_hazards.py`
    a caller (§3.9, §1.10).
20. The sweep that sweeps (§3.10) and `release-sync.yml` (§3.11).
21. `write_release_notes.py`, closing the issues the release ships (§3.12).

**Alongside, cheap and independent**

22. `CLAUDE.md`, with the relaxed section (§3.6).
23. `.gitattributes`, the anchored `.gitignore`, `.env.example`,
    `hotfix`/`experiment`, the anti-list, the glossary (§3.23, §1.15).
24. `default_install_hook_types` + `check_commit_message.py` (§3.7), and
    `tests/test_contribution_policy.py` (§3.8).
25. Ruff `D` plus the eight docstrings; then the generated tables and API
    reference with `--check` in CI (§3.22, §2).
26. The manual-test registry, four files, no web app (§3.21).
27. `docs/why.md` (§3.19), "How to review" (§3.18), "Not answered yet"
    (§3.20).
28. Record the five rejections in `docs/decisions.md` (§4).

---

## 7. What the other document should take from this one

For symmetry, and because the old comparison's §6 promised this exchange and
delivered it one-way.

1. **`SECURITY.md`.** Still the cheapest unclosed item after four revisions —
   three passing-level OpenSSF criteria for one file. Harder than it looks:
   §7's anti-list bans `.github/`, so it needs a new §7 row with
   `copy: verbatim`, not a drop-in.
2. **Plain HTTP as a recorded decision.** `http://192.168.226.1:3000` costs two
   passing-level criteria. On a LAN it is a considered trade; undocumented, it
   gets rediscovered as a defect. §15 is still three lines.
3. **Dependency monitoring.** Zero hits for Dependabot or Renovate in 6138
   lines.
4. **Measured evidence.** Benchmarks over its own code, a coverage floor, a
   complexity ceiling, an ISO 25010 assessment citing those numbers, `gitleaks`
   over full history. 4.0.0 added none of it, and it is the whole of what this
   repository is for.
5. **`docs/decisions.md` as a form** — a divergence with a **reopen trigger**,
   and a firewall between *"we chose this"* and *"we did not get to this"*. The
   other document has no equivalent after four revisions, which is precisely
   why plain HTTP is still undocumented.
6. **A check for `R-42`.** Its own column marks that rule `—`:
   *"an audit reads it first; nothing checks the link or the claim."*
