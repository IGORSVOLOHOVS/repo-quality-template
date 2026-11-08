# Install

1. Install [uv](https://docs.astral.sh/uv/) and Python 3.10 or later. Tkinter, which ships with CPython, is needed only for the window.
2. Clone this repository and run `uv sync --frozen` at its root: it installs the pinned toolchain from `uv.lock`.
3. Check the result with `.\recipe.ps1 test`: it runs pytest with the coverage floor, mypy and ruff.

`.\recipe.ps1 build` packs `src/quality_template` into a wheel in `dist\`. The wheel installs a `quality-template` command and needs nothing else at run time.

To reuse the layout on another repository, no install is needed: `python scripts/apply_template_to_repo.py --target <folder> --dry-run` shows what would be copied.
