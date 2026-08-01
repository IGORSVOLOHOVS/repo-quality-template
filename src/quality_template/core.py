"""Text statistics: the domain layer.

Pure functions over plain data, with no I/O and no framework imports. That
separation is what makes the rest of the repository cheap: these functions are
trivial to unit-test, to benchmark and to profile, and the CLI and the GUI are
thin shells that call them.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

WORD_RE = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.UNICODE)
SENTENCE_RE = re.compile(r"[.!?]+(?:\s|$)")

# Words that say nothing about a text's subject; excluded from `top_words`.
STOP_WORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "he",
        "her",
        "his",
        "i",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "she",
        "that",
        "the",
        "their",
        "they",
        "this",
        "to",
        "was",
        "were",
        "will",
        "with",
        "you",
        "your",
        "not",
        "but",
        "if",
    ]
)


@dataclass(frozen=True)
class TextStats:
    """A summary of one piece of text."""

    characters: int
    words: int
    unique_words: int
    sentences: int
    average_word_length: float
    longest_word: str
    frequencies: Counter[str] = field(default_factory=Counter, repr=False)

    @property
    def lexical_diversity(self) -> float:
        """Unique words divided by total words; 0.0 for empty text.

        A higher value means less repetition. Useful as a single number when
        comparing two texts of similar length.
        """
        if self.words == 0:
            return 0.0
        return self.unique_words / self.words


def tokenise(text: str) -> list[str]:
    """Split text into lower-cased word tokens.

    Digits and punctuation are dropped; an internal apostrophe is kept so that
    "don't" stays one token rather than becoming two.
    """
    return [m.group(0).lower() for m in WORD_RE.finditer(text)]


def count_sentences(text: str) -> int:
    """Count sentences by terminal punctuation.

    Text that contains no terminator at all still counts as one sentence, as
    long as it is not blank - otherwise a single unpunctuated line would report
    zero sentences and skew every average derived from it.
    """
    if not text.strip():
        return 0
    found = len(SENTENCE_RE.findall(text))
    return found if found else 1


def analyse_text(text: str) -> TextStats:
    """Produce a :class:`TextStats` for `text`.

    Raises:
        TypeError: if `text` is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")

    tokens = tokenise(text)
    frequencies = Counter(tokens)
    total_length = sum(len(t) for t in tokens)

    return TextStats(
        characters=len(text),
        words=len(tokens),
        unique_words=len(frequencies),
        sentences=count_sentences(text),
        average_word_length=(total_length / len(tokens)) if tokens else 0.0,
        longest_word=max(tokens, key=len) if tokens else "",
        frequencies=frequencies,
    )


def format_metrics(stats: TextStats) -> dict[str, str]:
    """Render a :class:`TextStats` as display-ready label/value pairs.

    Kept here rather than in the GUI so that the rounding rules are testable and
    identical everywhere the numbers are shown.
    """
    return {
        "characters": str(stats.characters),
        "words": str(stats.words),
        "unique words": str(stats.unique_words),
        "sentences": str(stats.sentences),
        "avg word length": f"{stats.average_word_length:.2f}",
        "lexical diversity": f"{stats.lexical_diversity:.3f}",
        "longest word": stats.longest_word or "-",
    }


def top_words(
    stats: TextStats, limit: int = 10, *, drop_stop_words: bool = True
) -> list[tuple[str, int]]:
    """The most frequent words, most common first.

    Args:
        stats: result of :func:`analyse_text`.
        limit: how many entries to return; must be positive.
        drop_stop_words: exclude common function words such as "the" and "of".

    Raises:
        ValueError: if `limit` is not positive.
    """
    if limit <= 0:
        raise ValueError("limit must be positive")

    counts = stats.frequencies
    if drop_stop_words:
        counts = Counter({w: c for w, c in counts.items() if w not in STOP_WORDS})
    return counts.most_common(limit)
