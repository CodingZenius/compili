"""
sections.py
===========

A .vtc *page* file (e.g. home.vtc) can mix three things in one file:

    ---html---
    <button id="signup">Sign up</button>

    ---css---
    #signup { padding: 8px 16px; }

    ---vtc---
    (button_element=signup)
    (event_listener=click)
    (action=registerUser)

This module ONLY knows how to split that file into its three raw text
sections. It does not understand VTC syntax at all -- the "vtc" section's
text is handed to the real compiler (compiler.Compiler) untouched. This
keeps the existing compiler package exactly as it was; the markers are a
build-time convention layered on top, not a language change.

Rules (kept deliberately simple):
  - A marker line is any line whose stripped text matches
    ---html--- / ---css--- / ---vtc---  (case-insensitive).
  - Everything between one marker and the next belongs to that section.
  - Sections are optional and can appear in any order. A file with no
    markers at all is treated as 100% vtc (so plain old .vtc files, like
    the ones in examples/, still work unchanged).
  - A file can have at most one of each section.
"""

from __future__ import annotations
from dataclasses import dataclass
import re

_MARKER_RE = re.compile(r"^---\s*(html|css|vtc)\s*---$", re.IGNORECASE)


@dataclass
class PageSections:
    html: str = ""
    css: str = ""
    vtc: str = ""


class SectionError(Exception):
    """Raised when a page file uses the section markers incorrectly."""


def split_sections(source: str) -> PageSections:
    lines = source.split("\n")

    # No markers at all -> whole file is VTC (backwards compatible with
    # plain .vtc files that have no HTML/CSS).
    if not any(_MARKER_RE.match(line.strip()) for line in lines):
        return PageSections(vtc=source)

    sections: dict[str, list[str]] = {"html": [], "css": [], "vtc": []}
    current: str | None = None
    seen: set[str] = set()

    for line_no, line in enumerate(lines, start=1):
        match = _MARKER_RE.match(line.strip())
        if match:
            name = match.group(1).lower()
            if name in seen:
                raise SectionError(f"Duplicate '---{name}---' marker at line {line_no}.")
            seen.add(name)
            current = name
            continue

        if current is None:
            if line.strip() != "":
                raise SectionError(
                    f"Line {line_no} appears before any ---html---/---css---/---vtc--- marker."
                )
            continue

        sections[current].append(line)

    return PageSections(
        html="\n".join(sections["html"]).strip("\n"),
        css="\n".join(sections["css"]).strip("\n"),
        vtc="\n".join(sections["vtc"]).strip("\n"),
    )
