"""tests.schema.test_migrate — schema migrations (C0 acceptance, review B8).

`migrate --check` reports the pending migration on a one-version-behind
prediction row; `--apply` round-trips (a re-check then reports none pending) and
the upgraded row validates against the current schema.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from platform.cli.migrate_cmd import cmd_migrate
from platform.schema import migrations, registry, validate

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "prediction_v1.jsonl"


def test_prediction_is_at_v2():
    assert registry.current_version("prediction") == 2


def test_plan_reports_the_pending_step():
    steps = migrations.plan("prediction", 1)
    assert steps == [(1, 2)]
    assert migrations.plan("prediction", 2) == []


def test_apply_computes_ratio_and_pins_version():
    row = json.loads(FIXTURE.read_text(encoding="utf-8").splitlines()[0])
    upgraded, steps = migrations.apply("prediction", row)
    assert steps == [(1, 2)]
    assert upgraded["schema_version"] == 2
    assert upgraded["ratio"] == row["actual"] / row["predicted"]
    assert validate.validate(upgraded, registry.load_schema("prediction")) == []


def test_ratio_is_null_when_predicted_is_zero():
    upgraded = migrations.MIGRATORS[("prediction", 1)]({"predicted": 0, "actual": 5})
    assert upgraded["ratio"] is None


def test_cli_check_then_apply_round_trips(tmp_path, capsys):
    work = tmp_path / "prediction_v1.jsonl"
    shutil.copy(FIXTURE, work)

    assert cmd_migrate(["--check", "--path", str(work)]) == 0
    out = capsys.readouterr().out
    assert "pending" in out and "1 -> 2" in out

    assert cmd_migrate(["--apply", "--path", str(work)]) == 0
    assert "applied" in capsys.readouterr().out

    assert cmd_migrate(["--check", "--path", str(work)]) == 0
    assert "none pending" in capsys.readouterr().out

    row = json.loads(work.read_text(encoding="utf-8").splitlines()[0])
    assert row["schema_version"] == 2 and row["ratio"] == 0.5


def test_kind_inference_handles_versioned_fixture_name():
    # The spec names the fixture `prediction_v1`; kind must resolve without --kind.
    assert registry.kind_for_filename("prediction_v1.jsonl") == "prediction"
    assert registry.kind_for_filename("predictions.jsonl") == "prediction"
    assert registry.kind_for_filename("factory.yaml") == "factory"
    assert registry.kind_for_filename("mystery.txt") is None
