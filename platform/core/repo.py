"""platform.core.repo — repo-layout invariants (architecture section 1.6).

Three machine checks that later become gate checks (C7 formalises them):

* :func:`check_repo_structure` — the top-level ALLOWLIST, one-package-per-component,
  the seven-department six-part contract, and a light import-lint.
* :func:`check_grep_clean` — the standalone-clone contract, section 1.4(3): the code
  and runtime planes carry no foreign path, id namespace, or credential value.
* :func:`check_import_lint` — ``platform/`` never imports ``products/``; ``products/``
  imports the factory plane only through ``platform.api``.

Each returns ``(ok: bool, findings: list[str])`` where every finding ends with a
remediation clause. The allowlist below is the single source of truth; a new
top-level directory needs an operator-approved edit here in the same commit
(section 1.6 rule 3).
"""
from __future__ import annotations

import re
from pathlib import Path

# --- The allowlist (single source of truth) -------------------------------
ALLOWED_TOP_LEVEL_DIRS = frozenset(
    {"bin", "platform", "products", "work", "metrics", "evals", "docs", "tests", "memory"}
)
ALLOWED_TOP_LEVEL_FILES = frozenset(
    {
        "factory.yaml",
        "Makefile",
        "README.md",
        "CLAUDE.md",
        "bootstrap.sh",
        "backlog.yaml",
        "requirements.txt",
        "conftest.py",
        ".gitignore",
    }
)
# Ignored everywhere: VCS, gitignored runtime, and tool caches.
_IGNORED_DIRS = frozenset(
    {".git", ".sode", "__pycache__", ".pytest_cache", ".venv", "node_modules", ".idea"}
)

# One package per component (architecture section 1.6 / hawk section 6).
PLATFORM_PACKAGES = frozenset(
    {
        "cli", "core", "schema", "config", "policy", "work", "engine", "workers",
        "guards", "brief", "record", "gate", "review", "ship", "measure",
        "observe", "departments", "metrics", "automations", "ports", "api",
    }
)

# Seven v1 departments and the six-part contract (architecture section 4A).
V1_DEPARTMENTS = frozenset(
    {"backend", "security", "frontend", "qa_quality", "devops", "architecture", "factory_ops"}
)
DEPARTMENT_CONTRACT_PARTS = ("kb", "roles", "fixtures", "tools.yaml", "review_checklist.md", "conventions.md")

# Planes scanned by the standalone grep-clean check. docs/ and memory/ (and the
# governance CLAUDE.md) legitimately document the contract and the sibling repo,
# so they are OUT of scope; the check guards the code and runtime planes plus the
# user-facing README (the first file a clone shows must be clean).
_GREP_SCAN_DIRS = ("platform", "products", "bin", "work", "metrics", "evals")
_GREP_SCAN_ROOT_FILES = ("factory.yaml", "Makefile", "README.md", "backlog.yaml", "requirements.txt", "conftest.py")

# Foreign tokens, assembled from fragments so this file never itself contains the
# literal it forbids (which would make the check flag its own source).
_SIBLING = "growth" + "-hack-" + "system"
_ID_NAMESPACES = re.compile(r"\b(" + "hyp|mech|pm" + r")_[a-z0-9]")
_CRED_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),                       # AWS access key id
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),     # PEM private key
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),                # api-key-shaped secret
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),           # slack token
)
_TEXT_SUFFIXES = frozenset(
    {".py", ".yaml", ".yml", ".json", ".md", ".txt", ".toml", ".cfg", ".ini", ".sh", ".mk", ""}
)


def _iter_files(root: Path, scan_dirs, root_files):
    for name in root_files:
        p = root / name
        if p.is_file():
            yield p
    for d in scan_dirs:
        base = root / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in _IGNORED_DIRS or part == "fixtures" for part in p.parts):
                continue
            yield p


def check_repo_structure(root: "str | Path") -> "tuple[bool, list[str]]":
    """Assert the on-disk layout matches the locked taxonomy (section 1.6)."""
    root = Path(root)
    findings: list[str] = []

    for entry in sorted(root.iterdir()):
        name = entry.name
        if entry.is_dir():
            if name in _IGNORED_DIRS or name.startswith("."):
                continue
            if name not in ALLOWED_TOP_LEVEL_DIRS:
                findings.append(
                    f"top-level directory {name!r} is not in the allowlist -- "
                    "a new top-level directory needs operator approval and an edit to "
                    "ALLOWED_TOP_LEVEL_DIRS in platform/core/repo.py in the SAME commit "
                    "(architecture section 1.6 rule 3)."
                )
        elif entry.is_file():
            if name.startswith(".") and name not in ALLOWED_TOP_LEVEL_FILES:
                continue
            if name not in ALLOWED_TOP_LEVEL_FILES:
                findings.append(
                    f"top-level file {name!r} is not in the allowlist -- add it to "
                    "ALLOWED_TOP_LEVEL_FILES in platform/core/repo.py, or move it under a plane."
                )

    platform_dir = root / "platform"
    if platform_dir.is_dir():
        for sub in sorted(platform_dir.iterdir()):
            if sub.is_dir():
                if sub.name in _IGNORED_DIRS:
                    continue
                if sub.name not in PLATFORM_PACKAGES:
                    findings.append(
                        f"platform/{sub.name}/ is not a known component package -- "
                        "one component per package (section 1.6 rule 1); add it to "
                        "PLATFORM_PACKAGES only with a spec entry."
                    )
                elif not (sub / "__init__.py").is_file():
                    findings.append(
                        f"platform/{sub.name}/ has no __init__.py -- every component package "
                        "is an importable Python package."
                    )

    depts_dir = platform_dir / "departments"
    if depts_dir.is_dir():
        present = {p.name for p in depts_dir.iterdir() if p.is_dir() and p.name not in _IGNORED_DIRS}
        for missing in sorted(V1_DEPARTMENTS - present):
            findings.append(
                f"department {missing!r} is missing under platform/departments/ -- "
                "the seven v1 departments exist from S1 (architecture section 4A)."
            )
        for extra in sorted(present - V1_DEPARTMENTS):
            findings.append(
                f"unexpected directory platform/departments/{extra}/ -- only the seven v1 "
                "departments live here (section 1.6 rule 7)."
            )
        for dept in sorted(present & V1_DEPARTMENTS):
            for part in DEPARTMENT_CONTRACT_PARTS:
                if not (depts_dir / dept / part).exists():
                    findings.append(
                        f"department {dept!r} is missing contract part {part!r} -- "
                        "each department carries the six-part contract (section 4A)."
                    )

    ok_imports, import_findings = check_import_lint(root)
    findings.extend(import_findings)
    return (len(findings) == 0, findings)


def check_import_lint(root: "str | Path") -> "tuple[bool, list[str]]":
    """platform/ must not import products/; products/ imports only platform.api."""
    root = Path(root)
    findings: list[str] = []
    plat = root / "platform"
    if plat.is_dir():
        bad = re.compile(r"^\s*(?:from|import)\s+products(?:\.|\s|$)")
        for p in plat.rglob("*.py"):
            if any(part in _IGNORED_DIRS or part == "fixtures" for part in p.parts):
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if bad.match(line):
                    findings.append(
                        f"{p.relative_to(root)}:{i} imports products/ -- the factory plane "
                        "never imports the product plane (section 1.6 rule 2)."
                    )
    prod = root / "products"
    if prod.is_dir():
        bad = re.compile(r"^\s*(?:from|import)\s+platform\.(?!api)")
        for p in prod.rglob("*.py"):
            if any(part in _IGNORED_DIRS for part in p.parts):
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if bad.match(line):
                    findings.append(
                        f"{p.relative_to(root)}:{i} imports platform internals -- products/ "
                        "imports the factory plane only through platform.api (section 1.6 rule 2)."
                    )
    return (len(findings) == 0, findings)


def scan_forbidden(text: str) -> "list[str]":
    """Return the forbidden tokens present in ``text`` (used by check + tests)."""
    hits: list[str] = []
    if _SIBLING in text:
        hits.append(f"sibling-repo reference {_SIBLING!r}")
    m = _ID_NAMESPACES.search(text)
    if m:
        hits.append(f"foreign id namespace {m.group(0)!r}")
    for pat in _CRED_PATTERNS:
        m = pat.search(text)
        if m:
            hits.append("credential-shaped value")
            break
    return hits


def check_grep_clean(root: "str | Path") -> "tuple[bool, list[str]]":
    """The standalone-clone contract (section 1.4(3)) over the code/runtime planes."""
    root = Path(root)
    findings: list[str] = []
    for p in _iter_files(root, _GREP_SCAN_DIRS, _GREP_SCAN_ROOT_FILES):
        if p.suffix not in _TEXT_SUFFIXES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for hit in scan_forbidden(text):
            findings.append(
                f"{p.relative_to(root)}: {hit} -- the tree must clone clean of any other "
                "repo's paths, id namespaces, client names or credentials "
                "(architecture section 1.4(3)); port by name with a platform/ports/ manifest."
            )
    return (len(findings) == 0, findings)
