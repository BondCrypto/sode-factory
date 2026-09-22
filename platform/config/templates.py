"""platform.config.templates — build factory.yaml / local.yaml for a profile.

A profile is exactly two booleans plus the kill switch (review C8): ``standard``
= push/self-fire true, ``restricted`` = false/false, ``local`` = false/false with
the mock provider and no broker (the standalone-test profile). The default init
is ``local`` + ``mock`` so a fresh clone runs offline (review A12).
"""
from __future__ import annotations

from typing import Any

PROFILES = ("local", "standard", "restricted")
PROVIDERS = ("mock", "anthropic_cli", "openai_cli")

# The declarative capability matrix (architecture section 3.3). Written whole into
# every factory.yaml; stages bind to one of these providers.
_PROVIDER_MATRIX = {
    "anthropic_cli": {
        "adapter": "claude_code_cli", "billing": "subscription",
        "families": ["claude"], "tools": ["bash", "edit", "read"], "hooks": "claude_hooks",
    },
    "openai_cli": {
        "adapter": "codex_cli", "billing": "subscription",
        "families": ["gpt"], "tools": ["bash", "edit", "read"], "hooks": "codex_config",
    },
    "mock": {"adapter": "mock", "billing": "none", "families": ["mock"]},
}


def _cross_family_reviewer(provider: str) -> str:
    if provider == "anthropic_cli":
        return "openai_cli"
    if provider == "openai_cli":
        return "anthropic_cli"
    return "mock"


def _stages(provider: str) -> "dict[str, Any]":
    reviewer = _cross_family_reviewer(provider)
    is_mock = provider == "mock"
    return {
        "spec": {
            "provider": provider, "model": None, "permission": "plan_only",
            "budget": {"rate_pct": 3, "cost_m": 0.5}, "max_attempts": 2, "secrets": [],
        },
        "implement": {
            "provider": provider, "model": None, "permission": "edit_in_clone",
            "budget": {"rate_pct": 8, "cost_m": 2.0}, "max_attempts": 3, "secrets": [],
        },
        "review": {
            "provider": reviewer, "model": None, "permission": "read_only",
            "budget": {"rate_pct": 2, "cost_m": 0.5}, "max_attempts": 1, "secrets": [],
            "cross_family_required": not is_mock,
        },
        "verify": {"provider": "none"},
        "ship": {"provider": "none"},
    }


def build_factory(profile: str, provider: str) -> "dict[str, Any]":
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}; choose from {PROFILES}")
    if provider not in PROVIDERS:
        raise ValueError(f"unknown provider {provider!r}; choose from {PROVIDERS}")
    # The local profile is offline by contract: mock provider, no broker.
    if profile == "local":
        provider = "mock"
    broker = "none" if profile == "local" else "1password"
    return {
        "schema_version": 1,
        "policy_profile": profile,
        "isolation": "clone",
        "secrets_broker": broker,
        "secrets_registry": "platform/policy/secrets.yaml",
        "targets": {
            "self": {
                "path": ".",
                "default_branch": "main",
                "setup": "make setup",
                "test_cmd": "make test",
                "cache": {"dir": ".sode/cache/self", "key": ["lockfile_hash"]},
                "healthcheck": "sode doctor --target self",
                "gate": {"t0": ["lint", "types", "unit_changed"], "t1": ["all"]},
            }
        },
        "git": "platform/policy/git.yaml",
        "reserve_pct": 15,
        "runners": {
            "local_clone": {
                "isolation": "clone",
                "watchdog": {"heartbeat_s": 120, "no_output_s": 900, "wall_clock_s": 7200},
            }
        },
        "automations": [],
        "integrations": {"github": {"mode": "pr_view"}, "chat": None},
        "decision_model": None,
        "scorers": {
            "sample_rate": 0.25,
            "dimensions": [
                "task_compliance", "procedure_compliance", "verbosity",
                "efficiency", "code_quality",
            ],
        },
        "providers": dict(_PROVIDER_MATRIX),
        "stages": _stages(provider),
    }


def build_local(profile: str, provider: str) -> "dict[str, Any]":
    if profile == "local":
        provider = "mock"
    broker_kind = "none" if profile == "local" else "1password"
    broker_state = "unavailable" if profile == "local" else "unknown"
    providers = {
        name: {
            "cli_path": None,
            "cli_version": None,
            "privacy_mode": "n/a" if name == "mock" else None,
            "operator_attested_on": None,
        }
        for name in PROVIDERS
    }
    return {
        "schema_version": 1,
        "profile": profile,
        "broker": {"kind": broker_kind, "state": broker_state},
        "providers": providers,
        "headroom_samples": [],
    }
