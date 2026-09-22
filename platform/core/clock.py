"""platform.core.clock — the ONE clock (review B20).

Every component reads time through this module: UTC wall-clock for stamps and a
monotonic source for durations. No other module calls ``time``/``datetime`` for
these directly, so the factory has a single, swappable time surface.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone


def now() -> datetime:
    """The current instant as an aware UTC datetime."""
    return datetime.now(timezone.utc)


def now_iso() -> str:
    """The current instant as an ISO-8601 UTC string, second precision."""
    return now().strftime("%Y-%m-%dT%H:%M:%SZ")


def monotonic() -> float:
    """A monotonic clock reading, for measuring durations only."""
    return time.monotonic()


@dataclass
class Timer:
    """Context manager that records a wall duration from a monotonic source."""

    elapsed_s: float = 0.0
    _t0: float = 0.0

    def __enter__(self) -> "Timer":
        self._t0 = time.monotonic()
        return self

    def __exit__(self, *exc: object) -> bool:
        self.elapsed_s = time.monotonic() - self._t0
        return False
