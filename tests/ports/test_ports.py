"""tests.ports.test_ports — port-manifest conformance (review E2, C0 acceptance).

A ported asset (a file carrying the port marker) FAILS the gate without a valid
manifest at platform/ports/<asset>.yaml and PASSES with one. Fixtures compose a
temporary code plane so the real tree is never scanned here.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from platform.ports.check import check_ports, find_ports

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _plant_marked_file(root: Path) -> Path:
    plat = root / "platform"
    (plat / "ports").mkdir(parents=True)
    dest = plat / "demo_port.py"
    shutil.copy(FIXTURES / "marked_port_source.txt", dest)
    return dest


def test_marker_is_discovered(tmp_path):
    _plant_marked_file(tmp_path)
    ports = find_ports(tmp_path)
    assert "demo_port" in ports
    assert any(p.name == "demo_port.py" for p in ports["demo_port"])


def test_marked_port_without_manifest_fails(tmp_path):
    _plant_marked_file(tmp_path)  # no platform/ports/demo_port.yaml
    ok, findings = check_ports(tmp_path)
    assert ok is False
    assert any("demo_port" in f and "no manifest" in f for f in findings)


def test_marked_port_with_valid_manifest_passes(tmp_path):
    _plant_marked_file(tmp_path)
    shutil.copy(FIXTURES / "manifest_GOOD.yaml", tmp_path / "platform" / "ports" / "demo_port.yaml")
    ok, findings = check_ports(tmp_path)
    assert ok is True, findings


def test_marked_port_with_invalid_manifest_fails(tmp_path):
    _plant_marked_file(tmp_path)
    shutil.copy(FIXTURES / "manifest_BAD.yaml", tmp_path / "platform" / "ports" / "demo_port.yaml")
    ok, findings = check_ports(tmp_path)
    assert ok is False
    assert any("demo_port" in f and "invalid" in f for f in findings)


def test_real_tree_has_no_unmanifested_ports():
    from platform.core import paths

    ok, findings = check_ports(paths.find_repo_root(__file__))
    assert ok, findings
