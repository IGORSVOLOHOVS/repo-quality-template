"""Roll this template out onto an existing repository.

    python scripts/apply_template_to_repo.py --target C:\\path\\to\\repo --dry-run
    python scripts/apply_template_to_repo.py --target C:\\path\\to\\repo --apply

Copies the infrastructure - workflows, lint config, scripts, licence, document
skeletons - and leaves the target's own source code alone. Files that already
exist are never overwritten unless --force is given; instead they are listed so
the difference can be looked at deliberately.

A report of which of the 24 standard points the target satisfies is printed at
the end, so it is obvious what still has to be done by hand.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent

# Copied as-is. Everything here is project-independent infrastructure.
INFRASTRUCTURE = [
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    ".github/workflows/branch-policy.yml",
    ".github/workflows/contribution-policy.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/task.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/CODEOWNERS",
    ".github/dependabot.yml",
    ".pre-commit-config.yaml",
    "LICENSE",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "scripts/install_dependencies.py",
    "scripts/build_release_artifact.py",
    "scripts/collect_quality_metrics.py",
    "scripts/profile_application.py",
    "scripts/enforce_branch_policy.py",
    "scripts/enforce_contribution_policy.py",
    "scripts/generate_sbom.py",
    "scripts/capture_usage_screenshots.py",
    "docs/branching.md",
    "docs/workflow.md",
]

# Copied only as a starting point - they describe the project and must be edited.
SKELETONS = [
    "docs/architecture.md",
    "docs/quality-iso25010.md",
    "docs/decisions.md",
    "CHANGELOG.md",
]

# The 24 points of the standard, and how to detect each one automatically.
#
# A point is either a path that has to exist, a marker that has to appear in
# pyproject.toml, or a judgement no script can make. The first two are checked
# here; the third is named so it cannot be forgotten.
CHECKS: list[tuple[str, str | None]] = [
    ("1. CI/CD", ".github/workflows/ci.yml"),
    ("2. Documentation", "README.md"),
    ("3. Tests", "tests"),
    ("4. Architecture", "docs/architecture.md"),
    ("5. Licence with your name", "LICENSE"),
    ("6. Build script", "scripts/build_release_artifact.py"),
    ("7. Benchmarks", "benchmarks"),
    ("8. ISO 25010 assessment", "docs/quality-iso25010.md"),
    ("9. Automatic formatting", ".pre-commit-config.yaml"),
    ("10. Dependency install script", "scripts/install_dependencies.py"),
    ("11. Usage screenshots", "docs/screenshots"),
    ("12. English throughout", None),  # judgement, not a file
    ("13. Release artefacts", ".github/workflows/release.yml"),
    ("14. Three long-lived branches", None),  # checked via git
    ("15. Issue templates", ".github/ISSUE_TEMPLATE"),
    ("16. Pull request template", ".github/PULL_REQUEST_TEMPLATE.md"),
    ("17. Contribution policy in CI", ".github/workflows/contribution-policy.yml"),
    ("18. Reviewers declared once", ".github/CODEOWNERS"),
    ("19. Type checking", "pyproject.toml::[tool.mypy]"),
    ("20. SBOM per release", "scripts/generate_sbom.py"),
    ("21. Dependency monitoring", ".github/dependabot.yml"),
    ("22. Security policy", "SECURITY.md"),
    ("23. Code of conduct", "CODE_OF_CONDUCT.md"),
    ("24. Divergences recorded", "docs/decisions.md"),
]


def copy(rel: str, target: Path, force: bool, dry: bool) -> str:
    src, dst = TEMPLATE / rel, target / rel
    if not src.exists():
        return f"MISSING IN TEMPLATE  {rel}"
    if dst.exists() and not force:
        return f"exists, skipped      {rel}"
    if not dry:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return f"{'would copy' if dry else 'copied':<20} {rel}"


def branch_report(target: Path) -> str:
    if not (target / ".git").exists():
        return "not a git repository"
    out = subprocess.run(
        ["git", "branch", "-a", "--format=%(refname:short)"],
        cwd=target,
        capture_output=True,
        text=True,
    ).stdout
    names = {b.strip().replace("origin/", "") for b in out.splitlines() if b.strip()}
    names.discard("HEAD")
    extra = sorted(n for n in names if n not in ("release", "dev", "test"))
    return "release, dev, test only" if not extra else f"extra branches: {', '.join(extra)}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="write files (default is a dry run)")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.is_dir():
        raise SystemExit(f"no such directory: {target}")
    dry = not args.apply

    print(f"{'DRY RUN - nothing written' if dry else 'APPLYING'} -> {target}\n")

    print("infrastructure:")
    for rel in INFRASTRUCTURE:
        print(f"  {copy(rel, target, args.force, dry)}")

    print("\nskeletons (edit these afterwards - they describe THIS project):")
    for rel in SKELETONS:
        print(f"  {copy(rel, target, args.force, dry)}")

    print("\nstandard compliance after this step:")
    for label, probe in CHECKS:
        if probe is None:
            state = "by hand" if label.startswith("12") else branch_report(target)
        elif "::" in probe:
            path, marker = probe.split("::", 1)
            candidate = target / path
            found = candidate.is_file() and marker in candidate.read_text(
                encoding="utf-8", errors="replace"
            )
            state = "yes" if found else "NO"
        else:
            state = "yes" if (target / probe).exists() else "NO"
        print(f"  {label:<32} {state}")

    print("\nstill to do by hand:")
    print("  - README.md: what it is, how to run it, screenshots")
    print("  - docs/architecture.md and docs/quality-iso25010.md: rewrite for this project")
    print("  - tests/ and benchmarks/: this template cannot invent them")
    print("  - build_release_artifact.py: point ENTRY at the real entry point")
    print("  - python scripts/capture_usage_screenshots.py")
    print("  - python scripts/enforce_branch_policy.py --remote origin")
    print("  - pyproject.toml: add [tool.repo-quality] with this project's code")
    print("  - pyproject.toml: add [tool.mypy] and put mypy in the dev extras")
    print("  - docs/decisions.md: record what this project deliberately does not do")
    print("  - branch protection: require CI, require review from CODEOWNERS")
    if dry:
        print("\nre-run with --apply to write these files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
