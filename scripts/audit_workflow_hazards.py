"""Find, across every repository, the four faults that broke CI today.

Each of these failed silently until a push happened, and each is detectable by
reading the workflow file:

  1. A pinned action version that is deprecated or archived. GitHub fails the
     run before any step executes (actions/cache v2), or the path stops
     resolving entirely (actions/setup-haskell).
  2. A tool invoked in CI but declared nowhere - pytest-cov, pytest-mock,
     types-requests. The step runs, the flag is unrecognised, the job dies.
  3. A workflow watching a branch the repository does not have. It never runs,
     which reads as "no CI" rather than "CI is broken" - the worst outcome,
     because nothing tells you.
  4. `uv sync` in a repository with no pyproject.toml.

    python audit_workflow_hazards.py
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
MIRRORS = HERE / "_secret_scan"

# Latest major of each action, as of 2026-08. Anything below is a time bomb.
CURRENT_MAJOR = {
    "actions/checkout": 4,
    "actions/setup-python": 5,
    "actions/setup-node": 4,
    "actions/cache": 4,
    "actions/upload-artifact": 4,
    "actions/download-artifact": 4,
    "docker/setup-buildx-action": 3,
    "docker/build-push-action": 6,
    "docker/login-action": 3,
}
# Actions that no longer exist at that path at all.
DEAD_ACTIONS = {
    "actions/setup-haskell": "haskell-actions/setup",
    "actions/create-release": "softprops/action-gh-release",
    "actions/upload-release-asset": "softprops/action-gh-release",
}

# A flag in a CI command implies a package that must be installed.
FLAG_REQUIRES = {
    r"--cov\b": "pytest-cov",
    r"--benchmark": "pytest-benchmark",
    r"\bmocker\b": "pytest-mock",
    r"\bmypy\b": "mypy",
    r"\bruff\b": "ruff",
    r"\bblack\b": "black",
}

USES = re.compile(r"uses:\s*([\w.-]+/[\w.-]+)@v?(\d+)")
BRANCHES = re.compile(r"branches:\s*\[([^\]]*)\]")
RUNS = re.compile(r"run:\s*(.+)")


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.stdout if p.returncode == 0 else ""


def default_branch(repo: Path) -> str:
    head = git(repo, "symbolic-ref", "--short", "HEAD").strip()
    if head and git(repo, "rev-parse", "--verify", "--quiet", head).strip():
        return head
    for c in ("release", "main", "master", "dev"):
        if git(repo, "rev-parse", "--verify", "--quiet", c).strip():
            return c
    return ""


def audit(name: str) -> list[dict]:
    repo = MIRRORS / f"{name}.git"
    if not repo.exists():
        return []
    branch = default_branch(repo)
    if not branch:
        return []

    files = git(repo, "ls-tree", "-r", "--name-only", branch).splitlines()
    workflows = [f for f in files if re.match(r"^\.github/workflows/.+\.ya?ml$", f)]
    if not workflows:
        return []

    real_branches = {b.strip() for b in
                     git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
                     if b.strip()}
    manifests = "\n".join(
        git(repo, "show", f"{branch}:{m}")
        for m in files
        if m in ("pyproject.toml", "requirements.txt", "requirements-dev.txt", "package.json")
    )
    has_pyproject = "pyproject.toml" in files

    issues: list[dict] = []
    for wf in workflows:
        body = git(repo, "show", f"{branch}:{wf}")
        short = wf.split("/")[-1]

        for action, major in USES.findall(body):
            if action in DEAD_ACTIONS:
                issues.append({"repo": name, "file": short, "kind": "dead action",
                               "detail": f"{action} -> use {DEAD_ACTIONS[action]}"})
            elif action in CURRENT_MAJOR and int(major) < CURRENT_MAJOR[action]:
                issues.append({"repo": name, "file": short, "kind": "outdated action",
                               "detail": f"{action}@v{major} (current: v{CURRENT_MAJOR[action]})"})

        commands = " ".join(RUNS.findall(body))
        # A tool counts as declared if a manifest lists it OR the workflow
        # installs it inline. Checking manifests alone reports a false positive
        # for every `pip install ruff` step.
        declared = manifests + "\n" + "\n".join(
            re.findall(r"pip install[^\n|&]*", body))
        for pattern, package in FLAG_REQUIRES.items():
            if re.search(pattern, commands) and package not in declared:
                issues.append({"repo": name, "file": short, "kind": "tool not declared",
                               "detail": f"CI uses {package} but nothing installs it"})

        if "uv sync" in commands and not has_pyproject:
            issues.append({"repo": name, "file": short, "kind": "uv without pyproject",
                           "detail": "uv sync needs a pyproject.toml; this repo has none"})

        watched = set()
        for group in BRANCHES.findall(body):
            watched |= {b.strip().strip('"\'') for b in group.split(",") if b.strip()}
        missing = sorted(watched - real_branches)
        if watched and not (watched & real_branches):
            issues.append({"repo": name, "file": short, "kind": "never triggers",
                           "detail": f"watches {sorted(watched)}; repo has {sorted(real_branches)}"})
        elif missing:
            issues.append({"repo": name, "file": short, "kind": "watches a missing branch",
                           "detail": f"{missing} do not exist"})
    return issues


def main() -> int:
    names = sorted(p.stem for p in MIRRORS.glob("*.git"))
    found = [i for n in names for i in audit(n)]

    by_kind: dict[str, list[dict]] = {}
    for i in found:
        by_kind.setdefault(i["kind"], []).append(i)

    print(f"scanned {len(names)} repositories\n")
    if not found:
        print("no hazards found")
        return 0

    for kind, items in sorted(by_kind.items(), key=lambda kv: -len(kv[1])):
        print(f"=== {kind}: {len(items)} ===")
        for i in items:
            print(f"  {i['repo']:<28} {i['file']:<20} {i['detail']}")
        print()

    (HERE / "workflow_hazards.json").write_text(
        json.dumps(found, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(found)} hazards -> workflow_hazards.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
