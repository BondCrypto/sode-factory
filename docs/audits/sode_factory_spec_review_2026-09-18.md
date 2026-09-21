# sode-factory spec review — adversarial pass (2026-09-18)

**Object:** `docs/design/sode_factory_architecture.md` (§1–§9 locked) · `sode_factory_component_specs.md` (C0–C15) ·
`sode_factory_build_plan.md`. **Method:** two independent reads — Codex (gpt-5.5, reasoning=high, two halves,
~163k tokens) and the advisor's own pass — merged, de-duplicated, each finding VERIFIED against the doc text
before it was kept. **Disposition codes:** ADOPT (edit the spec before build) · DEFER (backlog seed) · REJECT
(with reason). Operator decides; nothing below is applied until approved.

## A. Verified internal contradictions (must fix regardless — the docs disagree with themselves)
| # | Contradiction | Where | Fix |
|---|---|---|---|
| A1 | "Small-class work may skip spec" vs small REQUIRES spec | §2.3 vs §4.2 | §2.3: only `trivial` skips spec |
| A2 | `measure` runs AFTER ship, but its BASELINE is captured BEFORE ship; `ship` requires a "closed/complete record" yet the measure verdict lands later | §2.1 · §4.7 · §5.3 · C11 | split `record_complete_for_ship` (baseline captured as a verify artifact) from `record_complete_after_measure` |
| A3 | Security depth: class table says small=D1/medium=D2/large=D3; depth table says D0 for "any GREEN" — a large GREEN item is ambiguous | §4.2 vs §4.3 | one rule: depth = max(class floor, lane, overlay); lane/overlay can only RAISE |
| A4 | Human review: "human for YELLOW/RED" vs "medium = spec lock only" vs "YELLOW after shadow runs" | §2.1 · §6.2 · §8.6 | one pre-shadow / post-shadow rule stated once in §6.2; §2.1 points to it |
| A5 | Gate and checker run CONCURRENTLY, yet the checker's input includes the gate result | §6.1 vs §6.4 | checker receives the T0 (commit-time) result + last T1 if any; T1 runs concurrently |
| A6 | Build: "W2+ built BY sode" but the engine (C2) and brief renderer (C5) ARE W2 | build §0/§4 vs §1 | bootstrap from this repo through W2; dogfood starts W3 |
| A7 | C11 depends on C14 but is ordered before it | build §1 rows 15–16 | swap |
| A8 | C5 renders from department KB, but departments (C9) come four rows later | build §1 | C5 renders with an EMPTY KB slice in W2; C9 fills it |
| A9 | C7 "depends only on C0" but its checks need brief lint (C5), acceptance (C1), record completeness (C6) | build §1 | C7 lands in two steps: core registry + toolchain checks (W2), item-aware checks after C5/C6 |
| A10 | GitHub mirror: "two-way sync adapter" in §4.1 vs LATER in build §2; C6 specs only PR-body upsert + comment harvest | §4.1 vs build §2 vs C6 | §4.1: v1 = PR body view + comment harvest; issue mirror = LATER |
| A11 | Beads: "if adopted, our scheduler/lease code is NOT built" vs beads review deferred until AFTER W3 (when C1/C2 exist) | §4.1a vs build §3 | decide: build native (recommended) and drop the "delete if adopted" clause; beads = a plain backlog item |
| A12 | `sode init` writes `policy_profile: standard` (needs GitHub, 1Password) yet `doctor` must exit 0 offline in the standalone test | C0 vs §3.3 vs C10 | standalone test runs `sode init --profile local --provider mock`; `standard` checks are gated on profile |
| A13 | Dead reference "§11 measure windows" in C15; "no KB" in §1.2 vs department `kb/` in §4A | C15 · §1.2 | fix ref; say "no RESEARCH KB" |

## B. Missing — will strike in operation (both reviews converge on the first five)
| # | Gap | Fix | Disp. |
|---|---|---|---|
| B1 | **No merge queue / stale-base policy.** Items branch from a pinned base; main moves; green-on-old-base ≠ green-on-main | `ship` = one-at-a-time rebase onto current main → re-run T1 + checker on the post-rebase diff → ship; a conflict-fixer stage body (spec + both sides + hunks + acceptance ids) then full re-verify | ADOPT (C10) |
| B2 | **Side effects lack action ids.** Re-tick re-emits "the same pending action" but nothing stops a second spawn/push/notify | `.sode/actions.jsonl` with `action_id` (deterministic from item+stage+attempt), `claimed_by`, `pid`, `result_ref`; every external effect keys on it | ADOPT (C2) |
| B3 | **No watchdog / liveness model.** Workers hang, wedge on tests, hit prompts, die without exit | PORT `dispatch_watchdog` shape: heartbeat = transcript mtime + commit count; no-output timeout; wall-clock cap; process-group kill; classify-on-timeout; stale-clone quarantine | ADOPT (C3) |
| B4 | **Acceptance `cmd` and `impact_metric.read_cmd` are arbitrary host commands** run by the ENGINE, outside the worker shim | one policy runner `sode-run` for every deterministic command (acceptance, metric reads, setup hooks, gate checks): env scrub, cwd fence, timeout, output cap, same deny floor, no secrets by default | ADOPT (C4/C7) |
| B5 | **Secrets scoped at launch, not at capture.** `op run` env → transcripts, shim log, records, PR bodies, trajectories | redaction pipeline before ANY write; shim denies env dumps; positive-secret fixture proves absence under git AND `.sode/`; secret ids + allowed stages registry | ADOPT (C3/C4/C13) |
| B6 | **Git policy underspecified**: remotes, push refspecs, identity, signing, protected patterns | `platform/policy/git.yaml`: allowed remotes, worker refspec `sode/<id>` only, canonical identity, commit-message rule (commit-msg hook in the clone), protected branches | ADOPT (C3/C4) |
| B7 | **Environment provisioning absent** beyond `git clone` | per-target manifest: `setup`, `test_cmd`, `cache` (namespaced outside clones), `services`, `healthcheck`, `clean`; per-target gate config | ADOPT (C3/C7) |
| B8 | **No schema versions / migrations** for factory.yaml, item, record, events, trajectories, predictions, metrics history | `schema_version` on every artifact + `sode migrate --check|--apply` BEFORE dogfood creates history | ADOPT (C0) |
| B9 | **Human decisions harvested from free-form comments** can be spoofed, stale, or ambiguous | hash-bound command protocol: `/sode approve spec <hash>`, `approve ship <hash>`, `reject`, `needs-info`; trusted-actor list; a decision binds to the artifact hash it approved | ADOPT (C6) |
| B10 | **Subscription headroom may be unreadable** (checked: neither CLI exposes a usage verb) | fallback chain: provider read → local usage estimate + operator UI% sample (this repo's model) → widened reserve when only an estimate exists; stale-headroom expiry; never a permanent stall | ADOPT (§9.1/C12), mark RISK |
| B11 | **YELLOW auto-ship rule has no minimum sample** (0/5 passes "<2%") | n ≥ 50 per class × department, Wilson upper bound < 2%, canary fresh, reset on model/config change | ADOPT (§6.2/C8) |
| B12 | **Stacked children**: children built on the parent's old base; merge order undefined | stack id + parent branch ref; restack on parent merge; cumulative acceptance at the stack tip | ADOPT (C1/C10) |
| B13 | **Review↔fix loop unbounded** across stages; no finding ids | `max_review_rounds`; finding ids; re-check only addressed findings; stale-finding invalidation | ADOPT (C8) |
| B14 | **Spec changes after lock are silent** | spec hash pinned at lock; change → back to `ready-to-spec` | ADOPT (C5) |
| B15 | **Event storage inconsistent** (`events[]` inside record vs `record.yaml.events` vs C6 projection) | `events.jsonl` append-only per item = SOURCE; `record.yaml` = pure projection | ADOPT (§5/C2/C6) |
| B16 | `touches` is metadata, not a lock: semantic conflicts, ports, caches, manifests | resource/path leases from `touches` at dispatch; "compatible parallelism" rule | ADOPT-lite (path leases only) |
| B17 | No terminal `cancelled`; no revert path | `cancelled` label; `sode revert <id>` → expedited small item | ADOPT (§4.4/C10) |
| B18 | Scheduling policy absent (`ready` lists, nothing picks) | priority + WIP limit per department + lane concurrency + rate headroom as global cap | ADOPT (C1/C2) |
| B19 | Clone GC; `.sode/` evidence not portable across machines | GC policy by age+label; `sode archive-run` / `import-run` | DEFER |
| B20 | Time discipline incomplete (UTC vs wall clock vs monotonic) | one clock library: UTC timestamps, monotonic durations, reboot handling | ADOPT (C2) |
| B21 | Provider outage / retry taxonomy | adapter error classes (auth · rate · outage · CLI drift) → hold with backoff; "adapter degraded" disables auto-ship | ADOPT (C3) |
| B22 | Worker at context limit: compaction vs handoff undefined | handoff note + PARTIAL; never compact | ADOPT (C3) |
| B23 | `work/` location when target ≠ sode is unstated | `work/` lives in the SODE repo (the brain); PR body is the view in the target | ADOPT (§4.1) |

## C. Over-engineering — elegant replacements (recommendations; several touch LOCKED items → operator call)
| # | Component | Elegant replacement | Disp. |
|---|---|---|---|
| C1 | C13 full Observe store in v1 (scorers · replay · experience bank · distillation) | keep in v1 ONLY the irreversible part: trajectories (append-only jsonl + transcript refs, hash-chained) + `active.json` + the eval golden-set skeleton; scorers/replay/distillation = v1.1 after the WALK milestone. §7 lock (store first) is honoured; the learner tooling waits for data | RECOMMEND (re-scopes §7 timing, not its decision) |
| C2 | Six departments with KBs/seats on day one | three REAL (security · qa_quality · factory_ops) + three contract-satisfying stubs; graduate a stub when it has repeated findings + fixtures | RECOMMEND (§4A) |
| C3 | Eight metric groups + alerts at bootstrap | registry stays; SEED it with five hard metrics (lead time · first-pass gate rate · re-dispatch rate · escapes · headroom); the group discussions add the rest | RECOMMEND (§9.6) |
| C4 | `measure` on every medium/YELLOW item = ceremony for maintainability changes | no exemption: the DEFAULT `impact_metric` for refactor/maintainability items is the code-quality metric (complexity/LOC delta), always readable | ADOPT (§4.7) |
| C5 | D0–D3 security machinery front-loaded | D0 always; D1 checklist for small/medium; D2/D3 only for secrets/auth/money/deps/runner/guard changes and RED | RECOMMEND (§4.3 — narrows D2 default for medium) |
| C6 | Two real adapters in W4 | mock + ONE real adapter (Claude Code) through dogfood; Codex adapter in W5 proves the abstraction on real work | RECOMMEND (build §1) |
| C7 | Stable-prefix cache layout as an ACCEPTANCE target | deterministic rendering + size budget are acceptance; cache-hit is MEASURED, not asserted | ADOPT (C5/§9.4) |
| C8 | Restricted profile as a full GO port | two booleans (`allow_push`, `allow_self_fire`) + kill switch; the GO file stays this machine's artefact | ADOPT (§3.4/§8.4) |
| C9 | Two lints (`lint-item`, `lint_acceptance`); two state fields (`label` + `stage`) | one `sode lint`; `label` only for holds, queue state derived from `stage` | ADOPT (C1/C5/§4.4) |
| C10 | Canary corpus at every review | canary on adapter/model/checker/prompt change + weekly + always before enabling auto-ship | ADOPT (C8) |
| C11 | Full quality kit for every component | acceptance + one bad fixture minimum; RED components = full kit | RECOMMEND (build §0 — relaxes [[process_genesis_quality_kit]] for non-RED) |
| C12 | Beads detail inside the locked architecture | shrink §4.1a to one backlog pointer; build the native store | ADOPT (§4.1a) |

## D. What a Cursor/Warp factory engineer would add (80/20)
D1 **planner + replan transition** — on child HALT / stale base / conflict / repeated PARTIAL / dependency landed / metric regression, the parent returns to `spec` with the failure handoff (ADOPT §2/§4.5) · D2 **richer handoff payload** — report-back adds `concerns[]`, `assumptions[]`, `rejected_paths[]`, `suggested_followups[]` (ADOPT §5.2) · D3 **live control room** — `sode ps` / `status --live`: items, stages, clones, pids, leases, provider, spend, current command, stuck age; plus a global `.sode/events.jsonl` + `sode tail` (ADOPT C10/C14) · D4 **capability tests per adapter** — can edit / run shell / interrupt / install hook / report usage / resume (ADOPT C3) · D5 **formal state table** for C2 — no double spawn, no skipped review, no ship without baseline, no terminal item with an open child (ADOPT C2 as a test table; TLA+ later) · D6 **freshness on every context input** — `reviewed_on` + source hash on KB, seat memory, checklists; stale-context warning in the brief (ADOPT C9) · D7 **container runner sooner** for acceptance scripts / dependency installs / external targets (DEFER, seeded).

## E. Bookkeeping that prevents silent drift (registries + ongoing checks)
E1 **one generated policy authority** `platform/policy/classes.yaml` → doc tables + fixtures for every class × lane × overlay (ADOPT) · E2 **port-conformance manifest** per ported asset: source path, source commit, adapted invariants, dropped behaviour, tests (ADOPT §1.5) · E3 **acceptance identity**: `acceptance_hash`, run/phase ids, branch metadata (ADOPT C2) · E4 **schema registry** with versions + migrations for run state, events, record, trajectories, predictions, metrics, gate JSON (ADOPT = B8) · E5 **guard rule provenance**: rule ids, source ref, threat class, example; deny monotone; ask-prune EVIDENCE ledger (a removal must cite an item with holds data); deployed-shim/hook drift check (ADOPT C4) · E6 **evaluator manifest**: hashes for gate registry, scorer rubrics, canary corpus, golden set, holdout (ADOPT C13) · E7 **adapter registry**: cli_version pin vs installed, permission mapping, usage-field contract, fixture version; fail on unknown CLI (ADOPT C3) · E8 **gate outcomes ledger** with human adjudication of TP/FP (ADOPT C7) · E9 **KB lifecycle**: staleness threshold, owner, supersession (ADOPT C9) · E10 **routing coverage**: unowned path = FAIL, overlap precedence, fallback dept (ADOPT C1) · E11 **shadow ledger statistics**: denominator, window, bound, taxonomy, reset (ADOPT = B11) · E12 **metric field bindings**: formula referencing an unknown field = gate FAIL; every registry id has a compute impl (ADOPT C14) · E13 **secrets registry**: ids, allowed stages, redaction policy, broker-unavailable behaviour (ADOPT = B5) · E14 **a weekly `sode drift` sweep** running E1–E13 as an automation (ADOPT C15).

## F. Enforcement gaps (rule without mechanism / mechanism without test)
F1 shim bypass proof per provider (raw shell, provider-native tools) · F2 `sode halt` process semantics (process groups, signal escalation, freeze, recovery test) · F3 evaluator boundary fenced by guard rules (non-architecture edits to `evals/`, rubrics, gate registry = denied) · F4 positive-secret redaction tests · F5 PR-comment authority (trusted actors, commands, spoof tests) = B9 · F6 policy-profile matrix tests (push, ship, continuity, automations, doctor × standard/restricted) · F7 tamper-evident audit trail = hash chain + `sode verify-log` + a compromise-runbook fixture · F8 promote/rollback failure injection · F9 "worker never edits `record.yaml` / never writes outside its clone" enforced by shim path rules · F10 measure `read_cmd` sandboxed = B4. All ADOPT.

## G. Top-10 before the build (merged)
1. Fix the bootstrap circularity: this repo dispatches W1+W2; dogfood starts W3 (build §0/§1/§4).
2. Add the merge queue + conflict fixer to `ship` (C10) — the highest-leverage primitive after clone isolation.
3. Add action ids + the watchdog + `sode-run` command sandbox (C2/C3/C4/C7).
4. Add the secret redaction pipeline + secrets registry + positive tests (C3/C4/C13).
5. One generated class × lane × overlay policy table; fix A1/A3/A4 (§2.3/§4.2/§4.3/§6.2/C1).
6. Split record completeness for ship vs after measure; events.jsonl as source (§2.1/§4.7/§5/C2/C6/C11).
7. Fix build dependencies (A7–A9) and profile-gated doctor (A12).
8. Statistical auto-ship rule + shadow ledger schema (§6.2/C8).
9. Schema versions + `sode migrate`; port-conformance manifest; git policy file (C0/§1.5/C3).
10. Decide the C-section re-scopes (C1, C2, C3, C5, C6, C11) — each touches a locked item's TIMING or default, not its decision.

## H. Rejected
- "Cloud sandboxes by default" — conflicts with local-first + standalone; container runner stays a later backend.
- "Drop `measure` for factory internals" — operator requirement; resolved by the default code-quality metric (C4).
- "Advisory-only review verdict" — weaker than the locked evidence-required gate.
