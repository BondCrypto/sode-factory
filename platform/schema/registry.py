"""platform.schema.registry — the artifact-schema registry.

Every artifact that carries ``schema_version`` has a schema file here. This
module loads those schemas, reports each kind's CURRENT version (read from the
schema's ``schema_version`` constraint, the single source of truth), and maps the
well-known on-disk artifacts to their kind so ``doctor`` and ``migrate`` can walk
them.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_SCHEMA_DIR = Path(__file__).resolve().parent

# kind -> schema filename (all live in platform/schema/).
SCHEMA_FILES = {
    "factory": "factory.schema.json",
    "active": "active.schema.json",
    "local": "local.schema.json",
    "prediction": "prediction.schema.json",
    "port_manifest": "port_manifest.schema.json",
    "item": "item.schema.json",
    "events": "events.schema.json",
    "record": "record.schema.json",
    "trajectory": "trajectory.schema.json",
    "gate": "gate.schema.json",
}

# Well-known artifacts `migrate --check` (no --path) and `doctor` scan, relative
# to the repo root. Only the artifacts C0 emits exist at S1; the rest are absent
# until their owning component lands, and a missing artifact is simply skipped.
WELL_KNOWN_PATHS = {
    "factory.yaml": "factory",
    ".sode/active.json": "active",
    ".sode/local.yaml": "local",
    ".sode/predictions.jsonl": "prediction",
}

# Filename stem -> kind, for inferring a kind from a --path argument.
FILENAME_KIND = {
    "factory": "factory",
    "active": "active",
    "local": "local",
    "prediction": "prediction",
    "predictions": "prediction",
}


@lru_cache(maxsize=None)
def load_schema(kind: str) -> "dict[str, Any]":
    """Load and cache the JSON Schema for ``kind``."""
    if kind not in SCHEMA_FILES:
        raise KeyError(f"unknown artifact kind {kind!r}; known: {sorted(SCHEMA_FILES)}")
    return json.loads((_SCHEMA_DIR / SCHEMA_FILES[kind]).read_text(encoding="utf-8"))


def schema_path(kind: str) -> Path:
    return _SCHEMA_DIR / SCHEMA_FILES[kind]


def current_version(kind: str) -> int:
    """The current schema_version for ``kind``, read from the schema itself."""
    schema = load_schema(kind)
    sv = schema.get("properties", {}).get("schema_version", {})
    if "const" in sv:
        return int(sv["const"])
    if "enum" in sv:
        return int(max(sv["enum"]))
    raise ValueError(f"schema for {kind!r} does not pin schema_version")


def current_versions() -> "dict[str, int]":
    return {kind: current_version(kind) for kind in SCHEMA_FILES}


def all_schema_files() -> "list[Path]":
    return [_SCHEMA_DIR / name for name in SCHEMA_FILES.values()]


def kind_for_filename(name: str) -> "str | None":
    """Infer a kind from a file's basename stem (drops .yaml/.json/.jsonl).

    Falls back to the first ``_``-delimited segment so the ``<kind>_v<N>`` fixture
    naming resolves (for example ``prediction_v1.jsonl`` -> ``prediction``).
    """
    stem = Path(name).name
    for suffix in (".jsonl", ".yaml", ".yml", ".json"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    if stem in FILENAME_KIND:
        return FILENAME_KIND[stem]
    return FILENAME_KIND.get(stem.split("_", 1)[0])
