"""platform.cli.registry — load and query the CLI verb registry.

The registry (``registry.yaml``) is the authority for every ``sode`` verb. The
dispatcher refuses a verb that is not registered; a test asserts every ``stable``
verb has a real handler and every ``planned`` verb routes to the planned handler.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REGISTRY_PATH = Path(__file__).resolve().parent / "registry.yaml"

REQUIRED_VERB_KEYS = ("verb", "owner_component", "session", "stability", "profiles", "reads", "writes")
STABILITIES = ("stable", "planned")


@lru_cache(maxsize=1)
def _load() -> "dict[str, Any]":
    return yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))


def verbs() -> "list[dict[str, Any]]":
    return list(_load().get("verbs", []))


def binaries() -> "list[dict[str, Any]]":
    return list(_load().get("binaries", []))


def verb_names() -> "list[str]":
    return [v["verb"] for v in verbs()]


def get(verb: str) -> "dict[str, Any] | None":
    for v in verbs():
        if v["verb"] == verb:
            return v
    return None
