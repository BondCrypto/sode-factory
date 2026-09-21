# sode-factory — build sessions (the split into fresh build sessions)

**Status:** LOCKED with the build plan (operator 2026-09-21). This is the operator's answer to "how many fresh
sessions does a fully functional v1 take, and what does each one get?". It consumes `sode_factory_build_plan.md`
§1 (the 21 dependency-ordered rows) and `sode_factory_component_specs.md` (C0–C15). Every session below is ONE fresh
agent session started from a paste-first brief; it ends with its acceptance green, the standalone test still green,
and a session record (END_OF_RUN shape). No session re-decides architecture — a maker that needs to is a defect.

## 0. How to read the spec set (the order an agent reads it)
1. `sode_factory_architecture.md` — the locked decisions (§1–§9, §4A, §2.7 transition contract, §1.6 taxonomy).
2. `sode_factory_component_specs.md` — the 16 build-ready component contracts.
3. `sode_factory_build_plan.md` — dependency order · waves · brief stubs · backlog seeds B001–B025.
4. THIS doc — the session split. 5. `sode_factory_guard_rules_seed.yaml` — the rule catalogue for S3.
6. `docs/audits/sode_factory_spec_review_2026-09-18.md` — why things are the way they are (dispositions).

## 1. Session model
- **One session = one component (or one tightly coupled pair)**, one fresh context, one brief, one acceptance set.
  RED components get a session of their own and the full process-genesis kit; others may pair.
- **Entry state** = the repo at the previous session's tag. **Exit** = component acceptance green (from its spec) ·
  `make test` green · `tests/test_standalone.py` green (skeleton form until S9) · a session record committed · a tag.
- **Handoff artifact** between sessions = the tag + the session record (what landed · what did not · open questions).
  Nothing is handed off in chat.
- **Cost**: every session opens a prediction-ledger row with a hand cap at dispatch (§9.3); actuals fill at exit.
  No numbers are promised in this doc — the ledger calibrates them.
- **Who dispatches**: S1–S9 and K1–K7 are dispatched from growth-hack-system (its `/dispatch-brief` skill against the
  §4 stubs of the build plan). From S10 on, sode dispatches its own sessions (dogfood).
- **Parallelism**: KB seeding sessions (K1–K7) run in parallel with code sessions from S1 on; they touch only
  `platform/departments/*/kb/`. Code sessions are SEQUENTIAL on the main tree (no concurrent git-touching makers
  without separate clones).

## 2. The sessions

### Phase A — ground (dispatched from growth-hack-system; W1)
| # | Session | Builds | Lane | Exit acceptance (headline) | Depends on |
|---|---|---|---|---|---|
| S0 | repo init | repo · README · spec set · backlog.yaml · .gitignore (DONE 2026-09-21) | — | remote pushed | — |
| S1 | skeleton | C0: layout · `factory.yaml` schema · CLI registry · `sode init/doctor/version/migrate` · `.sode/local.yaml` · minimal `active.json` · `platform/ports/` manifests · standalone test (skeleton form) | YELLOW | `make test` green in a temp HOME · `doctor` 0 in `local` profile · BAD schema fixture refused · `migrate --check` round-trip | S0 |
| S2 | work store | C1: item schema · `classes.yaml` (generated tables) · routing · labels-as-holds · scheduler · leases on disk · `sode new/intake/ready/hold/release/dep/lint` · triage output schema | YELLOW | tables byte-equal to render · depth fixtures incl. medium-D1/D2 · lease + WIP fixtures · triage schema fixture | S1 |
| S3 | guards (RED) | C4: `sode-sh` · `sode-run --actor` · rules from the seed catalogue with provenance · `git.yaml` · `secrets.yaml` · hook installers · hash-chained shim log · `verify-log` · evaluator-boundary denies · path rules | RED | known-bad corpus all denied · known-good allowed · monotone deny test · bypass-proof matrix (mock) · `verify-log` tamper test | S1 |
| S4 | worker runtime | C3: provisioner (fresh clone per stage · read-only plan clone · `branch_ref`/`dispatch_ref`) · watchdog · mock adapter · adapter registry + capability suite · secrets injection · redaction · services supervisor · disk watermark · quarantine | YELLOW | clone isolation · env-scrub AST · mock end-to-end · positive-secret redaction · watchdog kill/quarantine · DEGRADED on cli_drift | S1, S3 |

### Phase B — the loop closes (dispatched from growth-hack-system; W2)
| # | Session | Builds | Lane | Exit acceptance (headline) | Depends on |
|---|---|---|---|---|---|
| S5 | brief | C5: renderer (stable prefix · recitation · empty-KB marker) · ONE `sode lint` · spec-lock brief · report-back schema · spec-hash pin | YELLOW | determinism · size budget · provider-neutral · seven-part refusal · re-lock on spec change · poisoned fixtures fail | S2 |
| S6 | gate core | C7a: registry · cache · T0/T1 · toolchain checks · anti-gaming checks · `sode-run` execution · determinism guard · escape-log four-part record · gate-outcomes ledger | YELLOW | remediation on every check · BAD fixture per check · 0-checks = FAIL · anti-gaming fixtures fail T0 · `--repeat 10 --frozen` identical | S1, S2, S3 |
| S7 | engine (RED) | C2: state machine + invariant table · leased ledger · actions ledger · effects outbox · classify (trailers · clean tree · acceptance hash) · review fan-out barrier · replan edge · clock · `sode tick [--until]/status` | RED | transition + invariant tables · double-fire · duplicate action_id · corrupt=FATAL · PARTIAL continuation · child HALT → replan · commit-count trap fixture | S2, S4, S5 |
| S8 | record | C6: events.jsonl → projection · redaction before write · two completeness gates · hash-bound decisions + actors · `ship_hash` · narrative · PR view (mock GitHub) | YELLOW | golden projection · no report-back → PARTIAL · untrusted approve = note · hash invalidation · for_ship vs after_measure | S7, S5 |
| S9 | departments | C9: loader · seven contract dirs · KB entry schema · `kb_ready` gate · `sode kb seed/gaps` · seats + handoff notes · freshness | YELLOW | contract check · kb_ready fixture pair · unready route holds · seed round-trip · ten QA angles doc-sync | S2 |

### Phase K — knowledge (parallel with A/B; operator brings sources for K4–K6)
| # | Session | Seeds | Exit |
|---|---|---|---|
| K1 | security KB | our guard rules · pre-flight discipline · CVE-class patterns · tooling picks (pinned) | `kb_ready(security)` true |
| K2 | qa_quality KB | the ten angles · lean bar · anti-gaming rules · refactor patterns | `kb_ready(qa_quality)` true |
| K3 | factory_ops KB | two-currencies · cache discipline · harness lessons · metrics definitions | `kb_ready(factory_ops)` true — REQUIRED before S10 |
| K4 | backend KB | operator-brought articles + best practices, distilled with citations | `kb_ready(backend)` true |
| K5 | frontend KB | operator-brought articles + best practices | `kb_ready(frontend)` true |
| K6 | devops KB | operator-brought articles + best practices (CI/CD · envs · runtime hosts) | `kb_ready(devops)` true |
| K7 | architecture KB | decision-record template · design sources · the elegance bar | `kb_ready(architecture)` true |

### Phase C — dogfood (sode dispatches its own sessions; W3)
| # | Session | Builds | Lane | Exit acceptance (headline) | Depends on |
|---|---|---|---|---|---|
| S10 | gate item-aware | C7b: brief lint · acceptance script · record completeness · port manifests as checks | GREEN | BAD fixture per check | S5, S6, S8 |
| S11 | review (RED) | C8: checker prompt + verdict script · canary corpus + cadence · fixer loop (bounded, finding ids) · cumulative pre-flight · shadow ledger + statistical switch · fan-out completeness | RED | evidence-less PASS → UNKNOWN · canary miss disables · cross-family · 0/5 OFF · dead leg → UNKNOWN | S8, S6, S9, S4 |
| S12 | cost | C12: usage readers · headroom chain (Codex exact · Claude port · calibrate) · stop rules · prediction ledger | YELLOW | p80 after 10 · HALT/KILL thresholds · stale headroom = hold + notify | S4 |
| S13 | ship (RED) | C10: merge queue · conflict fixer · profiles (booleans) · `stop-all` · revert · notify · handoff/resume · governor · control room (`ps/status --live/tail`) | RED | stale-base rebased + re-gated · conflict → fixer · GREEN human-free · RED waits · profile matrix | S7, S8, S11 |

### Phase D — adapters, observe, measure, metrics, automations (W4)
| # | Session | Builds | Lane | Exit acceptance (headline) | Depends on |
|---|---|---|---|---|---|
| S14 | Claude adapter | C3b: `claude_code_cli` + capability suite + live conformance smoke (manual) | YELLOW | recorded-transcript contract tests · hooks installed · capabilities green | S4, S3 |
| S15 | observe v1 (RED) | C13: hash-chained trajectories · evaluator manifest · `active.json` + promote/rollback + failure injection · `harness-card` · eval skeleton | RED | content-addressed · tamper → FAIL · atomic promote/rollback · boundary denied · card determinism | S8, S12 |
| S16 | metrics | C14: registry (five seeds) · field-binding + compute gates · `sode metrics` · history · alerts | YELLOW | registry gate · fixture metric matches · alert opens item | S15 |
| S17 | measure | C11: baseline in verify · `measure_queue` · after-read via `sode-run` · verdicts | GREEN | three verdicts · excessive → follow-up · unmeasured alert | S13, S16 |
| S18 | automations | C15: trigger runner · crawl set · measure-queue drain · weekly `sode drift` sweep (coverage grid · staleness · determinism) | YELLOW | idempotent re-delivery · `restricted` refuses host scheduler · planted stale entry caught | S7, S10, S13, S15, S16, S17 |

### Phase E — the WALK milestone and after (W5–W6)
| # | Session | Builds | Exit |
|---|---|---|---|
| S19 | WALK | `tests/test_standalone.py` full form + ONE real factory_ops item shipped BY sode end to end with a complete record | §1.4 all four criteria green — **v1 is FUNCTIONAL here** |
| S20 | Codex adapter | C3c: `codex_cli` + capability suite; a mock→Codex switch does not regress the eval skeleton | proves the model-agnostic abstraction on real work |
| S21 | observe v1.1 | C13b: scorers (cross-family judge) · `sode replay` · `sode distill` | replay reproduces a recorded item; distilled entry carries evidence refs |

## 3. Counts
- **Functional v1** (S1–S19): **19 code sessions** + **7 KB sessions** (K1–K7, parallel). Six of the code sessions
  are RED (S3 · S7 · S11 · S13 · S15 and S19's dogfood ship path). After S19 a fresh clone of sode is independently
  valuable (§1.4). S20–S21 complete the model-agnostic proof and the learning tooling.
- **Merge candidates if sessions run short**: S5+S8 (brief + record) · S16+S17 (metrics + measure). Never merge a RED
  session with anything.
- Product-plane sessions (paper engine) are NOT counted here; they start after B005 and a `paper_validated_card`.

## 4. Per-session brief contract (what every session brief carries; rendered from the build plan §4 stub + this table)
GOAL (the component) · READS (the exact spec sections) · ENTRY STATE (tag) · TOUCHES · DO-NOT-TOUCH (every other
package; the trio of spec docs is read-only for makers) · ACCEPTANCE (executable, from the component spec) ·
CONTEXT WITHHOLD · BUDGET (prediction-ledger row) · EXIT (gate green · standalone green · session record · tag) ·
REPORT-BACK (did · did_not · decisions · concerns · assumptions · rejected_paths · suggested_followups · confusions ·
tool_failures) · RECITATION.
