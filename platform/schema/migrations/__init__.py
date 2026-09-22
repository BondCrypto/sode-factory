"""platform.schema.migrations — per-artifact schema migrators.

A migrator is a pure ``from_version -> from_version + 1`` transform registered in
:data:`MIGRATORS`. :func:`plan` reports the chain a stale artifact needs to reach
the current version; :func:`apply` runs that chain. The current version for each
kind is owned by the schema itself (``registry.current_version``), so schema and
migrators cannot silently disagree.
"""
from __future__ import annotations

from typing import Any, Callable

from .. import registry
from . import prediction

# (kind, from_version) -> transform producing the next version.
MIGRATORS: "dict[tuple[str, int], Callable[[dict[str, Any]], dict[str, Any]]]" = {
    ("prediction", 1): prediction.migrate_1_to_2,
}


def artifact_version(data: "dict[str, Any]") -> int:
    """The declared schema_version of an artifact instance (default 1)."""
    return int(data.get("schema_version", 1))


def plan(kind: str, from_version: int) -> "list[tuple[int, int]]":
    """The ordered (from, to) steps to bring ``kind`` from ``from_version`` to current."""
    target = registry.current_version(kind)
    steps: list[tuple[int, int]] = []
    v = from_version
    while v < target:
        if (kind, v) not in MIGRATORS:
            raise KeyError(f"no migrator for {kind!r} {v} -> {v + 1}")
        steps.append((v, v + 1))
        v += 1
    return steps


def apply(kind: str, data: "dict[str, Any]") -> "tuple[dict[str, Any], list[tuple[int, int]]]":
    """Apply every pending migrator to ``data``; return (upgraded, steps_run)."""
    steps = plan(kind, artifact_version(data))
    for frm, _to in steps:
        data = MIGRATORS[(kind, frm)](data)
    return data, steps
