# sode-factory — repo orientation

sode-factory is a software factory: the outer loop that owns work (triage → spec → implement → review → verify →
ship → measure) and drives ephemeral, isolated workers through provider-agnostic adapters, with a per-item context
record, a deterministic gate plus an evidence-required checker, seven departments with curated knowledge bases,
guards, a two-currency cost model, and a self-evolving loop over its own runs. It produces production-ready
execution tooling for real use.

> This file is orientation and pointers, not a source of truth. The constitution is
> `docs/design/sode_factory_architecture.md` (locked). The role you play here is `docs/references/sode_advisor_role_prompt.md`
> (pasted by the operator at session start). The NOW anchor is `memory/current_state.md`. Anything time-varying
> lives there, not here.

## Status
**Spec locked 2026-09-21. Build not started.** No component code exists by design (architecture before skeleton).
The first build session is S1 (C0 skeleton). See `docs/design/sode_factory_build_sessions.md`.

## Two fixed constraints (operator; never reopened)
1. **Standalone-clone value.** A fresh clone is independently valuable: `make test` green, one item shipped end to
   end on the mock provider, the tree free of any other repo's paths, ids, client names or credentials (§1.4).
2. **Architecture before skeleton.** The spec set locks before code. It is locked; a maker that must re-decide an
   architecture item stops and surfaces it.

## Read in this order
1. `memory/current_state.md` — NOW anchor (read in full, first).
2. `memory/MEMORY.md` — index of standing lessons; open one when its hook applies.
3. `backlog.yaml` — sessions S1–S21 + K1–K7 and seeds B001–B025 as items.
4. `docs/design/sode_factory_architecture.md` → `sode_factory_component_specs.md` → `sode_factory_build_plan.md`
   → `sode_factory_build_sessions.md` → `sode_factory_guard_rules_seed.yaml`.
5. `docs/audits/sode_factory_spec_review_2026-09-18.md` — why things are the way they are.
6. `docs/references/build_session_brief_template.md` — the skeleton every session brief is rendered from.

## Repo layout (locked, architecture §1.6)
`factory.yaml` · `bin/` (sode · sode-sh · sode-run) · `platform/<component>/` (one package per component C0–C15;
`platform/departments/<name>/` carries the six-part department contract) · `products/<line>/` (imports platform only
through `platform/api`) · `work/<id>/` (items: item.yaml · spec.md · decision.md · events.jsonl · record.yaml ·
briefs/ · artifacts/) · `metrics/` · `evals/` · `docs/{design,adr,runbooks,references}/` · `tests/` (mirrors platform/)
· `memory/` (in-repo advisor memory) · `.sode/` (gitignored runtime). A new top-level directory is an
operator-approved act plus an allowlist edit in the same commit.

## Invariants (the short list; full text in the architecture doc)
- One component per package; `platform/` never imports `products/`.
- Work state lives in the repo (`work/`), not in GitHub; the PR body is a generated view.
- Workers run in a fresh clone per stage; every stage starts from committed state; the engine, ledgers, secrets
  broker and logs live on the host, never inside a worker boundary.
- Labels are holds only; queue state derives from `stage`. `halted` is released only by a human.
- The deny rule set only grows; an ask rule is pruned only with evidence.
- Every metric in the registry has a formula, drivers and an owner; no formula, no metric.
- Knowledge enters a department KB only with a source; a model never writes best practices from memory.

## How to validate
Until S1 lands there is nothing to run. From S1: `make test` (the one-command gate) and
`tests/test_standalone.py` in a temp HOME. Per-commit-green: run the gate, read the output, then commit.

## Commit discipline
Subject `type(scope): description`, at most 72 characters, no trailing period. Body carries the why; the diff
carries the what. Provider attribution trailers are not used. Sode oracle trailers (`Sode-Item`, `Sode-Phase`,
`Sode-Attempt`, `Sode-Acceptance-Hash`) are required on worker commits once C2 exists. One logical change per
commit. Tag at the end of every build session. Commit identity: `alexbond <49620818+BondCrypto@users.noreply.github.com>`.

## Memory bootstrap (once per machine)
Claude Code resolves memory at `~/.claude/projects/<cwd-hash>/memory/`. This repo keeps memory in `memory/`. If
the harness directory for this folder is empty or missing, link it once:

```bash
ln -sfn "$PWD/memory" "$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
```

## Sibling relationship
The research repo growth-hack-system designed sode and dispatches sessions S1–S9. Neither repo imports the
other's internals. Ported ideas are copied, adapted and tested here with a port manifest under `platform/ports/`.
The only runtime interface between the two, when the product plane exists, is two gated artifact classes
(architecture §1.3).
