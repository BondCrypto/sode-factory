"""platform.config.loader — read/write the factory's config artifacts.

``factory.yaml`` is the versioned definition (in git); ``.sode/local.yaml`` binds
it to this machine; ``.sode/active.json`` points at the active harness. This
module centralises their locations and their (atomic) serialisation. PyYAML is
the single config dependency (stdlib-first everywhere else); see requirements.txt.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from ..core import fs_atomic


def factory_path(root: "str | Path") -> Path:
    return Path(root) / "factory.yaml"


def local_path(root: "str | Path") -> Path:
    return Path(root) / ".sode" / "local.yaml"


def active_path(root: "str | Path") -> Path:
    return Path(root) / ".sode" / "active.json"


def load_yaml(path: "str | Path") -> Any:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def dump_yaml(obj: Any) -> str:
    return yaml.safe_dump(obj, sort_keys=False, default_flow_style=False, allow_unicode=True)


def write_yaml_atomic(path: "str | Path", obj: Any, header: "str | None" = None) -> None:
    text = dump_yaml(obj)
    if header:
        text = header.rstrip("\n") + "\n" + text
    fs_atomic.atomic_write_text(path, text)


def load_json(path: "str | Path") -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json_atomic(path: "str | Path", obj: Any) -> None:
    fs_atomic.atomic_write_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def load_factory(root: "str | Path") -> Any:
    return load_yaml(factory_path(root))


def load_local(root: "str | Path") -> Any:
    return load_yaml(local_path(root))


def load_active(root: "str | Path") -> Any:
    return load_json(active_path(root))
