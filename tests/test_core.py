"""Tests for the domain layer."""

from __future__ import annotations

import pytest

from quality_template.core import (
    STOP_WORDS,
    analyse_text,
    count_sentences,
    tokenise,
    top_words,
)


class TestTokenise:
    def test_lowercases_and_drops_punctuation(self):
        assert tokenise("Hello, World!") == ["hello", "world"]

    def test_keeps_internal_apostrophe(self):
        assert tokenise("don't stop") == ["don't", "stop"]

    def test_drops_digits(self):
        assert tokenise("abc 123 def4") == ["abc", "def"]

    def test_handles_non_ascii(self):
        assert tokenise("naïve café") == ["naïve", "café"]

    def test_empty(self):
        assert tokenise("") == []


class TestCountSentences:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("One. Two. Three.", 3),
            ("Really? Yes! Sure.", 3),
            ("No terminator here", 1),
            ("", 0),
            ("   \n  ", 0),
            ("Ellipsis... then more.", 2),
        ],
    )
    def test_counts(self, text, expected):
        assert count_sentences(text) == expected


class TestAnalyseText:
    def test_basic_counts(self):
        stats = analyse_text("The cat sat. The cat slept.")
        assert stats.words == 6
        assert stats.unique_words == 4
        assert stats.sentences == 2
        assert stats.characters == len("The cat sat. The cat slept.")

    def test_longest_word(self):
        assert analyse_text("a bb cccc dd").longest_word == "cccc"

    def test_average_word_length(self):
        # "ab" + "cde" -> (2 + 3) / 2
        assert analyse_text("ab cde").average_word_length == pytest.approx(2.5)

    def test_empty_text_is_all_zero(self):
        stats = analyse_text("")
        assert (stats.words, stats.unique_words, stats.sentences) == (0, 0, 0)
        assert stats.average_word_length == 0.0
        assert stats.longest_word == ""
        assert stats.lexical_diversity == 0.0

    def test_lexical_diversity(self):
        assert analyse_text("a b c d").lexical_diversity == pytest.approx(1.0)
        assert analyse_text("a a a a").lexical_diversity == pytest.approx(0.25)

    def test_rejects_non_string(self):
        with pytest.raises(TypeError, match="expected str"):
            analyse_text(42)

    def test_stats_are_immutable(self):
        stats = analyse_text("hello")
        with pytest.raises(AttributeError):
            stats.words = 99


class TestTopWords:
    def test_orders_by_frequency(self):
        stats = analyse_text("apple apple apple pear pear fig")
        assert top_words(stats, 2) == [("apple", 3), ("pear", 2)]

    def test_drops_stop_words_by_default(self):
        stats = analyse_text("the the the signal")
        assert [w for w, _ in top_words(stats)] == ["signal"]

    def test_can_keep_stop_words(self):
        stats = analyse_text("the the the signal")
        assert top_words(stats, 1, drop_stop_words=False) == [("the", 3)]

    def test_limit_is_respected(self):
        stats = analyse_text("alpha beta gamma delta epsilon")
        assert len(top_words(stats, 3)) == 3

    def test_rejects_non_positive_limit(self):
        stats = analyse_text("anything")
        with pytest.raises(ValueError, match="must be positive"):
            top_words(stats, 0)

    def test_text_of_only_stop_words_yields_nothing(self):
        assert top_words(analyse_text("the of and")) == []

    def test_stop_words_are_lowercase(self):
        # tokenise() lowercases, so an upper-case entry would never match.
        assert all(w == w.lower() for w in STOP_WORDS)
