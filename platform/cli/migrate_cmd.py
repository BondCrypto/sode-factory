"""sode migrate --check|--apply (review B8).

Every artifact that carries ``schema_version`` can be walked: ``--check`` reports
the pending migrations, ``--apply`` runs them atomically and round-trips (a
re-check then reports none pending). With ``--path`` it operates on one file
(``--kind`` names its kind, else it is inferred); without ``--path`` it scans the
well-known artifacts under the repo root.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..config import loader
from ..core import fs_atomic, paths
from ..schema import migrations, registry


def _load_rows(path: Path) -> "tuple[list[dict], str]":
    """Return (rows, fmt) where fmt is one of jsonl|yaml|json."""
    if path.suffix == ".jsonl":
        rows = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        return rows, "jsonl"
    if path.suffix == ".json":
        return [loader.load_json(path)], "json"
    return [loader.load_yaml(path)], "yaml"


def _write_rows(path: Path, rows: "list[dict]", fmt: str) -> None:
    if fmt == "jsonl":
        text = "".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in rows)
        fs_atomic.atomic_write_text(path, text)
    elif fmt == "json":
        loader.write_json_atomic(path, rows[0])
    else:
        loader.write_yaml_atomic(path, rows[0])


def _resolve_kind(path: Path, rows: "list[dict]", explicit: "str | None") -> str:
    if explicit:
        return explicit
    if rows and isinstance(rows[0], dict) and "kind" in rows[0]:
        return rows[0]["kind"]
    inferred = registry.kind_for_filename(path.name)
    if inferred:
        return inferred
    raise SystemExit(f"sode migrate: cannot determine kind of {path}; pass --kind")


def _process_file(path: Path, kind: str, apply: bool) -> "tuple[int, list[str]]":
    """Return (pending_count, report_lines) for one artifact file."""
    rows, fmt = _load_rows(path)
    lines: list[str] = []
    pending = 0
    new_rows: list[dict] = []
    for i, row in enumerate(rows):
        steps = migrations.plan(kind, migrations.artifact_version(row))
        if steps:
            pending += 1
            chain = " -> ".join(str(s[0]) for s in steps) + f" -> {steps[-1][1]}"
            where = f"{path.name}[{i}]" if fmt == "jsonl" else path.name
            lines.append(f"  pending: {where} ({kind}) {chain}")
        if apply and steps:
            migrated, _ = migrations.apply(kind, row)
            new_rows.append(migrated)
        else:
            new_rows.append(row)
    if apply and pending:
        _write_rows(path, new_rows, fmt)
        lines.append(f"  applied: {path.name} ({pending} row(s) upgraded to current)")
    return pending, lines


def cmd_migrate(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(prog="sode migrate", add_help=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report pending migrations (default)")
    mode.add_argument("--apply", action="store_true", help="run pending migrations atomically")
    parser.add_argument("--path", help="operate on one artifact file")
    parser.add_argument("--kind", help="artifact kind for --path (else inferred)")
    args = parser.parse_args(argv)
    apply = args.apply  # default (neither flag) == check

    root = paths.find_repo_root()
    total_pending = 0
    report: list[str] = []

    if args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"sode migrate: no such file: {path}")
            return 1
        rows, _ = _load_rows(path)
        kind = _resolve_kind(path, rows, args.kind)
        pending, lines = _process_file(path, kind, apply)
        total_pending += pending
        report.extend(lines)
    else:
        for rel, kind in registry.WELL_KNOWN_PATHS.items():
            path = root / rel
            if not path.exists():
                continue
            pending, lines = _process_file(path, kind, apply)
            total_pending += pending
            report.extend(lines)

    print("sode migrate --" + ("apply" if apply else "check") + ":")
    if report:
        for ln in report:
            print(ln)
    if total_pending == 0:
        print("  none pending")
    return 0
