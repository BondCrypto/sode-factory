"""platform.core.fs_atomic — atomic file writes.

A write lands whole or not at all: content goes to a temp file in the same
directory, is flushed and fsynced, then ``os.replace``-d over the target. This
keeps on-disk artifacts (records, ledgers, pointers) from ever being read
half-written.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def atomic_write_bytes(path: "str | os.PathLike[str]", data: bytes) -> None:
    """Write ``data`` to ``path`` atomically, creating parent dirs as needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix=".tmp-", suffix=target.name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_text(
    path: "str | os.PathLike[str]", text: str, encoding: str = "utf-8"
) -> None:
    """Write ``text`` to ``path`` atomically."""
    atomic_write_bytes(path, text.encode(encoding))
