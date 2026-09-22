"""platform.core.ids — id and short-hash primitives.

sode uses its OWN id scheme; a fresh clone must be free of any other repo's id
namespaces (architecture section 1.4(3)). Ids here are opaque, lexically
sortable by creation time, and carry a caller-chosen prefix.
"""
from __future__ import annotations

import hashlib
import os
import time

_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


def _b36(n: int) -> str:
    if n == 0:
        return "0"
    out = []
    while n > 0:
        n, rem = divmod(n, 36)
        out.append(_ALPHABET[rem])
    return "".join(reversed(out))


def new_id(prefix: str = "") -> str:
    """A time-sortable id: ``<prefix><base36 microseconds><4 random chars>``.

    The prefix is the caller's namespace (for example a component's own tag);
    it must not reuse another system's id namespace.
    """
    stamp = _b36(int(time.time() * 1_000_000))
    rand = _b36(int.from_bytes(os.urandom(3), "big")).rjust(4, "0")[:4]
    return f"{prefix}{stamp}{rand}"


def short_hash(data: "bytes | str", length: int = 12) -> str:
    """A short, stable content hash (sha256, hex-truncated)."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:length]
