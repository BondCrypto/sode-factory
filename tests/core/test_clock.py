"""tests.core.test_clock — the one clock (platform.core.clock)."""
from __future__ import annotations

import re

from platform.core import clock


def test_now_is_utc_aware():
    dt = clock.now()
    assert dt.tzinfo is not None
    assert dt.utcoffset().total_seconds() == 0


def test_now_iso_shape():
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", clock.now_iso())


def test_monotonic_never_decreases():
    a = clock.monotonic()
    b = clock.monotonic()
    assert b >= a


def test_timer_records_a_nonnegative_duration():
    with clock.Timer() as t:
        pass
    assert t.elapsed_s >= 0.0
