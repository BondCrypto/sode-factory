"""platform.core.jsonl — append-only JSONL ledgers.

The factory's ledgers (actions, effects, predictions, events) are append-only
lines of JSON. This module owns the read/append primitives so every ledger is
written and parsed the same way.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterator


def append(path: "str | os.PathLike[str]", obj: "dict[str, Any]") -> None:
    """Append one object as a JSON line, creating parent dirs as needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    with open(target, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def iter_rows(path: "str | os.PathLike[str]") -> Iterator["dict[str, Any]"]:
    """Yield each JSON object in the ledger; blank lines are skipped."""
    target = Path(path)
    if not target.exists():
        return
    with open(target, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def read(path: "str | os.PathLike[str]") -> "list[dict[str, Any]]":
    """Read all rows of the ledger into a list."""
    return list(iter_rows(path))
