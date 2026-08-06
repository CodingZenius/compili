"""
main.py
=======

FastAPI backend for the VTC playground web UI.

This file is the ONLY place in the web layer that imports the compiler
package, and it only ever calls `Compiler().compile_safe(source)`.
It never touches Lexer, Parser, or Generator directly -- see
compiler/__init__.py and context.md for why that boundary matters.

Run locally with:

    uvicorn web.main:app --reload

(from the project root, with the project root on PYTHONPATH -- see
README.md "Running locally" for the exact commands).
"""

from __future__ import annotations
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

# Make the top-level `compiler` package importable when this file is run
# directly via `uvicorn web.main:app` from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from compiler import Compiler  # noqa: E402  (import after sys.path fix-up)

app = FastAPI(title="VTC Compiler Playground", version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_compiler = Compiler()


class CompileRequest(BaseModel):
    source: str


class CompileResponse(BaseModel):
    success: bool
    javascript: str | None = None
    error: dict | None = None


@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    """Serve the playground UI."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.post("/api/compile", response_model=CompileResponse)
def compile_vtc(request: CompileRequest) -> CompileResponse:
    """
    Compile VTC source into JavaScript.

    This is the single API surface the frontend talks to. It delegates
    straight to Compiler.compile_safe(), which guarantees a friendly
    IntentError-shaped dict on failure -- never a raw traceback.
    """
    result = _compiler.compile_safe(request.source)
    return CompileResponse(**result)


@app.get("/api/keywords")
def list_keywords() -> dict:
    """
    Expose the language dictionary to the frontend, e.g. for an
    editor autocomplete/help panel. Read-only introspection endpoint.
    """
    from compiler import dictionary

    return {
        "keywords": {
            kw: {
                "category": entry["category"],
                "role": entry["role"],
                "description": entry["description"],
            }
            for kw, entry in dictionary.KEYWORDS.items()
        },
        "events": dictionary.EVENTS,
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
