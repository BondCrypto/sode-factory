"""sode doctor — validate the tree and the environment for the active profile.

Every artifact is checked against its schema; environment checks are PROFILE-GATED
(the broker, GitHub, and adapter checks do not apply in the offline ``local``
profile, so they are reported SKIP, not FAIL). Exit 0 iff nothing FAILs.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from ..config import loader
from ..core import paths
from ..core import subprocess as sp
from ..schema import registry, validate

_MIN_GIT = (2, 40)


@dataclass
class Check:
    name: str
    status: str  # PASS | SKIP | FAIL
    detail: str = ""
    remediation: str = ""


def _validate_artifact(kind: str, path: Path, name: str) -> Check:
    if not path.exists():
        return Check(name, "FAIL", f"{path.name} is missing", f"run `sode init` to create {path.name}")
    try:
        data = loader.load_json(path) if path.suffix == ".json" else loader.load_yaml(path)
    except Exception as exc:  # noqa: BLE001 - report any parse error as a failure
        return Check(name, "FAIL", f"{path.name} does not parse: {exc}", "fix the file syntax")
    errors = validate.validate(data, registry.load_schema(kind))
    if errors:
        return Check(name, "FAIL", f"{path.name}: {errors[0]}", f"fix {path.name} against platform/schema/{kind}.schema.json")
    return Check(name, "PASS", f"{path.name} valid")


def _check_git_version() -> Check:
    res = sp.run(["git", "--version"])
    if not res.ok:
        return Check("git", "FAIL", "git not found", "install git >= 2.40")
    m = re.search(r"(\d+)\.(\d+)", res.stdout)
    if not m:
        return Check("git", "FAIL", f"cannot parse: {res.stdout.strip()}", "install git >= 2.40")
    ver = (int(m.group(1)), int(m.group(2)))
    if ver < _MIN_GIT:
        return Check("git", "FAIL", f"git {ver[0]}.{ver[1]} < 2.40", "upgrade git to >= 2.40")
    return Check("git", "PASS", f"git {ver[0]}.{ver[1]}")


def _check_active_sha(root: Path, active: dict) -> Check:
    sha = active.get("sha", "")
    if sha in ("", "uncommitted"):
        return Check("active.sha", "SKIP", "no committed sha yet (uncommitted tree)")
    res = sp.run(["git", "-C", str(root), "cat-file", "-e", sha + "^{commit}"])
    if res.ok:
        return Check("active.sha", "PASS", f"active sha {sha[:12]} exists")
    return Check("active.sha", "FAIL", f"active sha {sha[:12]} not in git", "re-run `sode init`")


def _check_binaries(root: Path) -> Check:
    import os

    missing = []
    for b in ("sode", "sode-sh", "sode-run"):
        p = root / "bin" / b
        if not p.exists():
            missing.append(f"{b} (missing)")
        elif not os.access(p, os.X_OK):
            missing.append(f"{b} (not executable)")
    if missing:
        return Check("binaries", "FAIL", ", ".join(missing), "chmod +x bin/sode bin/sode-sh bin/sode-run")
    return Check("binaries", "PASS", "sode, sode-sh, sode-run present + executable")


def _check_schemas() -> Check:
    for kind in registry.SCHEMA_FILES:
        p = registry.schema_path(kind)
        if not p.exists():
            return Check("schemas", "FAIL", f"{p.name} missing", "restore platform/schema/")
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            return Check("schemas", "FAIL", f"{p.name} invalid JSON: {exc}", "fix the schema file")
    return Check("schemas", "PASS", f"{len(registry.SCHEMA_FILES)} schemas present")


def _env_checks(root: Path, factory: dict) -> "list[Check]":
    profile = factory.get("policy_profile", "local")
    broker = factory.get("secrets_broker", "none")
    checks: list[Check] = []

    # Secrets broker (only when one is configured).
    if broker == "1password":
        if shutil.which("op"):
            checks.append(Check("broker", "PASS", "1password `op` on PATH"))
        else:
            checks.append(Check("broker", "FAIL", "`op` not found", "install the 1Password CLI or set secrets_broker: none"))
    else:
        checks.append(Check("broker", "SKIP", f"no broker in {profile} profile"))

    # Secrets registry file (only relevant with a broker).
    if broker != "none":
        reg = root / factory.get("secrets_registry", "")
        if reg.exists():
            checks.append(Check("secrets_registry", "PASS", str(reg.name)))
        else:
            checks.append(Check("secrets_registry", "FAIL", f"{factory.get('secrets_registry')} missing", "create the secrets registry"))
    else:
        checks.append(Check("secrets_registry", "SKIP", "no secrets in this profile"))

    # GitHub reachability + branch protection (standard only; lands with C10).
    if profile == "standard":
        checks.append(Check("github", "SKIP", "GitHub checks land with C10 (S13)"))
    else:
        checks.append(Check("github", "SKIP", f"not applicable in {profile} profile"))

    # Adapter cli_version pinned + installed / model ids (non-mock stages only).
    stage_providers = {
        s.get("provider") for s in factory.get("stages", {}).values()
        if s.get("provider") not in (None, "none", "mock")
    }
    if stage_providers:
        try:
            local = loader.load_local(root)
        except Exception:  # noqa: BLE001
            local = {"providers": {}}
        for name in sorted(stage_providers):
            pinned = (local.get("providers", {}).get(name, {}) or {}).get("cli_version")
            if pinned:
                checks.append(Check(f"adapter.{name}", "PASS", f"cli_version {pinned}"))
            else:
                checks.append(Check(f"adapter.{name}", "FAIL", "cli_version not pinned", f"pin providers.{name}.cli_version in .sode/local.yaml"))
    else:
        checks.append(Check("adapters", "SKIP", "mock provider — no adapters to check"))

    return checks


def run_checks(root: Path) -> "list[Check]":
    checks: list[Check] = []
    fpath = loader.factory_path(root)
    checks.append(_validate_artifact("factory", fpath, "factory.yaml"))
    checks.append(_validate_artifact("local", loader.local_path(root), "local.yaml"))
    active_check = _validate_artifact("active", loader.active_path(root), "active.json")
    checks.append(active_check)
    checks.append(_check_git_version())
    checks.append(_check_binaries(root))
    checks.append(_check_schemas())
    if active_check.status == "PASS":
        checks.append(_check_active_sha(root, loader.load_active(root)))
    if fpath.exists():
        try:
            checks.extend(_env_checks(root, loader.load_factory(root)))
        except Exception as exc:  # noqa: BLE001
            checks.append(Check("env", "FAIL", f"could not run env checks: {exc}", "fix factory.yaml"))
    return checks


def cmd_doctor(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(prog="sode doctor", add_help=True)
    parser.add_argument("--target", default="self")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = paths.find_repo_root()
    checks = run_checks(root)
    failed = [c for c in checks if c.status == "FAIL"]

    if args.json:
        print(json.dumps([c.__dict__ for c in checks], indent=2))
    else:
        print(f"sode doctor (target={args.target}):")
        for c in checks:
            line = f"  [{c.status:4}] {c.name}: {c.detail}"
            if c.status == "FAIL" and c.remediation:
                line += f"\n         -> {c.remediation}"
            print(line)
        summary = f"{sum(c.status=='PASS' for c in checks)} pass, " \
                  f"{sum(c.status=='SKIP' for c in checks)} skip, {len(failed)} fail"
        print(f"  {summary}")
    return 1 if failed else 0
