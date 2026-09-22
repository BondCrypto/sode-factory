"""tests.cli.test_registry — the CLI verb registry is the single authority.

Every C0-documented verb is registered; every field is present; every `stable`
verb has a real handler and every `planned` verb routes to the planned handler.
A stable verb whose handler is missing at its stability level is caught here.
"""
from __future__ import annotations

from platform.cli import dispatch, registry

# The verb set documented in the C0 component spec (docs/design/..._component_specs.md).
C0_DOCUMENTED_VERBS = {
    "init", "doctor", "version", "migrate", "new", "intake", "ready", "hold",
    "release", "dep", "lint", "tick", "status", "ps", "tail", "stop-all",
    "brief", "record", "gate", "ratchet", "kb", "ship", "revert", "handoff",
    "resume", "measure", "metrics", "headroom", "automations", "drift",
    "harness-card", "promote", "rollback", "gc",
}


def test_registry_lists_exactly_the_documented_verbs():
    names = set(registry.verb_names())
    assert names == C0_DOCUMENTED_VERBS
    assert len(registry.verbs()) == 34


def test_every_verb_carries_the_required_fields():
    for v in registry.verbs():
        for key in registry.REQUIRED_VERB_KEYS:
            assert key in v, f"{v.get('verb')!r} missing {key!r}"
        assert v["stability"] in registry.STABILITIES
        assert isinstance(v["profiles"], list) and v["profiles"]


def test_stable_verbs_are_exactly_the_c0_four():
    stable = {v["verb"] for v in registry.verbs() if v["stability"] == "stable"}
    assert stable == {"init", "doctor", "version", "migrate"}


def test_every_stable_verb_has_a_handler_and_vice_versa():
    stable = {v["verb"] for v in registry.verbs() if v["stability"] == "stable"}
    handlers = set(dispatch.HANDLERS)
    # The invariant the gate relies on: stable verbs and implemented handlers match.
    assert stable == handlers, f"stable/handler mismatch: {stable ^ handlers}"


def test_missing_handler_at_stable_level_is_detectable():
    # Simulate a stable verb with no handler; the same set-difference the real
    # invariant uses must flag it (this is what would fail the gate).
    stable = {v["verb"] for v in registry.verbs() if v["stability"] == "stable"}
    handlers = set(dispatch.HANDLERS) - {"doctor"}
    assert stable - handlers == {"doctor"}


def test_planned_verbs_are_not_in_handlers():
    planned = {v["verb"] for v in registry.verbs() if v["stability"] == "planned"}
    assert planned.isdisjoint(dispatch.HANDLERS)
    assert "new" in planned and "gate" in planned


def test_separate_binaries_are_recorded_not_as_verbs():
    names = {b["name"] for b in registry.binaries()}
    assert {"sode", "sode-sh", "sode-run"} <= names
    assert "sode-sh" not in registry.verb_names()
