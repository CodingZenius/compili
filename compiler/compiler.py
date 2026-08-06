"""
compiler.py
===========

The single public entry point into the VTC compiler pipeline.

    from compiler import Compiler
    js_code = Compiler().compile(vtc_source)

Nothing outside the `compiler` package -- including the web UI/backend
-- should ever import Lexer, Parser, or Generator directly. Everything
goes through `Compiler.compile()`. This keeps the pipeline internals
free to change without breaking callers, and gives us one place to
guarantee that Python exceptions never leak out as raw tracebacks.
"""

from __future__ import annotations
from .lexer import Lexer
from .parser import Parser
from .generator import Generator
from .errors import IntentError


class Compiler:
    """Orchestrates Lexer -> Parser -> Generator and guarantees friendly errors."""

    def compile(self, source: str) -> str:
        """
        Compile VTC source text into JavaScript source text.

        Raises:
            IntentError: on any lexing, parsing, or generation failure.
                         This is the ONLY exception type this method
                         will ever raise -- unexpected internal errors
                         are also wrapped into an IntentError so the
                         caller never sees a Python traceback.
        """
        try:
            tokens = Lexer(source).tokenize()
            nodes = Parser(tokens).parse()
            js = Generator().generate(nodes)
            return js
        except IntentError:
            raise
        except Exception as exc:  # pragma: no cover - safety net
            raise IntentError(
                message="The compiler hit an unexpected internal error.",
                detail=str(exc),
                title="Compiler Error",
            ) from exc

    def compile_safe(self, source: str) -> dict:
        """
        Compile and return a result dict instead of raising, for callers
        (like the web API) that want uniform success/error handling
        without try/except at every call site.

        Returns:
            {"success": True, "javascript": "..."} or
            {"success": False, "error": {...IntentError.to_dict()...}}
        """
        try:
            js = self.compile(source)
            return {"success": True, "javascript": js}
        except IntentError as err:
            return {"success": False, "error": err.to_dict()}
