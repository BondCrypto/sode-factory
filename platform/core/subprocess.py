"""platform.core.subprocess — a thin, explicit subprocess wrapper.

One narrow entry point so every child process the factory spawns is launched the
same way: an argv list (never a shell string), captured text output, an optional
timeout, and a plain result object. The stdlib module is imported under an alias
so this module's own name never shadows it.
"""
from __future__ import annotations

import subprocess as _subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunResult:
    """The outcome of a child process."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run(
    cmd: "list[str]",
    cwd: "str | Path | None" = None,
    env: "dict[str, str] | None" = None,
    timeout: "float | None" = None,
    check: bool = False,
) -> RunResult:
    """Run ``cmd`` (an argv list) and return a :class:`RunResult`.

    ``shell=False`` always; no string commands are accepted. When ``check`` is
    true a non-zero exit raises ``subprocess.CalledProcessError``.
    """
    proc = _subprocess.run(  # noqa: S603 - argv list, shell disabled
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if check and proc.returncode != 0:
        raise _subprocess.CalledProcessError(
            proc.returncode, cmd, proc.stdout, proc.stderr
        )
    return RunResult(proc.returncode, proc.stdout or "", proc.stderr or "")
