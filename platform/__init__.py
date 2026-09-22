"""platform — the sode-factory FACTORY plane (architecture section 1.6).

NOTE: this package is deliberately named ``platform`` per the locked repo taxonomy
(section 1.6). Within this repo's execution context it therefore shadows the
stdlib ``platform`` module; no factory code imports the stdlib module (use ``sys``
/ ``os`` for host facts). See work/sessions/S1/report.yaml (concerns).
"""

__version__ = "0.1.0"  # C0 skeleton (S1); the sode CLI version.
