# Manual

## The text analyser

`.\recipe.ps1 run <file>` prints the statistics of a text file: characters, words, unique words, sentences, average word length, lexical diversity, the longest word and the most frequent words.

| Argument | Meaning |
| --- | --- |
| `<file>` | the text to analyse; without it the text is read from standard input |
| `-n`, `--top N` | how many frequent words to show, 10 by default |
| `--keep-stop-words` | count common function words too |
| `--json` | print the statistics as JSON |
| `--gui` | open the desktop window instead |
| `--version` | print the version |

## Applying the layout to another repository

`python scripts/apply_template_to_repo.py --target <folder>` is a dry run: it lists what it would copy and which of the layout's 24 points the target already meets. `--apply` writes the files, and `--force` overwrites files that exist. The workflows and templates come from `template/.github/`.

## The other scripts

| Script | What it does |
| --- | --- |
| `scripts/collect_quality_metrics.py` | measures the ISO 25010 characteristics that a script can measure |
| `scripts/enforce_branch_policy.py` | judges branch names against `[tool.repo-quality]` |
| `scripts/enforce_contribution_policy.py` | judges a pull request's branch, commits and issue link |
| `scripts/profile_application.py` | profiles the analyser on a large input |
| `scripts/generate_sbom.py` | writes a CycloneDX bill of materials |
| `scripts/build_release_artifact.py` | builds the PyInstaller executable and its checksum |
