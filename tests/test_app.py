"""Tests for the desktop shell.

The presentation logic (`format_metrics`) is a pure function and is always
tested. The widget tests need a display, so they skip where there is none.

One Tk root is created for the whole module rather than one per test. Creating
and destroying a root repeatedly is slow, and on hosted Windows runners it
intermittently fails to read init.tcl - a flake in the test setup, not in the
code under test.
"""

from __future__ import annotations

import contextlib
import tkinter as tk
from tkinter import ttk

import pytest

from quality_template.core import analyse_text, format_metrics

_DISPLAY: bool | None = None


def display_available() -> bool:
    """Whether a usable Tk *and* ttk are present. Probed once, then remembered.

    Creating a bare `tk.Tk()` is not a sufficient check. Some hosted runners
    ship a Python whose Tcl/Tk tree is incomplete: the root window is created,
    and then sourcing ttk.tcl fails with

        This probably means that tk wasn't installed properly.

    The window uses ttk widgets throughout, so the probe exercises ttk as well;
    otherwise these tests error instead of skipping on such a machine.
    """
    global _DISPLAY
    if _DISPLAY is None:
        root = None
        try:
            root = tk.Tk()
            ttk.Style(root).theme_use("clam")
        except tk.TclError:
            _DISPLAY = False
        else:
            _DISPLAY = True
        finally:
            if root is not None:
                with contextlib.suppress(tk.TclError):
                    root.destroy()
    return _DISPLAY


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


SAMPLE = "The cat sat on the mat. The cat purred."


@pytest.fixture(scope="module")
def app():
    """One window for the whole module."""
    if not display_available():
        pytest.skip("no display available for tkinter")
    from quality_template.app import AnalyserWindow

    window = AnalyserWindow(SAMPLE)
    window.update_idletasks()
    yield window
    window.destroy()


@pytest.fixture
def window(app):
    """The shared window, reset to the sample text before each test."""
    app.input.delete("1.0", "end")
    app.input.insert("1.0", SAMPLE)
    app.analyse()
    app.update_idletasks()
    return app


@pytest.mark.skipif(not display_available(), reason="no display available for tkinter")
class TestAnalyserWindow:
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
