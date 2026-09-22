"""tests.schema.test_factory_schema — the factory.yaml schema (C0 acceptance).

The generated factory.yaml validates; the BAD fixture with an unknown stage key
is REFUSED; a factory missing a required top-level key is refused.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from platform.config import templates
from platform.core import paths
from platform.schema import registry, validate

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _factory_schema():
    return registry.load_schema("factory")


def test_generated_factory_is_valid():
    factory = templates.build_factory("local", "mock")
    assert validate.validate(factory, _factory_schema()) == []


def test_committed_factory_is_valid():
    root = paths.find_repo_root(__file__)
    data = yaml.safe_load((root / "factory.yaml").read_text(encoding="utf-8"))
    assert validate.validate(data, _factory_schema()) == []


def test_unknown_stage_key_is_refused():
    bad = yaml.safe_load((FIXTURES / "factory_unknown_stage_BAD.yaml").read_text(encoding="utf-8"))
    errors = validate.validate(bad, _factory_schema())
    assert errors, "an unknown stage key must fail schema validation"
    assert any("deploy" in e and "not allowed" in e for e in errors)


def test_missing_required_top_level_key_is_refused():
    factory = templates.build_factory("local", "mock")
    del factory["providers"]
    errors = validate.validate(factory, _factory_schema())
    assert any("providers" in e and "missing" in e for e in errors)


def test_bad_profile_enum_is_refused():
    factory = templates.build_factory("local", "mock")
    factory["policy_profile"] = "wide-open"
    assert validate.validate(factory, _factory_schema())
