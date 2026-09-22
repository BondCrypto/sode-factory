"""platform.cli.gate_bootstrap — the S1 one-command gate's non-pytest checks.

`make test` runs pytest, then this module. It runs C0's four structural checks
against the REAL tree and exits non-zero on any finding. This is the BOOTSTRAP
gate; C6/C7 (S6/S10) replace it with the real gate registry under platform/gate/.
Each check ships a remediation string and a known-bad fixture (see tests/).
"""
from __future__ import annotations

import sys

from ..core import paths
from ..core.repo import check_grep_clean, check_repo_structure
from ..ports.check import check_ports
from ..schema.checks import check_factory_schema_doc_sync

_CHECKS = (
    ("check_repo_structure", check_repo_structure),
    ("check_factory_schema_doc_sync", check_factory_schema_doc_sync),
    ("check_ports", check_ports),
    ("check_grep_clean", check_grep_clean),
)


def main(argv: "list[str] | None" = None) -> int:
    root = paths.find_repo_root()
    failed = 0
    print(f"sode gate (S1 bootstrap) at {root}:")
    for name, fn in _CHECKS:
        ok, findings = fn(root)
        if ok:
            print(f"  [PASS] {name}")
        else:
            failed += 1
            print(f"  [FAIL] {name}")
            for f in findings:
                print(f"         - {f}")
    if failed:
        print(f"gate: {failed} check(s) FAILED")
        return 1
    print("gate: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
