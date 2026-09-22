"""tests.cli.test_doctor — `sode doctor` in the offline local profile."""
from __future__ import annotations

import os

from platform.cli.doctor_cmd import cmd_doctor, run_checks
from platform.cli.init_cmd import cmd_init
from platform.core import paths


def _mk_repo_with_binaries(tmp_path):
    (tmp_path / "platform").mkdir()
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for b in ("sode", "sode-sh", "sode-run"):
        p = bindir / b
        p.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        os.chmod(p, 0o755)
    return tmp_path


def test_doctor_exits_zero_after_init_in_local(tmp_path, monkeypatch):
    _mk_repo_with_binaries(tmp_path)
    monkeypatch.chdir(tmp_path)
    cmd_init([])
    assert cmd_doctor([]) == 0


def test_doctor_reports_only_skips_and_passes_in_local(tmp_path, monkeypatch):
    _mk_repo_with_binaries(tmp_path)
    monkeypatch.chdir(tmp_path)
    cmd_init([])
    checks = run_checks(paths.find_repo_root(tmp_path))
    statuses = {c.status for c in checks}
    assert "FAIL" not in statuses
    # The four profile-gated checks are skipped offline.
    skips = {c.name for c in checks if c.status == "SKIP"}
    assert {"broker", "secrets_registry", "github"} <= skips


def test_doctor_fails_when_factory_missing(tmp_path, monkeypatch):
    _mk_repo_with_binaries(tmp_path)  # no `sode init`, so factory.yaml is absent
    monkeypatch.chdir(tmp_path)
    assert cmd_doctor([]) == 1
    checks = run_checks(paths.find_repo_root(tmp_path))
    fails = {c.name for c in checks if c.status == "FAIL"}
    assert "factory.yaml" in fails


def test_doctor_json_mode(tmp_path, monkeypatch, capsys):
    _mk_repo_with_binaries(tmp_path)
    monkeypatch.chdir(tmp_path)
    cmd_init([])
    capsys.readouterr()  # discard init's output
    assert cmd_doctor(["--json"]) == 0
    import json

    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list) and any(c["name"] == "git" for c in data)
