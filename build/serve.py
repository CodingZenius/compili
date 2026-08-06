"""
serve.py
========

A tiny static file server for `dist/`, built entirely on Python's
standard library (`http.server`). No Flask/FastAPI dependency for this --
dist/ is just plain HTML/CSS/JS at this point, so a plain static server
is all it needs.
"""

from __future__ import annotations
import functools
import http.server
from pathlib import Path

from build.build import DEFAULT_DIST_DIR


def serve(dist_dir: Path = DEFAULT_DIST_DIR, port: int = 8080) -> None:
    """Serve dist_dir over HTTP at http://127.0.0.1:<port> until Ctrl+C."""
    if not dist_dir.exists():
        print(f"[serve] {dist_dir} does not exist yet -- run build() first.")
        return

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(dist_dir))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)

    print(f"[serve] serving {dist_dir} at http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[serve] stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    serve()
