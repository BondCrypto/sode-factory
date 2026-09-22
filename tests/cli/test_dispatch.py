"""tests.cli.test_dispatch — the `sode` entry-point routing."""
from __future__ import annotations

from platform.cli import dispatch


def test_unknown_verb_is_an_error(capsys):
    rc = dispatch.main(["frobnicate"])
    assert rc == 2
    assert "unknown verb" in capsys.readouterr().out


def test_help_lists_implemented_and_planned(capsys):
    assert dispatch.main([]) == 0
    out = capsys.readouterr().out
    assert "implemented (S1):" in out and "planned:" in out


def test_version_flag_routes_to_version(capsys):
    assert dispatch.main(["--version"]) == 0
    assert "sode" in capsys.readouterr().out


def test_planned_verb_reports_and_exits_nonzero(capsys):
    rc = dispatch.main(["ship"])
    assert rc == 2
    out = capsys.readouterr().out
    assert "not yet implemented" in out and "S13" in out
