"""platform.ports.check — port-manifest conformance (review E2).

A ported asset is copied + adapted + tested, never imported. A ported file
declares itself with a marker comment ``# <PORT>: <asset>`` (the token is
assembled below), and must have a matching manifest at
``platform/ports/<asset>.yaml`` that validates against the port_manifest schema.
A marked file with no valid manifest fails the gate.

The scan covers the code planes (``platform/``, ``products/``, ``bin/``) only;
``platform/ports/`` itself and test ``fixtures/`` trees are excluded.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..schema import registry, validate

# Assembled from fragments so this checker's own source is never mistaken for a
# ported file when the code planes are scanned.
MARKER = "SODE" + "-PORT"
_MARKER_RE = re.compile(re.escape(MARKER) + r":\s*([A-Za-z0-9_.-]+)")

_SCAN_DIRS = ("platform", "products", "bin")
_IGNORE_PARTS = frozenset({"__pycache__", ".git", ".sode", "fixtures"})
_TEXT_SUFFIXES = frozenset({".py", ".sh", ".yaml", ".yml", ".md", ".txt", ""})


def _load_yaml(path: Path):
    import yaml  # PyYAML: the one config dependency (see requirements.txt).

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def find_ports(root: "str | Path") -> "dict[str, list[Path]]":
    """Map declared asset name -> the files that declare it, across the code planes."""
    root = Path(root)
    ports: dict[str, list[Path]] = {}
    for d in _SCAN_DIRS:
        base = root / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix not in _TEXT_SUFFIXES:
                continue
            if any(part in _IGNORE_PARTS for part in p.parts):
                continue
            # Do not treat the manifests themselves as ported files.
            if p.parent == (root / "platform" / "ports"):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in _MARKER_RE.finditer(text):
                ports.setdefault(m.group(1), []).append(p)
    return ports


def check_ports(root: "str | Path") -> "tuple[bool, list[str]]":
    """Every marked port has a valid manifest at platform/ports/<asset>.yaml."""
    root = Path(root)
    findings: list[str] = []
    manifest_schema = registry.load_schema("port_manifest")
    for asset, files in sorted(find_ports(root).items()):
        manifest = root / "platform" / "ports" / f"{asset}.yaml"
        where = ", ".join(str(f.relative_to(root)) for f in files)
        if not manifest.is_file():
            findings.append(
                f"ported asset {asset!r} (declared in {where}) has no manifest at "
                f"platform/ports/{asset}.yaml -- a port without its manifest fails the gate "
                "(review E2); write the manifest (source, source_commit, adapted/dropped "
                "invariants, pinning tests)."
            )
            continue
        data = _load_yaml(manifest)
        errors = validate.validate(data, manifest_schema)
        if errors:
            findings.append(
                f"port manifest platform/ports/{asset}.yaml is invalid: {errors} -- "
                "fix it against platform/schema/port_manifest.schema.json."
            )
    return (len(findings) == 0, findings)
