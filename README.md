# sode-factory

A software factory: the outer loop that owns work (triage → spec → implement → review → verify → ship → measure),
driving ephemeral, isolated, bounded workers through provider-agnostic adapters, with a per-item context record, a
deterministic gate plus an evidence-required checker, departments with curated knowledge bases, guards, a cost model
in two currencies, and a self-evolving loop over its own runs. It produces production-ready execution tooling for
real use.

**Status (2026-09-21): SPEC LOCKED, BUILD NOT STARTED.** This repo holds the complete specification and build plan.
No code exists yet by design (architecture before skeleton). The first build session is S1 (see the build sessions).

## Two fixed constraints
1. **Standalone-clone value** — a fresh clone of this repo is independently valuable; no dependency on any other repo's
   internals (`docs/design/sode_factory_architecture.md` §1.4 is the acceptance test).
2. **Architecture before skeleton** — nothing builds before the spec set is locked. It is locked.

## Read in this order
1. `docs/design/sode_factory_architecture.md` — the locked architecture (§1–§9, §4A, §1.6 taxonomy, §2.7 transition
   contract, Appendix A source dispositions, Appendix B apply-check walk).
2. `docs/design/sode_factory_component_specs.md` — sixteen build-ready component contracts (C0–C15): responsibility,
   interface, acceptance test, failure modes.
3. `docs/design/sode_factory_build_plan.md` — dependency order, waves, W1/W2 brief stubs, backlog seeds B001–B025.
4. `docs/design/sode_factory_build_sessions.md` — the split into fresh build sessions: S1–S19 = functional v1,
   S20–S21 = model-agnostic proof + learning tooling, K1–K7 = department KB seeding (parallel).
5. `docs/design/sode_factory_guard_rules_seed.yaml` — the verbatim deny/ask rule catalogue the guards session ports.
6. `docs/audits/sode_factory_spec_review_2026-09-18.md` — the adversarial review and its dispositions (why).
7. `backlog.yaml` — the sode-scoped backlog: every session and every seed as an item.

## How a build session starts
A fresh agent session receives ONE paste-first brief rendered from the build plan §4 stub plus the build sessions §4
contract: goal, exact spec sections to read, entry tag, touches, do-not-touch, executable acceptance, budget row, exit
criteria, report-back format, recitation. It ends with its acceptance green, `make test` green,
`tests/test_standalone.py` green, a session record, and a tag. A maker that finds it must re-decide an architecture
item stops and surfaces it; that is a defect in the spec, not a judgment call for the maker.

## Repo taxonomy (locked, §1.6)
`factory.yaml` · `bin/` · `platform/<component>/` · `products/<line>/` · `work/<id>/` · `metrics/` · `evals/` ·
`docs/{design,adr,runbooks}/` · `tests/` · `.sode/` (gitignored runtime). Placement rules and the allowlist are in
§1.6; a new top-level directory is an operator-approved act.

## Provenance
Designed in an operator-led design session (2026-09-15 → 2026-09-21) from the design inputs distilled in the sibling
research repo, two adversarial Codex reviews, and the operator's own sources. The research repo and this repo are
siblings: neither imports the other's internals; the only interface is two gated artifact classes (§1.3).
