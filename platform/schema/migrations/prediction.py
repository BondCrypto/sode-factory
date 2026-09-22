"""Prediction-row migrator: schema_version 1 -> 2.

v1 rows recorded ``predicted`` and ``actual`` but not the derived ``ratio`` or a
``schema_version``. v2 adds both: ``ratio = actual / predicted`` (or null when
``predicted`` is zero/absent), and pins ``schema_version: 2``.
"""
from __future__ import annotations

from typing import Any


def migrate_1_to_2(row: "dict[str, Any]") -> "dict[str, Any]":
    out = dict(row)
    predicted = out.get("predicted")
    actual = out.get("actual")
    if isinstance(predicted, (int, float)) and predicted and isinstance(actual, (int, float)):
        out["ratio"] = actual / predicted
    else:
        out["ratio"] = None
    out["schema_version"] = 2
    return out
