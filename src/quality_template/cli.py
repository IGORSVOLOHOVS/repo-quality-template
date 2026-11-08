"""Command line interface - a thin shell over :mod:`quality_template.core`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quality_template import __version__
from quality_template.core import TextStats, analyse_text, top_words


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quality-template",
        description="Analyse a text file and report its statistics.",
    )
    parser.add_argument(
        "path", nargs="?", type=Path, help="file to analyse; omit to read standard input"
    )
    parser.add_argument(
        "-n", "--top", type=int, default=10, help="how many frequent words to show (default: 10)"
    )
    parser.add_argument(
        "--keep-stop-words", action="store_true", help="include words such as 'the' and 'of'"
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON instead of a table"
    )
    parser.add_argument(
        "--gui", action="store_true", help="open the desktop window instead of printing"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def read_input(path: Path | None) -> str:
    if path is None:
        return sys.stdin.read()
    if not path.is_file():
        raise SystemExit(f"error: no such file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def render_table(stats: TextStats, words: list[tuple[str, int]]) -> str:
    lines = [
        f"{'characters':<22}{stats.characters}",
        f"{'words':<22}{stats.words}",
        f"{'unique words':<22}{stats.unique_words}",
        f"{'sentences':<22}{stats.sentences}",
        f"{'average word length':<22}{stats.average_word_length:.2f}",
        f"{'lexical diversity':<22}{stats.lexical_diversity:.3f}",
        f"{'longest word':<22}{stats.longest_word}",
    ]
    if words:
        width = max(len(w) for w, _ in words)
        lines.append("")
        lines.append("most frequent words")
        lines += [f"  {w:<{width}}  {c}" for w, c in words]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.gui:
        from quality_template.app import run_app

        return run_app(args.path)

    stats = analyse_text(read_input(args.path))
    words = top_words(stats, args.top, drop_stop_words=not args.keep_stop_words)

    if args.json:
        print(
            json.dumps(
                {
                    "characters": stats.characters,
                    "words": stats.words,
                    "unique_words": stats.unique_words,
                    "sentences": stats.sentences,
                    "average_word_length": round(stats.average_word_length, 4),
                    "lexical_diversity": round(stats.lexical_diversity, 4),
                    "longest_word": stats.longest_word,
                    "top_words": [{"word": w, "count": c} for w, c in words],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(render_table(stats, words))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
