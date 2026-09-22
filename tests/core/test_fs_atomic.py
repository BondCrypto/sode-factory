"""tests.core.test_fs_atomic — atomic writes (platform.core.fs_atomic)."""
from __future__ import annotations

from platform.core import fs_atomic


def test_write_text_creates_parents_and_content(tmp_path):
    target = tmp_path / "a" / "b" / "c.txt"
    fs_atomic.atomic_write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"


def test_write_overwrites_whole(tmp_path):
    target = tmp_path / "x.txt"
    fs_atomic.atomic_write_text(target, "first")
    fs_atomic.atomic_write_text(target, "second")
    assert target.read_text(encoding="utf-8") == "second"


def test_no_temp_files_left_behind(tmp_path):
    target = tmp_path / "y.bin"
    fs_atomic.atomic_write_bytes(target, b"\x00\x01\x02")
    leftovers = [p.name for p in tmp_path.iterdir() if p.name.startswith(".tmp-")]
    assert leftovers == []
    assert target.read_bytes() == b"\x00\x01\x02"
