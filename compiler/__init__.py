"""
VTC (Virtual Template Code) Compiler Package
=============================================

This package contains the full compiler pipeline for the VTC language:

    Lexer      -> tokenizes raw .vtc source text
    Parser     -> turns tokens into an Abstract Syntax Tree (AST)
    AST        -> node class definitions representing VTC intent
    Dictionary -> data-driven mapping of VTC keywords to JS behaviour
    Generator  -> walks the AST and emits JavaScript
    Errors     -> friendly "Intent Error" reporting (no Python tracebacks)
    Compiler   -> the single public entry point that orchestrates everything

External code (the FastAPI web layer, tests, tools) should ONLY ever
import and call `Compiler.compile(source)` from compiler.py.
Nothing outside this package should talk to Lexer, Parser or Generator
directly. This keeps the pipeline swappable and testable in isolation.
"""

from .compiler import Compiler

__all__ = ["Compiler"]
