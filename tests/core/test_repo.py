"""tests.core.test_repo — repo-layout + standalone-clone invariants.

Covers the placement-rule allowlist (section 1.6), the import-lint, and the
section 1.4(3) grep-clean scanner. Foreign tokens are assembled at run time so
this test file never itself contains the literal the scanner forbids.
"""
from __future__ import annotations

from platform.core import paths, repo


def test_flags_unlisted_top_level_dir(tmp_path):
    (tmp_path / "platform").mkdir()
    (tmp_path / "bin").mkdir()
    (tmp_path / "frobnicate").mkdir()  # not in the allowlist
    ok, findings = repo.check_repo_structure(tmp_path)
    assert ok is False
    assert any("frobnicate" in f and "allowlist" in f for f in findings)


def test_dotdirs_and_allowed_dirs_do_not_flag(tmp_path):
    (tmp_path / "platform").mkdir()
    (tmp_path / "bin").mkdir()
    (tmp_path / ".sode").mkdir()  # gitignored runtime, ignored by the check
    (tmp_path / "docs").mkdir()  # allowlisted
    ok, findings = repo.check_repo_structure(tmp_path)
    # No finding should mention .sode or docs as an unlisted directory.
    assert not any(".sode" in f or "'docs'" in f for f in findings)


def test_real_tree_passes_structure_and_grep():
    root = paths.find_repo_root(__file__)
    ok_struct, struct = repo.check_repo_structure(root)
    assert ok_struct, struct
    ok_grep, grep = repo.check_grep_clean(root)
    assert ok_grep, grep


def test_import_lint_flags_platform_importing_products(tmp_path):
    pkg = tmp_path / "platform" / "engine"
    pkg.mkdir(parents=True)
    (pkg / "m.py").write_text("import products.line\n", encoding="utf-8")
    ok, findings = repo.check_import_lint(tmp_path)
    assert ok is False
    assert any("imports products" in f for f in findings)


def test_import_lint_allows_products_via_api_only(tmp_path):
    prod = tmp_path / "products" / "line"
    prod.mkdir(parents=True)
    (prod / "good.py").write_text("from platform.api import client\n", encoding="utf-8")
    ok, _ = repo.check_import_lint(tmp_path)
    assert ok is True
    (prod / "bad.py").write_text("from platform.core import ids\n", encoding="utf-8")
    ok2, findings = repo.check_import_lint(tmp_path)
    assert ok2 is False
    assert any("platform internals" in f for f in findings)


def test_scan_forbidden_detects_each_class():
    sibling = "growth" + "-hack-" + "system"
    idns = "hyp" + "_" + "abc"
    cred = "AKIA" + "ABCDEFGHIJKLMNOP"
    assert repo.scan_forbidden(f"/Users/x/{sibling}/repo")
    assert repo.scan_forbidden(f"see {idns} here")
    assert repo.scan_forbidden(f"key={cred}")
    assert repo.scan_forbidden("a perfectly clean line of text") == []
