"""Tests for the desktop shell.

The presentation logic (`format_metrics`) is a pure function and is always
tested. The widget wiring needs a display, so those tests skip where there is
none - a headless CI runner without an X server, for instance.
"""

from __future__ import annotations

import tkinter as tk

import pytest

from quality_template.core import analyse_text, format_metrics


def display_available() -> bool:
    try:
        root = tk.Tk()
    except tk.TclError:
        return False
    root.destroy()
    return True


class TestFormatMetrics:
    def test_all_labels_present(self):
        values = format_metrics(analyse_text("The cat sat."))
        assert set(values) == {
            "characters",
            "words",
            "unique words",
            "sentences",
            "avg word length",
            "lexical diversity",
            "longest word",
        }

    def test_every_value_is_a_string(self):
        assert all(isinstance(v, str) for v in format_metrics(analyse_text("hi")).values())

    def test_rounding(self):
        values = format_metrics(analyse_text("ab cde"))
        assert values["avg word length"] == "2.50"
        assert values["lexical diversity"] == "1.000"

    def test_empty_text_shows_dash_for_longest_word(self):
        assert format_metrics(analyse_text(""))["longest word"] == "-"

    def test_counts_match_the_stats(self):
        stats = analyse_text("one two two three three three.")
        values = format_metrics(stats)
        assert values["words"] == str(stats.words)
        assert values["unique words"] == str(stats.unique_words)


@pytest.mark.skipif(not display_available(), reason="no display available for tkinter")
class TestAnalyserWindow:
    @pytest.fixture
    def window(self):
        from quality_template.app import AnalyserWindow

        win = AnalyserWindow("The cat sat on the mat. The cat purred.")
        win.update_idletasks()
        yield win
        win.destroy()

    def test_opens_with_the_given_text(self, window):
        assert "cat sat" in window.input.get("1.0", "end-1c")

    def test_metrics_are_populated(self, window):
        assert window.metric_labels["words"].cget("text") == "9"

    def test_table_lists_frequent_words(self, window):
        rows = [window.table.item(i)["values"] for i in window.table.get_children()]
        assert rows and rows[0][0] == "cat"

    def test_reanalyses_after_editing(self, window):
        window.input.delete("1.0", "end")
        window.input.insert("1.0", "alpha beta gamma")
        window.analyse()
        assert window.metric_labels["words"].cget("text") == "3"

    def test_clear_empties_everything(self, window):
        window.clear()
        assert window.metric_labels["words"].cget("text") == "0"
        assert window.table.get_children() == ()

    def test_status_reports_word_count(self, window):
        assert "9 words" in window.status.cget("text")
