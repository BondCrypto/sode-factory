"""tests.cli.test_init — `sode init` writes valid artifacts and is idempotent."""
from __future__ import annotations

from platform.cli.init_cmd import cmd_init
from platform.config import loader
from platform.schema import registry, validate


def _mk_repo(tmp_path):
    (tmp_path / "platform").mkdir()
    (tmp_path / "bin").mkdir()
    return tmp_path


def test_init_writes_schema_valid_artifacts(tmp_path, monkeypatch, capsys):
    _mk_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert cmd_init(["--profile", "local", "--provider", "mock"]) == 0

    factory = loader.load_factory(tmp_path)
    assert validate.validate(factory, registry.load_schema("factory")) == []
    local = loader.load_local(tmp_path)
    assert validate.validate(local, registry.load_schema("local")) == []
    active = loader.load_active(tmp_path)
    assert validate.validate(active, registry.load_schema("active")) == []


def test_init_creates_seven_departments_with_contract(tmp_path, monkeypatch):
    _mk_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    cmd_init([])
    depts = tmp_path / "platform" / "departments"
    present = {p.name for p in depts.iterdir() if p.is_dir()}
    assert len(present) == 7
    for part in ("kb", "roles", "fixtures", "tools.yaml", "review_checklist.md", "conventions.md"):
        assert (depts / "backend" / part).exists()


def test_default_profile_is_local_mock_offline(tmp_path, monkeypatch):
    _mk_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    cmd_init([])
    factory = loader.load_factory(tmp_path)
    assert factory["policy_profile"] == "local"
    assert factory["stages"]["implement"]["provider"] == "mock"
    assert factory["secrets_broker"] == "none"


def test_init_is_idempotent_no_clobber(tmp_path, monkeypatch, capsys):
    _mk_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    cmd_init([])
    capsys.readouterr()
    fpath = loader.factory_path(tmp_path)
    fpath.write_text(fpath.read_text(encoding="utf-8") + "\n# operator hand-edit\n", encoding="utf-8")

    cmd_init([])  # second run must preserve the hand-edit
    out = capsys.readouterr().out
    assert "kept existing factory.yaml" in out
    assert "# operator hand-edit" in fpath.read_text(encoding="utf-8")


def test_force_overwrites(tmp_path, monkeypatch, capsys):
    _mk_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    cmd_init([])
    fpath = loader.factory_path(tmp_path)
    fpath.write_text(fpath.read_text(encoding="utf-8") + "\n# stale edit\n", encoding="utf-8")
    capsys.readouterr()

    cmd_init(["--force"])
    out = capsys.readouterr().out
    assert "wrote factory.yaml" in out
    assert "# stale edit" not in fpath.read_text(encoding="utf-8")
