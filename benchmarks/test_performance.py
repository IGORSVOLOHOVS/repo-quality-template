"""Point 7: benchmarks, so a performance regression shows up as a number.

Run locally with:
    pytest benchmarks --benchmark-only
Compare against a saved baseline with:
    pytest benchmarks --benchmark-only --benchmark-compare
"""

from __future__ import annotations

import pytest

from quality_template.core import analyse_text, tokenise, top_words

PARAGRAPH = (
    "Quality is not an act, it is a habit. A repository earns trust the same "
    "way: tests that run, documentation that matches the code, and a release "
    "anyone can download and verify. "
)


def make_text(paragraphs: int) -> str:
    return PARAGRAPH * paragraphs


@pytest.mark.parametrize("paragraphs", [1, 50, 500])
def test_analyse_text_scales(benchmark, paragraphs):
    text = make_text(paragraphs)
    result = benchmark(analyse_text, text)
    assert result.words > 0


def test_tokenise_throughput(benchmark):
    text = make_text(500)
    tokens = benchmark(tokenise, text)
    assert len(tokens) > 10_000


def test_top_words_is_cheap_after_analysis(benchmark):
    stats = analyse_text(make_text(500))
    result = benchmark(top_words, stats, 20)
    # Repeating one paragraph gives fewer than 20 distinct non-stop words, so the
    # limit is an upper bound here, not the expected count.
    assert 0 < len(result) <= 20
