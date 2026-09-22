"""platform.cli.dispatch — the `sode` entry point.

Resolves the first argument to a registered verb and calls its handler. C0
implements ``init``, ``doctor``, ``version`` and ``migrate``; every other v1 verb
is registered and routes to the planned handler (which names its owning session).
A verb absent from the registry is an error.
"""
from __future__ import annotations

from . import registry
from .doctor_cmd import cmd_doctor
from .init_cmd import cmd_init
from .migrate_cmd import cmd_migrate
from .planned import planned_handler
from .version_cmd import cmd_version

# The implemented (stable) handlers. Every key here must be a registry verb whose
# stability is `stable`; every `stable` registry verb must appear here. A test
# pins both directions.
HANDLERS = {
    "init": cmd_init,
    "doctor": cmd_doctor,
    "version": cmd_version,
    "migrate": cmd_migrate,
}


def _usage() -> None:
    print("sode — the software-factory CLI")
    print("\nusage: sode <verb> [args]\n")
    impl = sorted(HANDLERS)
    print("implemented (S1):", " ".join(impl))
    planned = sorted(v["verb"] for v in registry.verbs() if v["verb"] not in HANDLERS)
    print("planned:         ", " ".join(planned))
    print("\nseparate binaries:", " ".join(b["name"] for b in registry.binaries()))


def main(argv: "list[str]") -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        _usage()
        return 0
    if argv[0] in ("-V", "--version"):
        return cmd_version(argv[1:])

    verb, rest = argv[0], argv[1:]
    entry = registry.get(verb)
    if entry is None:
        print(f"sode: unknown verb {verb!r} -- it is not in platform/cli/registry.yaml.")
        print("      run `sode help` for the verb list; a new verb needs a registry entry.")
        return 2

    handler = HANDLERS.get(verb)
    if handler is not None:
        return handler(rest)
    return planned_handler(verb, rest)
