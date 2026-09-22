"""tests.core.test_ids — id + short-hash primitives (platform.core.ids)."""
from __future__ import annotations

import time

from platform.core import ids


def test_new_id_carries_prefix():
    assert ids.new_id("it_").startswith("it_")
    bare = ids.new_id()  # empty prefix is allowed
    assert bare and bare.isalnum()


def test_new_id_is_unique_across_a_burst():
    seen = {ids.new_id("x") for _ in range(1000)}
    assert len(seen) == 1000


def test_new_id_is_time_sortable():
    a = ids.new_id("p")
    time.sleep(0.002)
    b = ids.new_id("p")
    # Same prefix + fixed-width base36 microsecond stamp => later id sorts later.
    assert a < b


def test_short_hash_is_stable_and_truncated():
    assert ids.short_hash("hello") == ids.short_hash(b"hello")
    assert len(ids.short_hash("hello", 8)) == 8
    assert ids.short_hash("a") != ids.short_hash("b")
