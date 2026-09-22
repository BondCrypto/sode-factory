"""platform.core.paths — locate the repo root.

The root is the nearest ancestor that holds both ``platform/`` and ``bin/`` (the
locked taxonomy, section 1.6). Commands resolve it from the current directory so
``sode`` works from anywhere in the tree.
"""
from __future__ import annotations

from pathlib import Path


def find_repo_root(start: "str | Path | None" = None) -> Path:
    here = Path(start).resolve() if start else Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / "platform").is_dir() and (candidate / "bin").is_dir():
            return candidate
    raise FileNotFoundError(
        "not inside a sode repo (no ancestor has both platform/ and bin/)"
    )
