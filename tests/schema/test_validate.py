"""tests.schema.test_validate — the dependency-free JSON Schema subset validator."""
from __future__ import annotations

import pytest

from platform.schema import validate


def test_type_and_required():
    schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}}}
    assert validate.validate({"a": 1}, schema) == []
    assert validate.validate({}, schema)  # missing required
    assert validate.validate({"a": "x"}, schema)  # wrong type


def test_additional_properties_false():
    schema = {"type": "object", "additionalProperties": False, "properties": {"a": {}}}
    assert validate.validate({"a": 1}, schema) == []
    errs = validate.validate({"a": 1, "b": 2}, schema)
    assert any("additional property" in e for e in errs)


def test_enum_and_const():
    assert validate.validate("x", {"enum": ["x", "y"]}) == []
    assert validate.validate("z", {"enum": ["x", "y"]})
    assert validate.validate(1, {"const": 1}) == []
    assert validate.validate(2, {"const": 1})


def test_bool_is_not_integer():
    # A JSON boolean must not satisfy integer/number (a common validator bug).
    assert validate.validate(True, {"type": "integer"})
    assert validate.validate(True, {"type": "number"})
    assert validate.validate(True, {"type": "boolean"}) == []


def test_minimum_maximum_and_items():
    schema = {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 10}}
    assert validate.validate([0, 5, 10], schema) == []
    assert validate.validate([0, 11], schema)
    assert validate.validate([-1], schema)


def test_ref_resolution():
    schema = {
        "type": "object",
        "properties": {"s": {"$ref": "#/definitions/stage"}},
        "definitions": {"stage": {"type": "object", "required": ["provider"]}},
    }
    assert validate.validate({"s": {"provider": "mock"}}, schema) == []
    assert validate.validate({"s": {}}, schema)


def test_pattern_properties():
    schema = {"type": "object", "patternProperties": {"^x_": {"type": "integer"}},
              "additionalProperties": False}
    assert validate.validate({"x_a": 1}, schema) == []
    assert validate.validate({"x_a": "no"}, schema)


def test_validate_or_raise():
    with pytest.raises(validate.SchemaError):
        validate.validate_or_raise({}, {"required": ["a"]}, label="thing")
