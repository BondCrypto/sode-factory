"""tests.test_standalone — the standalone-clone contract (architecture section 1.4).

SKELETON form for C0 (session S1). In a temp HOME, with no network, a fresh copy
of the tree must:

  1. `make test` GREEN,
  2. `sode init --profile local --provider mock` exit 0 (offline default),
  3. `sode doctor` exit 0 in the local profile,
  4. grep clean per section 1.4(3) — no sibling path, foreign id namespace, or
     credential value in the code/runtime planes.

Section 1.4(2) (run ONE work item end to end on the mock provider) and the full
grep/record assertions arrive with the components that add `sode new/tick/record/
measure` (S2, S7, S8, S17); this file is the seam those sessions extend. There
are deliberately no skip markers: every assertion below is in C0's scope.

`make test` inside the copy is the fast target (it excludes THIS file), so the
copied gate never recurses into another standalone run.
"""
from __future__ import annotations

import os
import shutil
import site
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest

from platform.core import paths, repo

_COPY_IGNORE = shutil.ignore_patterns(
    ".git", ".sode", "__pycache__", "*.pyc", ".pytest_cache", ".venv",
    "node_modules", ".DS_Store",
)


def _toolchain_sitedirs() -> "list[str]":
    """The interpreter's site-packages (pytest + PyYAML live here).

    Captured from the CURRENT process (real HOME) so they stay importable after
    HOME is repointed at a throwaway dir: the temp HOME still catches any repo
    code that reads a machine-local path, but the Python toolchain is not a repo
    concern and must remain available (a real fresh clone runs `pip install -r
    requirements.txt` first).
    """
    dirs = [sysconfig.get_paths()["purelib"]]
    try:
        dirs.append(site.getusersitepackages())
    except Exception:  # noqa: BLE001 - user site is best-effort
        pass
    try:
        dirs.extend(site.getsitepackages())
    except Exception:  # noqa: BLE001 - not present in every layout
        pass
    return list(dict.fromkeys(d for d in dirs if d))


def _offline_env(home: Path) -> "dict[str, str]":
    """A throwaway-HOME environment that still reaches the Python toolchain."""
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["PYTHONPATH"] = os.pathsep.join(_toolchain_sitedirs())
    return env


def _run(cmd: "list[str]", cwd: Path, env: "dict[str, str]") -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True)


@pytest.fixture(scope="module")
def fresh_clone(tmp_path_factory) -> "tuple[Path, Path]":
    """Copy the working tree into a throwaway HOME (a stand-in for `git clone`)."""
    src = paths.find_repo_root(__file__)
    home = tmp_path_factory.mktemp("home")
    dst = home / "sode-factory"
    shutil.copytree(src, dst, ignore=_COPY_IGNORE)
    return home, dst


def test_standalone_skeleton(fresh_clone):
    home, clone = fresh_clone
    env = _offline_env(home)
    sode = [str(clone / "bin" / "sode")]

    # 1.4(1) — the one-command gate is GREEN in the fresh copy. PY pins the same
    # interpreter that ran this suite (the one with the deps installed).
    gate = _run(["make", "test", f"PY={sys.executable}"], clone, env)
    assert gate.returncode == 0, f"`make test` failed in the clone:\n{gate.stdout}\n{gate.stderr}"

    # C0 default — init is offline (local + mock) and succeeds.
    init = _run(sode + ["init", "--profile", "local", "--provider", "mock"], clone, env)
    assert init.returncode == 0, f"`sode init` failed:\n{init.stdout}\n{init.stderr}"

    # doctor is green in the local profile (broker/github/adapters skipped).
    doctor = _run(sode + ["doctor"], clone, env)
    assert doctor.returncode == 0, f"`sode doctor` failed:\n{doctor.stdout}\n{doctor.stderr}"

    # 1.4(3) — the code + runtime planes clone clean of foreign paths/ids/creds.
    ok, findings = repo.check_grep_clean(clone)
    assert ok, "grep-clean violations in the fresh clone:\n" + "\n".join(findings)
