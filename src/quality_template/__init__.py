"""A minimal but real application, used to demonstrate the project layout.

The point of the package is not the feature set - it is that every quality
control in this repository has something concrete to act on: tests to run,
functions to benchmark and profile, a CLI to document and a window to screenshot.
"""

from quality_template.core import TextStats, analyse_text, top_words

__all__ = ["TextStats", "analyse_text", "top_words"]
__version__ = "1.0.0"
