"""
lexer.py
========

Turns raw VTC source text into a flat list of Token objects.

VTC's surface syntax is deliberately tiny. A VTC program is a sequence
of "intent statements" that look like:

    (keyword=value)
    (keyword)
    import(graphics)

Each statement is a parenthesized expression, optionally with a
`keyword=value` pair inside. Statements are grouped into blocks by
blank-line separation (a "block" describes one coherent piece of UI
behaviour, e.g. one button's full click handler).

The lexer does NOT understand keyword meaning at all -- that is the
Parser's (structure) and Dictionary's (meaning) job. The lexer only
understands punctuation and shape:

    LPAREN      (
    RPAREN      )
    EQUALS      =
    IDENT       keyword or value text
    IMPORT      the literal word 'import' immediately before '('
    NEWLINE     a blank line (block separator)
    EOF         end of file

Comments start with '#' and run to end of line.
"""

from __future__ import annotations
from dataclasses import dataclass
from .errors import IntentError


@dataclass
class Token:
    kind: str
    value: str
    line: int

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.value!r}, line={self.line})"


_IDENT_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./:-"
)


class Lexer:
    """Converts VTC source text into a list of Tokens."""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.length = len(source)

    def tokenize(self) -> list[Token]:
        """
        Two-pass-ish strategy: first strip comments and split the source
        into physical lines, classify each line as blank or non-blank,
        then tokenize non-blank lines and emit exactly one NEWLINE token
        per *run* of one-or-more blank lines (block separator).
        """
        tokens: list[Token] = []
        raw_lines = self.source.split("\n")

        prev_line_had_content = False
        pending_separator = False  # a run of blank line(s) is waiting to be emitted

        for line_no, raw_line in enumerate(raw_lines, start=1):
            self.line = line_no
            line = self._strip_comment(raw_line)
            stripped = line.strip()

            if stripped == "":
                if prev_line_had_content:
                    pending_separator = True
                prev_line_had_content = False
                continue

            # non-blank line: if a separator was pending, emit it first
            if pending_separator:
                tokens.append(Token("NEWLINE", "\\n", line_no - 1))
                pending_separator = False

            tokens.extend(self._tokenize_line(line, line_no))
            prev_line_had_content = True

        tokens.append(Token("EOF", "", len(raw_lines)))
        return tokens

    @staticmethod
    def _strip_comment(line: str) -> str:
        """Remove a '#' comment (outside of nothing fancy -- VTC has no strings)."""
        idx = line.find("#")
        return line if idx == -1 else line[:idx]

    def _tokenize_line(self, line: str, line_no: int) -> list[Token]:
        tokens: list[Token] = []
        pos = 0
        length = len(line)

        while pos < length:
            ch = line[pos]

            if ch in (" ", "\t", "\r"):
                pos += 1
                continue

            if ch == "(":
                tokens.append(Token("LPAREN", "(", line_no))
                pos += 1
                continue

            if ch == ")":
                tokens.append(Token("RPAREN", ")", line_no))
                pos += 1
                continue

            if ch == "=":
                tokens.append(Token("EQUALS", "=", line_no))
                pos += 1
                continue

            if ch in _IDENT_CHARS:
                start = pos
                while pos < length and line[pos] in _IDENT_CHARS:
                    pos += 1
                text = line[start:pos]
                if text == "import":
                    tokens.append(Token("IMPORT", text, line_no))
                else:
                    tokens.append(Token("IDENT", text, line_no))
                continue

            raise IntentError(
                message=f"Unexpected character: '{ch}'",
                line=line_no,
            )

        return tokens
