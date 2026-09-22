"""tests.schema.test_registry — the artifact-schema registry."""
from __future__ import annotations

import pytest

from platform.schema import registry


def test_every_kind_loads_and_pins_a_version():
    versions = registry.current_versions()
    assert set(versions) == set(registry.SCHEMA_FILES)
    for kind, v in versions.items():
        assert isinstance(v, int) and v >= 1


def test_ten_schemas_present():
    assert len(registry.SCHEMA_FILES) == 10


def test_prediction_current_is_two():
    assert registry.current_version("prediction") == 2


def test_well_known_paths_map_to_known_kinds():
    for _rel, kind in registry.WELL_KNOWN_PATHS.items():
        assert kind in registry.SCHEMA_FILES


def test_unknown_kind_raises():
    with pytest.raises(KeyError):
        registry.load_schema("nope")
