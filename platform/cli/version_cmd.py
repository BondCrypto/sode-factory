"""sode version — print the sode version and the artifact schema versions."""
from __future__ import annotations

from .. import __version__
from ..schema import registry


def cmd_version(argv: "list[str]") -> int:
    print(f"sode {__version__}")
    versions = registry.current_versions()
    rendered = " ".join(f"{k}={v}" for k, v in sorted(versions.items()))
    print(f"schema_versions: {rendered}")
    return 0
