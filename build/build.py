"""
build.py
========

The core build step. Turns every page file under `pages/` (or whatever
source directory you point it at) into a browser-ready output in `dist/`:

    pages/home.vtc  ->  dist/home.html
                         dist/home.css   (only if the page had a css section)
                         dist/home.js    (only if the page had a vtc section)

This file does NOT reimplement or modify the VTC compiler. The only line
that touches language semantics is the call to `Compiler().compile_safe()`
in `compile_page()` below -- everything else here is file I/O and string
stitching (splitting page files into html/css/vtc via sections.py, and
wiring the three outputs together with <link>/<script> tags).

Usage (see cli.py for the command-line wrapper):

    from build.build import build_all
    results = build_all()
"""

from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path

# Make the project root importable so `from compiler import Compiler` works
# no matter where this script is invoked from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from compiler import Compiler  # noqa: E402
from build.sections import split_sections, SectionError  # noqa: E402

DEFAULT_SRC_DIR = PROJECT_ROOT / "pages"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist"

_compiler = Compiler()


@dataclass
class BuildResult:
    page: str                 # e.g. "home"
    success: bool
    outputs: list[Path]       # files written, on success
    error: str | None = None  # human-readable message, on failure


def build_all(src_dir: Path = DEFAULT_SRC_DIR, dist_dir: Path = DEFAULT_DIST_DIR) -> list[BuildResult]:
    """Compile every .vtc page under src_dir into dist_dir. Returns one BuildResult per page."""
    dist_dir.mkdir(parents=True, exist_ok=True)

    if not src_dir.exists():
        return []

    results = []
    for page_path in sorted(src_dir.glob("*.vtc")):
        results.append(build_page(page_path, dist_dir))
    return results


def build_page(page_path: Path, dist_dir: Path = DEFAULT_DIST_DIR) -> BuildResult:
    """Compile a single .vtc page file into dist_dir. Never raises -- errors come back in BuildResult."""
    page_name = page_path.stem
    dist_dir.mkdir(parents=True, exist_ok=True)

    try:
        source = page_path.read_text(encoding="utf-8")
        sections = split_sections(source)
    except SectionError as exc:
        return BuildResult(page=page_name, success=False, outputs=[], error=str(exc))
    except OSError as exc:
        return BuildResult(page=page_name, success=False, outputs=[], error=f"Could not read {page_path}: {exc}")

    js_result = _compiler.compile_safe(sections.vtc) if sections.vtc.strip() else {"success": True, "javascript": ""}

    if not js_result["success"]:
        err = js_result["error"]
        message = err["message"]
        if err.get("suggestion"):
            message += f" (did you mean {err['suggestion']}?)"
        if err.get("line") is not None:
            message = f"line {err['line']}: {message}"
        return BuildResult(page=page_name, success=False, outputs=[], error=message)

    outputs = _write_outputs(page_name, sections, js_result["javascript"], dist_dir)
    return BuildResult(page=page_name, success=True, outputs=outputs)


def _write_outputs(page_name: str, sections, javascript: str, dist_dir: Path) -> list[Path]:
    """Write the .html/.css/.js files for one page and return the paths written."""
    outputs: list[Path] = []
    has_css = sections.css.strip() != ""
    has_js = javascript.strip() != ""

    if has_css:
        css_path = dist_dir / f"{page_name}.css"
        css_path.write_text(sections.css + "\n", encoding="utf-8")
        outputs.append(css_path)

    if has_js:
        js_path = dist_dir / f"{page_name}.js"
        js_path.write_text(javascript, encoding="utf-8")
        outputs.append(js_path)

    html_path = dist_dir / f"{page_name}.html"
    html_path.write_text(
        _render_html(page_name, sections.html, has_css, has_js),
        encoding="utf-8",
    )
    outputs.append(html_path)

    return outputs


def _render_html(page_name: str, body_html: str, has_css: bool, has_js: bool) -> str:
    """Wrap the page's html section in a minimal document, linking css/js if present."""
    css_tag = f'  <link rel="stylesheet" href="{page_name}.css" />\n' if has_css else ""
    js_tag = f'  <script src="{page_name}.js" defer></script>\n' if has_js else ""

    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="UTF-8" />\n'
        f"  <title>{page_name}</title>\n"
        f"{css_tag}"
        "</head>\n"
        "<body>\n"
        f"{body_html}\n"
        f"{js_tag}"
        "</body>\n"
        "</html>\n"
    )
