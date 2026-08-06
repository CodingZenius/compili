"""
errors.py
=========

VTC never shows the end user a raw Python traceback. Every failure in the
pipeline (lexing, parsing, generation) is converted into an `IntentError`
before it leaves the compiler package.

Design decision:
    We intentionally keep this class dead simple (message + optional
    suggestion + optional line number) rather than building a full
    diagnostics framework. VTC is young; a rich diagnostics system
    (spans, multiple errors per pass, warning levels) is future work.
    See context.md -> "Known TODO items".
"""

from __future__ import annotations
from difflib import get_close_matches


class IntentError(Exception):
    """
    The one and only exception type that should ever cross the boundary
    of the compiler package into the web layer or CLI.

    Attributes:
        title:      Short category, e.g. "Intent Error"
        message:    Human-readable explanation of what went wrong.
        detail:     Optional extra context, e.g. the offending token.
        suggestion: Optional "Did you mean...?" hint.
        line:       Optional 1-based line number in the source file.
    """

    def __init__(
        self,
        message: str,
        detail: str | None = None,
        suggestion: str | None = None,
        line: int | None = None,
        title: str = "Intent Error",
    ):
        self.title = title
        self.message = message
        self.detail = detail
        self.suggestion = suggestion
        self.line = line
        super().__init__(self.to_text())

    def to_text(self) -> str:
        """Render a friendly, multi-line, human-readable error message."""
        lines = [self.title]
        if self.line is not None:
            lines.append(f"Line {self.line}")
        lines.append(self.message)
        if self.detail:
            lines.append(self.detail)
        if self.suggestion:
            lines.append(f"Did you mean {self.suggestion}?")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Render as a JSON-friendly dict for the web API."""
        return {
            "title": self.title,
            "message": self.message,
            "detail": self.detail,
            "suggestion": self.suggestion,
            "line": self.line,
        }


def suggest_closest(unknown_word: str, known_words: list[str]) -> str | None:
    """
    Return the closest known keyword to `unknown_word`, if any is close
    enough to be a plausible typo. Powers messages like:

        Intent Error
        Unknown keyword:
        (card_glidee)
        Did you mean:
        (card_glide)
    """
    matches = get_close_matches(unknown_word, known_words, n=1, cutoff=0.6)
    return matches[0] if matches else None


def unknown_keyword_error(keyword: str, known_words: list[str], line: int | None = None) -> IntentError:
    """Build a standard 'unknown keyword' IntentError with a suggestion if possible."""
    suggestion = suggest_closest(keyword, known_words)
    return IntentError(
        message=f"Unknown keyword:\n({keyword})",
        suggestion=f"({suggestion})" if suggestion else None,
        line=line,
    )


def missing_dependency_error(this_keyword: str, requires_keyword: str, before_keyword: str, line: int | None = None) -> IntentError:
    """
    Build the standard dependency-ordering error, e.g.:

        Intent Error
        (button_element)
        requires
        (event_listener)
        before
        (action)
    """
    return IntentError(
        message=f"({this_keyword})\nrequires\n({requires_keyword})\nbefore\n({before_keyword})",
        line=line,
    )
