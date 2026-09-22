# Makefile — the one-command gate (architecture section 1.4, C0 acceptance).
#
# `make test` is the S1 gate: the pytest suite over tests/ (excluding the
# standalone end-to-end, which re-invokes `make test` in a fresh copy) plus the
# four structural checks that C6/C7 later fold into the real gate registry.
# `make test-all` adds the standalone e2e. Stdlib-first; the only dependency is
# PyYAML (see requirements.txt).

PY ?= python3
PYTEST ?= $(PY) -m pytest

.PHONY: test test-all unit gate standalone setup clean help

test: unit gate            ## the one-command S1 gate (fast; the standalone e2e re-runs this in a copy)

unit:                      ## the pytest suite, minus the standalone e2e (kept non-recursive)
	$(PYTEST) tests/ --ignore=tests/test_standalone.py -q

gate:                      ## the four structural checks against the real tree (S1 bootstrap gate)
	$(PY) -m platform.cli.gate_bootstrap

standalone:                ## the fresh-clone end-to-end (copies the tree, runs `make test`, init, doctor, grep)
	$(PYTEST) tests/test_standalone.py -q

test-all: unit standalone gate   ## everything, including the standalone e2e

setup:                     ## provisioning manifest hook (factory.yaml targets.self.setup)
	@echo "sode setup: stdlib-first. Ensure PyYAML is present: $(PY) -m pip install -r requirements.txt"

clean:                     ## remove Python and pytest caches
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache

help:                      ## list the targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/' | sort
