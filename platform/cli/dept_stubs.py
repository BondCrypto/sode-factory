"""Create the seven department contract stubs (C0's init helper).

The department PLANE (``platform/departments/``) is owned by C9 (S9); C0 only
guarantees the seven directories exist with the six-part contract (architecture
section 4A) so the layout is valid from S1. Real KB/roles/checklists land in each
department's seeding session. This helper is idempotent: it fills only what is
missing and never overwrites existing content.
"""
from __future__ import annotations

from pathlib import Path

from ..core.repo import DEPARTMENT_CONTRACT_PARTS, V1_DEPARTMENTS

_DIR_PARTS = ("kb", "roles", "fixtures")

_TOOLS_YAML = (
    "# GENERATED-STUB: platform/departments/{d}/tools.yaml\n"
    "# Department tooling registry (architecture section 4A). Stub at S1; owned by C9 (S9).\n"
    "schema_version: 1\n"
    "department: {d}\n"
    "tools: []\n"
)
_REVIEW_MD = (
    "# {d} — review checklist (STUB)\n\n"
    "Stub at S1. The real checklist and its angle tags land in the {d} seeding "
    "session (C9 / S9).\n"
)
_CONVENTIONS_MD = (
    "# {d} — conventions (STUB)\n\n"
    "Stub at S1 (six-part department contract, architecture section 4A). Real "
    "conventions land in the {d} seeding session (C9 / S9).\n"
)


def ensure_departments(root: "str | Path") -> "list[str]":
    """Ensure every v1 department carries the six-part contract. Return dept names created/repaired."""
    base = Path(root) / "platform" / "departments"
    touched: list[str] = []
    for dept in sorted(V1_DEPARTMENTS):
        ddir = base / dept
        created = not ddir.exists()
        for part in _DIR_PARTS:
            d = ddir / part
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
                (d / ".gitkeep").write_text(f"# {dept} {part} — populated at S9.\n", encoding="utf-8")
                created = True
        for fname, tmpl in (
            ("tools.yaml", _TOOLS_YAML),
            ("review_checklist.md", _REVIEW_MD),
            ("conventions.md", _CONVENTIONS_MD),
        ):
            f = ddir / fname
            if not f.exists():
                f.write_text(tmpl.format(d=dept), encoding="utf-8")
                created = True
        # Sanity: the contract is complete.
        assert all((ddir / part).exists() for part in DEPARTMENT_CONTRACT_PARTS)
        if created:
            touched.append(dept)
    return touched
