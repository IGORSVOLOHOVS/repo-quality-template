# Three standards, side by side

Where this standard's fourteen points came from, what an external checklist
would still ask for, and which of those gaps are deliberate.

The divergences that are deliberate are argued in [`decisions.md`](decisions.md).
The gaps that were open when this was written are being closed - the section
"What to do, shortest path first" is the list, and items 1, 3, 5 and 6 are
already done.

What each of these asks of a repository, where they agree, and what each one
alone would catch.

| | source | size | shape |
| --- | --- | --- | --- |
| **A** | [OpenSSF Best Practices Badge](https://github.com/ossf/best-practices-badge) + [Scorecard](https://github.com/ossf/scorecard) | 68 passing criteria, 54 more for silver/gold, 20 automated checks | what the wider open-source world asks of a public project |
| **B** | `BEST_REQUIREMENTS.md` rev 2.0.0 | 2214 lines, 36 numbered rules R-01…R-36, 23 required files, 5 Gitea workflows | how a repository in `additive-lab` is built and gated |
| **C** | [`repo-quality-template`](https://github.com/IGORSVOLOHOVS/repo-quality-template) | 14 points, 35 files, 3 GitHub workflows, 6 CI jobs | a working reference project that proves the 14 points |

A is a checklist. B is a process with the workflows written out. C is a
project that already passes its own list and can copy itself onto another
repository. They overlap less than their subject suggests, because they
answer different questions: A asks "can a stranger trust this?", B asks "can
this reach `release` without a human being careless?", C asks "is this
measurably good?".

---

## 1. Where all three agree

Eleven things every one of the three requires. A repository with only these
is already past most of what any of them will complain about.

| what | A | B | C |
| --- | --- | --- | --- |
| A README that says what the project is | `description_good` | §7 | point 2 |
| An OSI licence at the top level, with a name on it | `floss_license`, `license_location` | §7, MIT | point 5 |
| Contribution instructions | `contribution` | `CONTRIBUTING.md` | `CONTRIBUTING.md` |
| An issue tracker | `report_tracker` | §4, issue-first | GitHub issues |
| Version control with history | `repo_track` | git | git |
| Unique, incrementing versions | `version_unique`, `version_semver` | R-23, `$Version` | tags `v1.2.0` |
| Tagged releases | `version_tags` | release workflow | `release.yml` |
| Release notes | `release_notes` | R-24, written by the pipeline | `CHANGELOG.md` |
| A documented build command | `build`, `build_common_tools` | R-10, `recipe.ps1 build` | `build_release_artifact.py` |
| Tests run automatically on every change | `test_continuous_integration` | R-12, propose gate | `ci.yml`, six jobs |
| Lint warnings treated as failures | `warnings`, `warnings_fixed` | R-12, ruff and mypy | ruff, fails the job |

---

## 2. What B has that A and C do not

B's own ideas, the ones no external standard asks for. These are its
contribution and the parts worth defending.

| B rule | what it is | why A and C miss it |
| --- | --- | --- |
| R-07 | Work starts as an issue; no branch without an issue number | A wants a tracker; it never says every change must come through one |
| R-08 | Branch grammar `<code>-<issue>/<type>/<slug>`, machine-checked | nowhere else |
| R-09 | `<type>(<scope>): <subject>` with a sign-off, checked in CI | A has `dco` only at silver |
| R-10, R-11 | One interface, `recipe.ps1`, exactly eight verbs | A asks that a build exist, not that there be one way in |
| §9, R-28…R-30 | A manual-test registry with a page that runs it, a verdict per commit, evidence kept, and an empty list counted as passed rather than skipped | A and C have nothing at all on tests a human has to perform |
| §10, R-31…R-33 | The AI environment: `CLAUDE.md` as the single rules file, hooks wired only to events the product actually fires, a gate hook that may only deny or stay silent | invented here; no standard has caught up |
| §11, R-34, R-35 | The wiki is generated on every push and never hand-edited; a change that cannot be documented is not done | A asks for documentation, not for a mechanism that keeps it true |
| R-19, R-20, R-21 | Reviewers declared once in the recipe, whitelists mirror it, no auto-merge, a human clicks | Scorecard's `Code-Review` asks for review; it does not ask that the reviewer list have one source |
| R-25 | Every release carries an SBOM | Scorecard checks `SBOM` — and **C does not produce one** |
| R-26, R-27 | Weekly sweep of stale branches and pull requests; nightly rebuild of `test` to catch environment drift | nowhere else, and environment drift is a real failure mode nobody else names |
| R-14, R-16 | The toolchain is pinned and drift refuses to run; `$Needs` pins `name@tag`, never a branch tip | Scorecard's `Pinned-Dependencies` is the closest and it is weaker |
| R-36, §17 | The standard is versioned, and a repository states which revision it complies with | nowhere else — and it is the reason this comparison can be written at all |

---

## 3. What C has that A and B do not

| C point | what it is | why A and B miss it |
| --- | --- | --- |
| 7 | Benchmarks over the project's own code, run in CI, numbers published in the README | A has no performance criterion at any level; B has none either |
| 8 | An ISO/IEC 25010 assessment: eight characteristics, four measured, four argued **citing those measurements** | nothing comparable anywhere |
| 11 | Usage screenshots as a required artefact | nowhere else |
| — | Complexity ceiling: ruff `C90`, maximum 10, enforced | A stops at "no warnings" |
| — | Coverage floor of 85 %, enforced in CI | A wants 80 % at silver and 90 % at gold; C sits between them and **enforces** it |
| — | `gitleaks` over the full history on every push | A's `no_leaked_credentials` is a promise; this is a check |
| — | `audit_workflow_hazards.py` | Scorecard has `Dangerous-Workflow`; B has nothing |
| — | Security linting through ruff's `S` (bandit) rules, in CI | the closest thing here to A's `static_analysis_common_vulnerabilities` |
| — | `apply_template_to_repo.py` — the standard installs itself into another repository and reports which points that repository now satisfies | A and B are documents; this one is executable |
| 14 | Exactly three branches, CI fails if a fourth appears | B has two branches by rule but does not fail a build over a third |
| 12 | English throughout, as an explicit rule | A has `english` for the badge, and asks for **internationalisation** at silver, which is the opposite choice |

---

## 4. What A has that neither B nor C does

The gaps, cheapest to close first.

| A criterion | level | B | C | note |
| --- | --- | --- | --- | --- |
| `vulnerability_report_process` | passing | **no** | yes | B has no `SECURITY.md`; it is not in the §7 list |
| `vulnerability_report_private` | passing | **no** | yes | a private channel to report a hole |
| `vulnerability_report_response` | passing | **no** | partial | a stated response time |
| `release_notes_vulns` | passing | **no** | **no** | release notes must name the vulnerabilities fixed |
| `know_secure_design` | passing | **no** | **no** | somebody on the project can name the common design errors |
| `know_common_errors` | passing | **no** | **no** | the same for implementation errors |
| `dependency_monitoring` | silver | **no** | **no** | no Dependabot, no Renovate, nothing watching for known-vulnerable dependencies |
| `signed_releases`, `version_tags_signed` | silver | **no** | **no** | C writes a SHA-256 per artefact, which is integrity, not authenticity |
| `dynamic_analysis` | passing | **no** | **no** | fuzzing, sanitizers, assertions enabled in a test build |
| `two_person_review` | gold | partial | **no** | B requires one whitelisted approval; gold wants two people |
| `build_reproducible` | silver | **no** | **no** | same source, same binary |
| `code_of_conduct` | silver | **no** | **no** | |
| `governance`, `roles_responsibilities`, `bus_factor` | silver/gold | **no** | **no** | who decides, and what happens when one person is unavailable — both standards are written by and for one person, and it shows |
| `input_validation` | silver | **no** | **no** | |
| `documentation_quick_start` | silver | partial | yes | C's README has one |
| `copyright_per_file`, `license_per_file` | silver | **no** | **no** | |

Nine of A's sixteen `Security` criteria are `crypto_*` and do not apply to
either project. They are excluded above rather than counted as failures.

---

## 5. Two findings

**B breaks its own rule R-02.** Line 46 of `BEST_REQUIREMENTS.md`, in §2,
holds a real 40-hex-character Gitea token where the placeholder belongs. §3
line 58 does it correctly. The document's own task T008 is ticked as "Verify
§2 contains NO literal token value", and it does contain one. A's
`no_leaked_credentials` therefore fails on the standard itself, and C's
`gitleaks` step would have caught it in any repository that had one. Rotate
the token and fix the line.

**B is served over plain HTTP.** `http://192.168.226.1:3000`. A's
`sites_https` and `delivery_mitm`, both passing-level, fail. On a LAN this is
a considered trade rather than an oversight, but it costs two passing-level
criteria and belongs in the document as a decision instead of being left to
be rediscovered.

---

## 6. What to do, shortest path first

1. **Add `SECURITY.md` to B's §7 list.** Three passing criteria, one file,
   and C already has one to copy. The cheapest change in this report.
2. **Fix line 46 and rotate that token.**
3. **Give C an SBOM step.** B's R-25 requires one per release, Scorecard
   checks for it, and C's `release.yml` does not produce one.
4. **Give C a review requirement.** B's R-20 and R-21 are its strongest
   rules and C has no equivalent. A solo project can still require a pull
   request and a green gate before `release`.
5. **Give C type checking.** B's R-12 runs mypy; C's fourteen points do not
   mention it, and ruff does not type-check.
6. **Turn on dependency monitoring in both.** One file,
   `.github/dependabot.yml`, closes a silver criterion neither has.
7. **Sign the tags.** `git tag -s`. Closes `version_tags_signed`, and it is
   one flag.
8. **Write down the divergences that look like gaps and are not:** plain HTTP
   on a LAN, English instead of internationalisation, one reviewer instead of
   two. A standard that does not record why it diverges gets re-litigated
   every six months.

Items 3, 4 and 5 are B's ideas moving into C; item 1 is C's idea moving into
B. That exchange is most of the value here — the two documents together are
stronger than either, and neither is missing anything the other cannot
supply.

---

## 7. One line on each

**A** is the floor a stranger measures you against. Neither B nor C would
earn a passing badge today, and both fail on the same thing: nothing says how
to report a security hole, and nothing watches the dependencies.

**B** is the better *process*. Nothing else here makes work start at an
issue, gates a merge on a human, keeps a manual-test verdict per commit, or
notices that the build environment drifted overnight.

**C** is the better *evidence*. It is the only one of the three that produces
numbers — coverage, complexity, benchmark medians, an ISO 25010 score — and
the only one that can install itself into another repository and report what
is still missing.
