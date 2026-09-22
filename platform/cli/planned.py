"""The handler for registered-but-not-yet-implemented (``planned``) verbs.

Every v1 verb is in the registry from S1; only C0's four are implemented. A
planned verb names its owning component and the session that lands it, then exits
non-zero so callers never mistake it for a completed action.
"""
from __future__ import annotations

from . import registry

PLANNED_EXIT = 2


def planned_handler(verb: str, argv: "list[str]") -> int:
    entry = registry.get(verb)
    owner = entry.get("owner_component", "?") if entry else "?"
    session = entry.get("session", "?") if entry else "?"
    print(
        f"sode {verb}: not yet implemented (planned). "
        f"Owned by {owner}; lands in session {session}."
    )
    return PLANNED_EXIT
