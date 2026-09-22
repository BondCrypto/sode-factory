"""platform.schema.checks — schema/doc anti-drift (gate: check_factory_schema_doc_sync).

The factory.yaml schema and the section 3.3 shape documented in the architecture
spec must not drift apart. This check parses the section 3.3 fenced block, then
asserts the factory schema declares exactly the same top-level keys and the same
stage names. A drift on either side fails with a remediation string.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import registry

_DOC_REL = "docs/design/sode_factory_architecture.md"
_SECTION = "### 3.3"


def _extract_section_block(doc_text: str) -> str:
    idx = doc_text.find(_SECTION)
    if idx < 0:
        raise ValueError(f"{_SECTION} not found in {_DOC_REL}")
    fence_open = doc_text.find("```", idx)
    body_start = doc_text.find("\n", fence_open) + 1
    fence_close = doc_text.find("```", body_start)
    return doc_text[body_start:fence_close]


def _doc_top_level_keys(block: str) -> "set[str]":
    return {m.group(1) for m in re.finditer(r"^([a-z_]+):", block, re.MULTILINE)}


def _doc_stage_names(block: str) -> "set[str]":
    lines = block.splitlines()
    names: set[str] = set()
    in_stages = False
    for line in lines:
        if re.match(r"^stages:", line):
            in_stages = True
            continue
        if in_stages:
            if re.match(r"^[a-z_]+:", line):  # next top-level key ends the stages block
                break
            m = re.match(r"^  ([a-z_]+):", line)
            if m:
                names.add(m.group(1))
    return names


def check_factory_schema_doc_sync(root: "str | Path") -> "tuple[bool, list[str]]":
    root = Path(root)
    findings: list[str] = []
    doc = (root / _DOC_REL).read_text(encoding="utf-8")
    block = _extract_section_block(doc)

    doc_keys = _doc_top_level_keys(block)
    doc_stages = _doc_stage_names(block)

    schema = registry.load_schema("factory")
    schema_keys = set(schema.get("properties", {}))
    schema_stages = set(schema["properties"]["stages"].get("properties", {}))

    missing = doc_keys - schema_keys
    extra = schema_keys - doc_keys
    if missing:
        findings.append(
            f"factory schema is MISSING top-level keys documented in section 3.3: {sorted(missing)} -- "
            "add them to platform/schema/factory.schema.json (properties + required)."
        )
    if extra:
        findings.append(
            f"factory schema has top-level keys NOT in section 3.3: {sorted(extra)} -- "
            "either document them in the spec (architecture-class change) or remove them."
        )

    if doc_stages != schema_stages:
        findings.append(
            f"stage names drift: spec section 3.3 = {sorted(doc_stages)}, schema = {sorted(schema_stages)} -- "
            "keep stages.properties in factory.schema.json equal to the documented stage set."
        )
    return (len(findings) == 0, findings)
