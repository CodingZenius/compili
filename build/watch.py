"""
watch.py
========

A minimal, dependency-free file watcher. Polls the mtimes of every
`.vtc` file under `pages/` and reruns `build_all()` whenever any of them
change. No `watchdog`/`inotify` dependency -- keeps the build system's
footprint small, at the cost of a small poll interval instead of instant
OS-level file events. Fine for a local dev loop.
"""

from __future__ import annotations
import time
from pathlib import Path

from build.build import build_all, DEFAULT_SRC_DIR, DEFAULT_DIST_DIR


def _snapshot(src_dir: Path) -> dict[Path, float]:
    """Map each .vtc file to its last-modified time."""
    if not src_dir.exists():
        return {}
    return {p: p.stat().st_mtime for p in src_dir.glob("*.vtc")}


def watch(src_dir: Path = DEFAULT_SRC_DIR, dist_dir: Path = DEFAULT_DIST_DIR, interval: float = 0.5) -> None:
    """Build once immediately, then rebuild whenever a .vtc file changes. Runs until Ctrl+C."""
    print(f"[watch] watching {src_dir} (checking every {interval}s, Ctrl+C to stop)")
    _run_and_report(src_dir, dist_dir)

    last_snapshot = _snapshot(src_dir)
    try:
        while True:
            time.sleep(interval)
            current_snapshot = _snapshot(src_dir)
            if current_snapshot != last_snapshot:
                changed = _describe_change(last_snapshot, current_snapshot)
                print(f"[watch] change detected ({changed}) -- rebuilding")
                _run_and_report(src_dir, dist_dir)
                last_snapshot = current_snapshot
    except KeyboardInterrupt:
        print("\n[watch] stopped")


def _describe_change(old: dict[Path, float], new: dict[Path, float]) -> str:
    added = new.keys() - old.keys()
    removed = old.keys() - new.keys()
    if added:
        return f"added {sorted(p.name for p in added)}"
    if removed:
        return f"removed {sorted(p.name for p in removed)}"
    changed = [p.name for p in new if p in old and new[p] != old[p]]
    return f"modified {sorted(changed)}"


def _run_and_report(src_dir: Path, dist_dir: Path) -> None:
    results = build_all(src_dir, dist_dir)
    if not results:
        print(f"[watch] no .vtc pages found in {src_dir}")
        return
    for result in results:
        if result.success:
            names = ", ".join(p.name for p in result.outputs)
            print(f"[build] {result.page}.vtc -> {names}")
        else:
            print(f"[build] {result.page}.vtc FAILED: {result.error}")


if __name__ == "__main__":
    watch()
