# sode-factory — build plan

**Status:** LOCKED (agenda 10, operator 2026-09-18) — amended per `docs/audits/sode_factory_spec_review_2026-09-18.md`. Consumes `sode_factory_architecture.md` (LOCKED §1–§9) +
`sode_factory_component_specs.md` (C0–C15). Components in DEPENDENCY ORDER; each carries its acceptance test
(from the spec), a dispatch-brief STUB, class/lane, and v1 vs LATER. The build fires under the standing gate
(synthesis §5: no PRODUCT code before a `paper_validated_card`; the FACTORY plane has no such gate).

## 0. Ground rules for the build
- **Architecture before skeleton — satisfied by these three docs.** A maker re-deciding any §1–§9 item = stop
  and surface.
- **Where the build runs.** Until sode exists, its bootstrap bricks live HERE (synthesis §5): `sode_bootstrap.py`
  creates the sibling from these specs. **W1 AND W2 are dispatched from THIS repo** (sode cannot brief, tick, record
  or gate its own items until C1 + C2 + C5 + C6 + C7a exist — review A6); the first maker builds C0 in a fresh
  sibling dir (`../sode-factory/`, a NEW git repo — not a clone of this one). **Dogfood starts at W3**: from then on
  every component is a sode work item built BY sode (the walk milestone proves it).
- **Per-commit-green · one logical change per commit · pinned deps via `sfw`. No PROVIDER attribution trailers
  (`Co-Authored-By`, `Generated-with`); the `Sode-*` oracle trailers (item · phase · attempt · acceptance hash) ARE
  required where the oracle reads them (hawk A17).**
- **Code quality applies to ALL code, every wave** (operator 2026-09-18): lean · senior-engineer style · solves the
  task, never games the test · passes the gate (lint · types · complexity budget · anti-gaming checks) · passes the
  QA ten-angle review. No exceptions by class or lane.
- **Process-genesis kit** ([[process_genesis_quality_kit]]): RED components ship the FULL kit (bar · deterministic
  checker · known-bad fixtures · pilot · risk table · run report); every other component ships at minimum executable
  acceptance + one known-bad fixture per check (review C11).
- **Maker tier**: implement = the pinned worker tier; spec/review = a different family where configured.

## 1. Dependency-ordered build (v1)
| # | Component | Depends on | Class / lane | Acceptance (headline) | Wave |
|---|---|---|---|---|---|
| 1 | C0 skeleton + schema + CLI + mock harness | — | medium / YELLOW | `make test` green in a temp HOME; `sode doctor` 0; BAD schema fixture refused | W1 |
| 2 | C1 work store + class table + scheduler | C0 | medium / YELLOW | table-driven `required_stages` = doc table; blocked item excluded from `ready` | W1 |
| 3 | C4 guards: shim + rules + installers | C0 | large / RED (security) | known-bad corpus all denied; deny set monotone test | W1 |
| 4 | C3 worker runtime (provisioner · adapter iface · mock adapter) | C0, C4 | medium / YELLOW | clone isolation asserted; env scrub AST test; mock end-to-end | W1 |
| 5 | C5 brief renderer + ONE lint + spec-lock brief + report-back (EMPTY KB slice allowed) | C1 | medium / YELLOW | determinism; size budget; provider-neutral; poisoned fixtures fail; spec-hash re-lock | W2 |
| 6 | C7a gate core: registry · cache · toolchain + anti-gaming checks · `sode-run` execution | C0, C1, C4 | medium / YELLOW | every check has remediation + a BAD fixture; 0-checks-run = FAIL; anti-gaming fixtures fail T0 | W2 |
| 7 | C2 lifecycle engine + leased ledger + actions ledger + classify + replan + clock | C1, C3, C5 | large / RED (core) | one-transition-per-tick + invariant table; double-fire; duplicate action_id cannot double-advance; corrupt=FATAL | W2 |
| 8 | C6 context record (events.jsonl source · projection · two completeness gates · hash-bound decisions · redaction) | C2, C5 | medium / YELLOW | golden projection; no report-back → PARTIAL; untrusted approve = note; invalidated on hash change | W2 |
| 9 | C7b item-aware gate checks (brief lint · acceptance · record completeness · port manifests) | C5, C6, C7a | small / GREEN | each with a BAD fixture | W3 |
| 10 | C9 departments: loader · seven contract dirs · KB entry schema · `kb_ready` gate · `sode kb seed/gaps` (moved to W2 so dogfood in W3 has routing + readiness — hawk A6) | C1 | medium / YELLOW | contract check; kb_ready fixture pair; unready route holds; seed round-trip; ten QA angles doc-sync; seat handoff primed | W2 |
| 11 | C8 review: checker + verdict + canary cadence + bounded fixer loop + pre-flight + statistical shadow rule | C6, C7a, C9, C3 | large / RED | evidence-less PASS → UNKNOWN; canary miss disables; cross-family asserted; 0/5 stays OFF | W3 |
| 12 | C12 cost: usage · headroom chain (Codex exact · Claude port) · stop rules · prediction ledger | C3 | medium / YELLOW | p80 after 10 samples; stop thresholds; stale headroom = hold + notify | W3 |
| 13 | C10 ship: MERGE QUEUE + conflict fixer + profiles(booleans) + `stop-all` + revert + notify + handoff + governor + control room | C2, C6, C8 | large / RED | stale-base rebased + re-gated; conflict → fixer; GREEN ships human-free; RED waits; profile matrix | W3 |
| 14 | C3b real adapter: `claude_code_cli` (+ capability suite, live conformance smoke) | C3, C4 | medium / YELLOW | contract tests vs recorded CLI fixtures; hooks installed; capability suite green | W4 |
| 15 | C13 observe store v1: hash-chained trajectories · evaluator manifest · `active.json` + promote/rollback | C6, C12 | large / RED (evaluator) | content-addressed; tamper → FAIL; promote/rollback atomic + failure injection; boundary denied | W4 |
| 16 | C14 metrics registry (five seeds) + `sode metrics` + alerts | C13 | medium / YELLOW | registry gate incl. field binding + compute coverage; fixture metric matches; alert opens item | W4 |
| 17 | C11 `measure` stage (baseline in verify · after via `sode-run`) | C10, C14 | small / GREEN | three verdicts; excessive → follow-up item; unreadable = `unmeasured` | W4 |
| 18 | C15 automations (crawl set + `sode drift` weekly sweep + measure-queue drain) | C2, C7, C9, C10, C11, C13, C14 | medium / YELLOW | idempotent on re-delivery; `restricted` refuses host scheduler; drift sweep catches a planted stale KB entry | W4 |
| 19 | WALK milestone: `tests/test_standalone.py` + dogfood one real factory_ops item through sode | all | — | §1.4 all four criteria green; one item shipped BY sode with a complete record | W5 |
| 20 | C3c second adapter `codex_cli` (proves the abstraction on real work) | C3b, WALK | medium / YELLOW | contract + capability suite; a mock→Codex switch does not regress the eval skeleton | W5 |
| 21 | C13b observe v1.1: scorers · `sode replay` · `sode distill` | C13, WALK | medium / YELLOW | replay reproduces a recorded item; scorer judge cross-family; distilled entry carries evidence refs | W6 |

Wave = a sequential batch of makers working the MAIN sode tree (sequential makers → main tree; concurrent →
separate clones). W1 + W2 are dispatched from THIS repo (`sode_bootstrap.py` + briefs from the §4 stubs); W3+ are
sode work items (dogfood).

## 2. LATER (not v1; each is a backlog seed, §3)
container runner · beads (or other) item store · decision-model adapter (Sage/Jev class) · Evolve proposer
(§7.5) · Slack notify/intake · the `data` department (frontend is v1) · external target repos · GitHub issue/PR two-way
mirror beyond PR body · the PRODUCT plane (paper engine: card schema · risk kernel · re-validation · maintenance).

## 3. Bootstrap-backlog seeds (a sode-scoped backlog; created by `sode init`, one item each; STABLE ids — hawk 5.12)

| id | seed |
|---|---|
| B001 | Third-party tooling review: beads (pre-flight + pilot) and alternatives — DEFERRED until after W3; sode builds its native store regardless (review A11). Also carried in this repo's backlog as `sode-third-party-tooling-review-beads`. |
| B002 | Decision-model pre-flight (Sage / Jev): security + ZDR + no-external-API approval. |
| B003 | Decision-model use-sites, one item each, each stating WHERE it plugs in, HOW it is shadow-tested (agreement · latency · cost vs the current path) and its value add: triage proposals · review-depth routing · 100% scorer coverage · auto-ship confidence input · money/auth/secrets diff pre-flag (§6.7). |
| B004 | Metric-group discussions, one per group (§9.6): precise definitions · drivers · measures · baselines · alert rules → registry entries. |
| B005 | Product-plane design session (§10 of the architecture): card schema · risk kernel · re-validation · maintenance layer. |
| B006 | Container runner backend (when external targets or guard-floor evidence demand it). |
| B007 | interlinked-cli rule-catalogue comparison vs C4 rules (reference-only). |
| B008 | Security department KB seeding session (patterns · CVE classes · tooling picks, pinned). |
| B009 | Gate signal-to-noise audit cadence (per-check catch/FP review) — factory_ops recurring. |
| B010 | Experience-bank distillation cadence + first distillation after W5. |
| B011 | Evolve unlock criteria check (≥50 trajectories/stage + hidden holdout) — factory_ops recurring. |
| B012 | Claude headroom port: transcript-usage parser + era-scoped rate model + UI% calibration (`sode headroom calibrate`); Codex exact-read parser pinned to a rollout fixture (review B10). |
| B013 | Clone GC policy + `sode archive-run` / `import-run` portable evidence bundles (review B19). |
| B014 | Gate-outcomes adjudication cadence (TP/FP labelling of every FAIL) — factory_ops recurring (review E8). |
| B015 | Weekly `sode drift` sweep review — factory_ops recurring (review E14). |
| B016 | Shadow-phase review: per class × department, when does YELLOW auto-ship flip — factory_ops recurring (review B11). |
| B017 | Formal state model of C2 (TLA+ or equivalent) once the invariant table stabilises (review D5). |
| B018 | KB SEEDING sessions, one per department (W1–W2, parallel with the code build): security · qa_quality · factory_ops from our own material; backend · frontend · devops from operator-brought articles + best practices; architecture from the decision-record template + design sources. Acceptance per session: `kb_ready` flips true (every checklist angle covered by a sourced entry + a conventions section). The WALK milestone requires factory_ops ready (sode's first real items are its own). |
| B019 | GAP-1 (apply-check): one clone per ITEM reused across stages vs a fresh clone per stage — decide at C3; advisor recommends one clone per item, fresh only on a PARTIAL continuation after a kill. |
| B020 | Apply-check closures GAP-2..GAP-7 (architecture Appendix B): plan-only read-only clone (C3) · T1 runs in the clone via `sode-run` after worker exit (C7a) · ship approval hash = (diff sha, record sha) (C6) · `.sode/measure_queue.jsonl` at ship (C11/C15) · null-safe rates on an empty ledger (spec of the first dogfood item) · triage stage body with a fixed output schema (C1/C15). |
| B021 | Tool eval: ponytail (minimal-code senior-dev agent) as a sode maker style / skill — baseline vs current maker on 2–3 real script tasks; correctness · tokens · review burden; security pre-flight before install (operator 2026-08-22). |
| B022 | Evolve reference: Meta-Harness / harness-evolver (7-stage evolve loop, isolated proposers, counterfactual trace diagnosis) as the design reference for §7.5 when it unlocks — reference-only, no install. |
| B023 | Semantic-escape design session: "what semantic error passes ALL gates?" — rule-of-five perspective-diverse review, explain-a-sample, surrogate verifier; RED; design-first with deterministic catch + alarm per mitigation. |
| B024 | Runner hardening eval: isolation ladder (container < gVisor < microVM < VM) vs OS syscall jail (Seatbelt/Landlock) for the `container` runner + egress-proxy credential injection — evaluate before the first external target. |
| B025 | Gap-closure cadence: `sode kb gaps` + worker confusions with no KB coverage → factory_ops items; first review after W5 — self-learning fills the `run_lesson` layer over time (operator 2026-09-18). |

## 4. Dispatch-brief STUBS (W1 + W2 — dispatched from this repo; W3+ rendered by sode's own C5)
Each stub fills the ported brief skeleton; load-bearing content is IN the brief; acceptance is executable.

### W1-1 — C0 skeleton
GOAL: create `../sode-factory/` as a NEW repo from `sode_factory_component_specs.md` §C0. READS: architecture
§1, §3.3, §9; specs C0. TOUCHES (sode): `factory.yaml`, `platform/schema/`, `platform/cli/`, `Makefile`,
`tests/test_standalone.py` (skeleton form), `README.md`. DO-NOT-TOUCH: anything in growth-hack-system except
`common_tools/scripts/sode_bootstrap.py` (+ its test). ACCEPTANCE: `make test` green in a temp HOME · `sode init
&& sode doctor` exit 0 in the `local` profile · `factory_unknown_stage_BAD.yaml` refused · `sode migrate --check`
round-trips a one-version-behind fixture · `platform/ports/` manifest gate · grep clean (§1.4.3). CONTEXT WITHHOLD:
none. BUDGET: hand estimate → prediction ledger row #1.

### W1-2 — C1 work store
GOAL: specs C1. READS: architecture §4 (all), §4A routing. TOUCHES: `platform/work/`, `platform/policy/
classes.yaml`, `routing.yaml`, `tests/`. ACCEPTANCE: §4.2/§4.3 tables byte-equal to the `classes.yaml` render · depth
= max(class, lane, overlay) incl. the large-GREEN fixture · `sode ready` excludes blocked AND lease-overlapping items ·
WIP limit · unowned path fails `sode lint` · impact_metric-less medium fails `sode lint`. WITHHOLD: growth-hack-system's
`backlog.yaml` (re-derive from the spec, do not copy fields).

### W1-3 — C4 guards (RED, security department)
GOAL: specs C4. READS: architecture §8; `docs/design/sode_factory_guard_rules_seed.yaml` (the 34 deny + 27 ask rules,
generated verbatim from this machine's live rules — pasted INTO the brief; the file is the paste) + `platform/policy/git.yaml` + `platform/policy/secrets.yaml` shapes. TOUCHES: `platform/guards/`,
`bin/sode-sh`, `bin/sode-run`, `platform/policy/git.yaml`, `platform/policy/secrets.yaml`, `tests/`. ACCEPTANCE:
known-bad corpus all denied · known-good allowed · worker push to main or to a remote outside `git.yaml` denied ·
`test_deny_rules_never_shrink` · ask-rule removal without a cited item fails · `sode-run` cwd-fence + secret-grant
fixtures · evaluator-boundary write denied · `sode verify-log` detects a tampered record · rule provenance fields
present on every rule. WITHHOLD: none. NOTE: writing
destructive-command patterns into files trips this repo's own guard on literal strings — the maker writes the
rule corpus as data (YAML) through the editor tool, not as executable text in a shell heredoc.

### W1-4 — C3 worker runtime (mock adapter only)
GOAL: specs C3 minus real adapters. READS: architecture §3.2, §3.5. TOUCHES: `platform/workers/`,
`platform/adapters/mock.py`, `platform/workers/watchdog.py`, `tests/`. ACCEPTANCE: clone isolation · AST env-scrub ·
mock end-to-end · empty `secrets` → no token env · POSITIVE-secret fixture appears nowhere under git or `.sode/` ·
watchdog kills + classifies + quarantines a stalled mock worker · `error_class: cli_drift` → DEGRADED · per-target
`setup` runs through `sode-run`. WITHHOLD: this repo's `orchestrator` skill text (re-derive the lifecycle from §3.5).

### W2-1 — C5 brief renderer + `sode lint` + spec-lock brief + report-back
GOAL: specs C5. READS: architecture §4.6, §4.8, §5.2, §9.4. TOUCHES: `platform/brief/`, `platform/lint/`, `tests/`.
ACCEPTANCE: determinism · size budget · provider-neutral · seven-part spec-lock refusal · spec-hash re-lock ·
poisoned-acceptance fixtures FAIL / corrected PASS · idempotent phases (a re-render on a partial does not double-emit).
WITHHOLD: this repo's brief skeleton TEXT (the maker re-derives the sections from §4.6; the skeleton's RULES are
restated inside this brief).

### W2-2 — C7a gate core
GOAL: specs C7a. READS: architecture §6.3. TOUCHES: `platform/gate/`, `tests/`. ACCEPTANCE: remediation on every check
· a BAD fixture per check · cache 0-re-runs · 0-checks-run = FAIL · anti-gaming fixtures (deleted test · skip marker ·
edited acceptance cmd) FAIL T0 · every check runs via `sode-run` · T1 wall time under budget. WITHHOLD: none.

### W2-3 — C2 lifecycle engine (RED)
GOAL: specs C2. READS: architecture §2 (all incl. §2.6), §3.5. TOUCHES: `platform/engine/`, `platform/ledger/`,
`platform/clock.py`, `tests/`. ACCEPTANCE: transition table + invariant table · double-fire · duplicate `action_id`
cannot double-advance · corrupt ledger FATAL · PARTIAL continuation · attempts cap → HALTED + notify · child HALT →
parent replan. WITHHOLD: `supervisor.py` SOURCE (the maker re-derives from the spec; the port-conformance manifest
names the invariants to keep).

### W2-4 — C6 context record
GOAL: specs C6. READS: architecture §5 (all). TOUCHES: `platform/record/`, `platform/policy/actors.yaml`, `tests/`.
ACCEPTANCE: golden projection from `events.jsonl` + artifacts · no report-back → PARTIAL · two completeness gates ·
hash-bound approve from trusted actor = decision, from untrusted = note, hash mismatch = INVALIDATED · redaction before
write (positive-secret fixture). WITHHOLD: none.

## 5. Standalone-clone acceptance — stated explicitly
The build is DONE for v1 when, on a machine with no growth-hack-system present: `git clone <sode>` → `make test`
GREEN → `sode init --profile local --provider mock` → one small item shipped end to end by `sode tick` (through the
merge queue) → its `record.yaml` passes `record_complete_for_ship` → `sode metrics` renders → the tree greps clean of any growth-hack-system path, id
namespace, client name or credential. Every ported asset has its own tests inside sode. This is
`tests/test_standalone.py` and it runs in sode's CI on every PR.

## 6. Cost envelope (RECORDED predictions, not promises — §9.3)
Per component: a hand-estimated cap goes into the prediction ledger at dispatch; actuals fill in at completion;
the W2+ caps for a class × department × stage cell switch to the empirical p80 once 10 samples exist. No
component starts without its row.
