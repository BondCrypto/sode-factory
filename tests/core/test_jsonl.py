"""tests.core.test_jsonl — append-only ledgers (platform.core.jsonl)."""
from __future__ import annotations

from platform.core import jsonl


def test_append_then_read_round_trip(tmp_path):
    ledger = tmp_path / "d" / "events.jsonl"
    jsonl.append(ledger, {"n": 1})
    jsonl.append(ledger, {"n": 2, "s": "x"})
    rows = jsonl.read(ledger)
    assert rows == [{"n": 1}, {"n": 2, "s": "x"}]


def test_iter_rows_skips_blank_lines(tmp_path):
    ledger = tmp_path / "e.jsonl"
    jsonl.append(ledger, {"a": 1})
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write("\n   \n")
    jsonl.append(ledger, {"a": 2})
    assert list(jsonl.iter_rows(ledger)) == [{"a": 1}, {"a": 2}]


def test_read_missing_ledger_is_empty(tmp_path):
    assert jsonl.read(tmp_path / "nope.jsonl") == []
