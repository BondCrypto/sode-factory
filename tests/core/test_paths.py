"""tests.core.test_paths — repo-root resolution (platform.core.paths)."""
from __future__ import annotations

import pytest

from platform.core import paths


def test_finds_root_from_a_nested_dir(tmp_path):
    (tmp_path / "platform").mkdir()
    (tmp_path / "bin").mkdir()
    nested = tmp_path / "platform" / "cli"
    nested.mkdir()
    assert paths.find_repo_root(nested) == tmp_path.resolve()


def test_raises_outside_a_repo(tmp_path):
    with pytest.raises(FileNotFoundError):
        paths.find_repo_root(tmp_path)


def test_finds_this_repo_root():
    root = paths.find_repo_root(__file__)
    assert (root / "platform").is_dir()
    assert (root / "bin" / "sode").exists()
