# sode-factory

A software factory: the outer loop that owns work (triage → spec → implement →
review → verify → ship → measure) and drives ephemeral, isolated workers through
provider-agnostic adapters. A fresh clone is independently valuable and runs
offline on a mock provider (architecture §1.4).

**Status:** C0 skeleton (build session S1). The clonable root, the `factory.yaml`
schema, the `sode` CLI (`init` · `doctor` · `version` · `migrate`), the CLI verb
registry, and the one-command gate exist. The lifecycle engine, work store,
guards, gate registry and departments land in later sessions (see
`docs/design/sode_factory_build_sessions.md`).

## How to validate

Requires Python 3.12+ and PyYAML (`pip install -r requirements.txt`); no network.

```bash
git clone https://github.com/BondCrypto/sode-factory.git && cd sode-factory
make test                                    # the one-command gate: pytest + structural checks
./bin/sode init --profile local --provider mock   # write factory.yaml + .sode/ (offline default)
./bin/sode doctor                            # validate the tree + environment (exit 0 in local)
```

`make test` runs the pytest suite and the four S1 structural checks
(`check_repo_structure` · `check_factory_schema_doc_sync` · `check_ports` ·
`check_grep_clean`). `make test-all` also runs the standalone end-to-end
(`tests/test_standalone.py`), which copies the tree into a throwaway HOME and
re-runs the gate to prove the clone carries no machine-local dependency.

## Layout

- `factory.yaml` — the versioned factory definition (machine-local binding lives
  in the gitignored `.sode/local.yaml`).
- `bin/` — `sode` (operator + engine CLI) plus `sode-sh` / `sode-run` (worker
  binaries; stubs until session S3).
- `platform/` — the factory plane, one package per component (C0–C15).
- `products/` — the product plane (imports `platform` only through `platform/api`).
- `work/` · `metrics/` · `evals/` — work items, the metric registry, the eval set.
- `docs/` — the locked spec set, ADRs and runbooks.
- `tests/` — mirrors `platform/`, plus `tests/test_standalone.py`.

The spec set under `docs/design/` is the source of truth. Start with
`docs/design/sode_factory_architecture.md`.
