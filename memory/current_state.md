---
name: current_state
description: "The single NOW anchor for sode advisor sessions — HEAD, status, what landed, the immediate next step, in-flight sessions, open operator decisions. Read first at every session open. Update at every wrap. Keep lean."
metadata:
  type: project
---

> Standing rule: this file records the LIVE position only. Landed work belongs in git and tags; durable lessons in
> topic memories; tasks in `backlog.yaml`. If you append a block, delete one.

### NOW (2026-09-22): S1 LANDED · C0 SKELETON GREEN · PUSHED

- **HEAD:** `a58f4ed`, tag `s1-skeleton`, pushed to `origin/main` (13 commits from f0ce094).
- **Status:** S1 (C0 skeleton) landed. `sode` CLI live — `init · doctor · version · migrate`; `factory.yaml`
  schema (§3.3 shape); CLI registry (34 verbs, C1–C15 = `planned`); ports-manifest gate; 7 department stub dirs.
  Spec set LOCKED (operator 2026-09-21).
- **Gate / standalone:** `make test` GREEN (74 tests + 4 checks: repo-structure · schema-doc-sync · ports ·
  grep-clean). `tests/test_standalone.py` GREEN in a temp HOME (skeleton form; `make test-all` includes it).
- **New dep:** PyYAML pinned `>=6.0,<7` in `requirements.txt` — the one runtime dep (YAML config); rest stdlib.
- **Backlog:** 53 items — S2–S21, K1–K7, seeds B001–B025 pending.

### IMMEDIATE NEXT
1. **S2 — C1 work store** (item schema · `classes.yaml` generated tables · routing · scheduler · leases on disk ·
   `sode new/ready/hold/dep/lint` · triage output schema). Depends on S1 (done). Sequential on main.
2. **S3 — C4 guards (RED)** then **S4 — C3 worker runtime** complete W1; S4 depends on S1 + S3.
3. **K1–K3 KB seeding, parallel** (security · qa_quality · factory_ops) from our own material; each in a SEPARATE
   clone (touches `platform/departments/*/kb/` only). K3 REQUIRED before S10.

### IN-FLIGHT
none.

### OPEN OPERATOR DECISIONS
none. (Product-plane design session = seed B005; waits for a `paper_validated_card`.)

### S1 FOLLOW-UPS (carry forward; not blockers)
- `platform` package name shadows stdlib `platform` (LOCKED §1.6) — hardening follow-up (conftest guard or
  interpreter pin); works today.
- `secrets.yaml` (referenced by `factory.yaml`) lands at S3/C4; doctor skips it in `local`, would FAIL in
  `standard`/`restricted`.
- Fold the 4 S1 bootstrap gate checks into the real gate registry at S6/C7a. Interpreter 3.14.7 vs spec 3.12 — pin.
