"""
cli.py
======

Command-line entry point for the build system.

    python -m build.cli build   # compile pages/*.vtc -> dist/ once
    python -m build.cli watch   # build, then rebuild on every change
    python -m build.cli serve   # serve dist/ at http://127.0.0.1:8080

`watch` and `serve` are separate commands (not combined) so you can run
them in two terminals during development -- one rebuilding, one serving --
which keeps each script doing exactly one job.
"""

from __future__ import annotations
import sys

from build.build import build_all
from build.watch import watch
from build.serve import serve


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    command = argv[0] if argv else "build"

    if command == "build":
        results = build_all()
        if not results:
            print("No .vtc pages found in pages/.")
            return 0
        failures = 0
        for result in results:
            if result.success:
                names = ", ".join(p.name for p in result.outputs)
                print(f"[build] {result.page}.vtc -> {names}")
            else:
                failures += 1
                print(f"[build] {result.page}.vtc FAILED: {result.error}")
        return 1 if failures else 0

    if command == "watch":
        watch()
        return 0

    if command == "serve":
        port = int(argv[1]) if len(argv) > 1 else 8080
        serve(port=port)
        return 0

    print(f"Unknown command: {command!r}. Use build, watch, or serve.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
