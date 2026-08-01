"""Desktop window - the other thin shell over the domain layer.

tkinter is used deliberately: it ships with CPython, so the screenshot step in
CI and the release .exe need no extra GUI dependency.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from quality_template import __version__
from quality_template.core import analyse_text, format_metrics, top_words

SAMPLE = (
    "Quality is not an act, it is a habit. A repository earns trust the same "
    "way: tests that run, documentation that matches the code, and a release "
    "anyone can download and check. Every claim in the README should be "
    "verifiable by running a single command."
)

BG = "#1e1e24"
FG = "#e8e8ee"
ACCENT = "#4c8dff"


class AnalyserWindow(tk.Tk):
    """Paste or open text on the left, read its statistics on the right."""

    def __init__(self, initial: str = SAMPLE) -> None:
        super().__init__()
        self.title(f"Text Analyser {__version__}")
        self.geometry("980x620")
        self.configure(bg=BG)
        self.minsize(760, 480)

        self._build_style()
        self._build_layout()
        self.input.insert("1.0", initial)
        self.analyse()

    def _build_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 13))
        style.configure("Value.TLabel", foreground=ACCENT, font=("Consolas", 11))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure(
            "Treeview",
            background="#26262e",
            fieldbackground="#26262e",
            foreground=FG,
            rowheight=24,
            font=("Consolas", 10),
        )
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10))

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=2)
        root.rowconfigure(1, weight=1)

        ttk.Label(root, text="Input text", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        self.input = tk.Text(
            root,
            wrap="word",
            bg="#26262e",
            fg=FG,
            insertbackground=FG,
            relief="flat",
            padx=10,
            pady=10,
            font=("Consolas", 10),
        )
        self.input.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.input.bind("<KeyRelease>", lambda _event: self.analyse())

        right = ttk.Frame(root)
        right.grid(row=1, column=1, sticky="nsew")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Statistics", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        self.metrics = ttk.Frame(right)
        self.metrics.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.metric_labels: dict[str, ttk.Label] = {}
        for i, name in enumerate(
            (
                "characters",
                "words",
                "unique words",
                "sentences",
                "avg word length",
                "lexical diversity",
                "longest word",
            )
        ):
            ttk.Label(self.metrics, text=name).grid(row=i, column=0, sticky="w", pady=1)
            value = ttk.Label(self.metrics, text="-", style="Value.TLabel")
            value.grid(row=i, column=1, sticky="e", padx=(24, 0))
            self.metrics.columnconfigure(1, weight=1)
            self.metric_labels[name] = value

        self.table = ttk.Treeview(right, columns=("word", "count"), show="headings", height=10)
        self.table.heading("word", text="Word")
        self.table.heading("count", text="Count")
        self.table.column("count", width=70, anchor="e")
        self.table.grid(row=2, column=0, sticky="nsew")

        buttons = ttk.Frame(root)
        buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(buttons, text="Open file...", command=self.open_file).pack(side="left")
        ttk.Button(buttons, text="Clear", command=self.clear).pack(side="left", padx=8)
        self.status = ttk.Label(buttons, text="")
        self.status.pack(side="right")

    def analyse(self) -> None:
        text = self.input.get("1.0", "end-1c")
        stats = analyse_text(text)
        values = format_metrics(stats)
        for name, label in self.metric_labels.items():
            label.configure(text=values[name])

        self.table.delete(*self.table.get_children())
        for word, count in top_words(stats, 12):
            self.table.insert("", "end", values=(word, count))
        self.status.configure(text=f"{stats.words} words analysed")

    def open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Open a text file", filetypes=[("Text files", "*.txt *.md"), ("All files", "*.*")]
        )
        if not path:
            return
        self.input.delete("1.0", "end")
        self.input.insert("1.0", Path(path).read_text(encoding="utf-8", errors="replace"))
        self.analyse()

    def clear(self) -> None:
        self.input.delete("1.0", "end")
        self.analyse()


def run_app(path: Path | None = None) -> int:
    initial = (
        path.read_text(encoding="utf-8", errors="replace") if path and path.is_file() else SAMPLE
    )
    AnalyserWindow(initial).mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(run_app())
