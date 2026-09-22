"""platform.schema.validate — a small, dependency-free JSON Schema validator.

sode is stdlib-first and must clone offline, so validation ships in-tree rather
than depending on an installed ``jsonschema``. This supports the subset the
factory's schemas actually use: ``type`` (single or list), ``properties``,
``required``, ``additionalProperties`` (bool or subschema), ``enum``, ``const``,
``items``, ``patternProperties``, ``minimum`` and ``maximum``. It returns a list
of human-readable error strings (empty means valid).
"""
from __future__ import annotations

import re
from typing import Any

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _type_ok(value: Any, type_spec: "str | list[str]") -> bool:
    types = [type_spec] if isinstance(type_spec, str) else list(type_spec)
    return any(_TYPE_CHECKS.get(t, lambda _v: False)(value) for t in types)


def _resolve_ref(ref: str, root: "dict[str, Any]") -> "dict[str, Any]":
    if not ref.startswith("#/"):
        raise SchemaError(f"unsupported $ref {ref!r} (only local '#/...' refs are supported)")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _validate(
    value: Any,
    schema: "dict[str, Any]",
    path: str,
    errors: "list[str]",
    root: "dict[str, Any] | None" = None,
) -> None:
    if not isinstance(schema, dict):
        return
    if root is None:
        root = schema

    if "$ref" in schema:
        _validate(value, _resolve_ref(schema["$ref"], root), path, errors, root)
        return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']!r}")

    if "type" in schema and not _type_ok(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']!r}, got {type(value).__name__}")
        return  # further keyword checks assume the type matched

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        addl = schema.get("additionalProperties", True)
        patterns = schema.get("patternProperties", {})
        for key, sub in value.items():
            child = f"{path}.{key}" if path else key
            if key in props:
                _validate(sub, props[key], child, errors, root)
                continue
            matched = False
            for pat, psub in patterns.items():
                if re.search(pat, key):
                    _validate(sub, psub, child, errors, root)
                    matched = True
                    break
            if matched:
                continue
            if addl is False:
                errors.append(f"{path}: additional property {key!r} is not allowed")
            elif isinstance(addl, dict):
                _validate(sub, addl, child, errors, root)

    elif isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, item in enumerate(value):
                _validate(item, item_schema, f"{path}[{i}]", errors, root)

    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} > maximum {schema['maximum']}")


def validate(instance: Any, schema: "dict[str, Any]") -> "list[str]":
    """Return a list of validation errors; empty means the instance is valid."""
    errors: list[str] = []
    _validate(instance, schema, "", errors)
    return errors


class SchemaError(ValueError):
    """Raised by :func:`validate_or_raise` when an instance is invalid."""


def validate_or_raise(instance: Any, schema: "dict[str, Any]", label: str = "artifact") -> None:
    errors = validate(instance, schema)
    if errors:
        raise SchemaError(f"{label} failed schema validation:\n  - " + "\n  - ".join(errors))
