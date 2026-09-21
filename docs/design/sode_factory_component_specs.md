# sode-factory — component specs (build-ready)

**Status:** LOCKED (agenda 10, operator 2026-09-18) — amended per `docs/audits/sode_factory_spec_review_2026-09-18.md`
(operator-adopted dispositions; `review Xn` tags below point at that doc). Companion to `sode_factory_architecture.md` (the locked
architecture; section refs below point there) and `sode_factory_build_plan.md` (order · v1/later · brief stubs).
Each component: RESPONSIBILITY · INTERFACE/CONTRACT · ACCEPTANCE TEST · FAILURE MODES. A component a maker could
not build from its section is not done. Language: Python 3.12 (stdlib-first; pinned deps via `sfw`); CLI = `sode`.
Repo-internal paths below are SODE paths. Nothing here imports growth-hack-system; "PORT of X" = copy + adapt +
test inside sode.

---

## C0 — Skeleton + `factory.yaml` schema + `sode` CLI + mock-run harness
**Responsibility.** The clonable root: `platform/` · `products/` · `work/` · `metrics/` · `evals/` · `.sode/`
(gitignored runtime) · `factory.yaml` · `sode` entry point · one-command gate `make test`.
**Interface.** `sode init [--profile local|standard|restricted] [--provider mock|anthropic_cli|openai_cli]` (writes
`factory.yaml` from the schema; DEFAULT `--profile local --provider mock` so a fresh clone works offline — review A12;
SEVEN v1 departments as contract-satisfying stub dirs; a minimal `.sode/active.json` pointer at the init sha) · `sode doctor` (validates every artifact against `platform/schema/*.schema.json`; checks git
≥2.40; profile-GATED checks: `op` present only if broker=1password, GitHub reachability + branch protection only in
`standard`; adapter `cli_version` pinned AND installed; model ids present in the provider capability matrix;
`active.json` sha exists) · `sode migrate --check|--apply` (review B8: every artifact — factory.yaml · item · events ·
record · trajectory · prediction · metrics history · gate JSON — carries `schema_version`; migrators live in
`platform/schema/migrations/`) · `sode version` · `platform/ports/<asset>.yaml` port-conformance manifests (review E2) ·
`.sode/local.yaml` — MACHINE-LOCAL config split from the versioned `factory.yaml` (hawk B5: provider CLI paths ·
installed `cli_version`s · UI-headroom samples · broker state · `provider.privacy_mode` + `operator_attested_on` —
`standard` WARNS when a provider's privacy/ZDR mode is unknown, hawk B8); `factory.yaml` names capabilities, `local.yaml`
binds them. **CLI REGISTRY** (one table, the authority for every verb — hawk B10): `platform/cli/registry.yaml`
`{verb, owner_component, stability, profiles, reads, writes}`; documented verbs = `init · doctor · version · migrate ·
new [--child] · intake · ready · hold · release · dep · lint · tick [--item|--max|--until <stage>] · status [--live
--json] · ps · tail · stop-all · brief · record · gate [--t0|--t1|--repeat --frozen] · ratchet · kb seed|gaps · ship ·
revert · handoff · resume · measure · metrics · headroom · automations · drift · harness-card · promote · rollback ·
gc --dry-run|--apply`; `sode-sh` and `sode-run` are SEPARATE binaries (workers call them directly). A verb not in the
registry fails the gate. **Package layout** (hawk §6, adopted): `platform/{cli,core,schema,config,policy,work,engine,
workers,guards,brief,record,gate,review,ship,measure,observe,departments,metrics,automations}/` — one component per
package, `core/` = ids · clock · fs_atomic · subprocess · jsonl. **On-disk runtime layout**: `.sode/{run/<id>/state.json,
actions.jsonl, effects.jsonl, leases/, clones/<id>/ + clones/quarantine/, trajectories/, active.json, predictions.jsonl,
gate_outcomes.jsonl, shadow.jsonl, measure_queue.jsonl, metrics/, logs/shim.jsonl, local.yaml}`; `work/<id>/{item.yaml,
spec.md, decision.md, events.jsonl, record.yaml, briefs/<stage>-<attempt>.md, artifacts/<stage>/<attempt>/manifest.yaml}`.
**Acceptance.** Fresh clone, no network: `make test` GREEN; `sode init && sode doctor` exit 0 (local profile); schema
rejects a factory.yaml with an unknown stage key (fixture `factory_unknown_stage_BAD.yaml`); `sode migrate --check` on
an artifact one version behind reports the pending migration and `--apply` round-trips; a ported asset without its
`platform/ports/` manifest fails the gate; repo grep clean per §1.4(3).
**Failure modes.** Schema drift vs docs (gate `check_factory_schema_doc_sync`); a hidden dependency on a
machine-local path (caught by the standalone test running in a temp HOME).

## C1 — Work store + class table + scheduler
**Responsibility.** `work/<id>/item.yaml` (§4.1 schema, `schema_version`, `spec_hash`, `acceptance_hash`, `stack`),
`platform/policy/classes.yaml` — the SINGLE generated authority for class × lane × overlay → stages · depth (max
rule) · human locks (review E1; §4.2/§4.3/§6.2 tables are GENERATED from it), `platform/policy/routing.yaml`
(touches-glob × class → primary department + consulted; unowned path = FAIL; overlap precedence — review E10),
labels = HOLDS only incl. `cancelled` (§4.4), deterministic scheduling policy: priority → age, WIP limit per
department, concurrency cap per lane, headroom as global cap, PATH LEASES from `touches` (§4.5, review B16/B18),
stacks for children (review B12).
**Interface.** `sode new "<title>" --class small --lane GREEN [--outcome ... --parent ...]` → `work/<id>/` ·
`sode ready` → items whose `depends_on` are all done, `label == null`, and whose path leases do not overlap a running
item; ordered by priority then age · `sode hold <id> needs-info|blocked|parked|cancelled` / `sode release <id>` ·
`sode dep add <child> <parent>` · `sode lint <id>` (the ONE lint: item shape + acceptance lint + impact_metric rule —
review C9) · library `policy.required_stages(item)`, `policy.security_depth(item)` (= max(class, lane, overlay)),
`policy.route(item) -> (primary, consulted[])`, `scheduler.pick(ready, wip, leases) -> item|None` · `sode intake
<source>` (GAP-7/hawk A15: any intake — CLI · issue · PR comment · monitor signal — runs the TRIAGE stage body, a
small mockable worker call with the fixed output schema `{class, lane, department, depth, touches[], one_question|null,
confidence, evidence[]}`; human-ratified until a decision model is approved) · durable PATH LEASES on disk (hawk B4):
`.sode/leases/<lease_id>.json` `{item, action_id, resources[], acquired_at, heartbeat, released_at}`; stale-lease
recovery is engine-owned and logged.
**Acceptance.** The §4.2/§4.3 doc tables are byte-equal to the render of `classes.yaml` (generated, review E1);
`security_depth(large, GREEN)` == D3 (max rule; fixture for review A3); `security-sensitive` raises one grade;
`irreversible` forces RED; `sode ready` excludes an item with an open dependency AND an item whose lease overlaps a
running one (fixtures); WIP limit respected (fixture); an unowned `touches` path fails `sode lint`; an
`impact_metric`-less medium item fails `sode lint`; a `depends_on` cycle is refused; `security_depth(medium, GREEN,
non-sensitive) == D1` and `security_depth(medium, GREEN, touches secrets) == D2` (hawk A1 fixtures); a triage fixture
input → the exact output schema; a stale lease (no heartbeat past TTL) is recovered and the event logged.
**Failure modes.** Class table edited in code but not doc (sync test); a cycle in `depends_on` (detected, refused).

## C2 — Lifecycle engine (state machine + leased ledger + classify)
**Responsibility.** §2: one tick = ONE transition computed from disk; deterministic transitions performed
in-process; model-needing transitions emitted as pending-actions. PORT of `supervisor.py` shape + `dispatch_ledger`
(atomic temp+fsync+rename, `fcntl` lease, corrupt = FATAL) + `classify_dispatch_state` (COMPLETE/PARTIAL/EMPTY) with the
HARDENED oracle: clean tree required · acceptance REQUIRED and pinned by `acceptance_hash` · phase identity from commit
TRAILERS (`Sode-Item` · `Sode-Phase` · `Sode-Attempt` · `Sode-Acceptance-Hash`) — NEVER a commit count.
**Interface.** `sode tick [--item <id>] [--max <n>] [--until <stage>]` · `sode status [<id>] [--live --json]` (read-only) · runstate at
`.sode/run/<item>/state.json`; events appended to `work/<id>/events.jsonl` (the SOURCE; `record.yaml` projects it —
review B15); `engine.next_transition(state) -> Transition | PendingAction`; every PendingAction carries a
deterministic `action_id = h(item, stage, attempt)` and is CLAIMED in `.sode/actions.jsonl` `{action_id, claimed_by,
pid, spawned_at, result_ref}` BEFORE any side effect — a re-tick that finds a claimed, unresolved action re-emits the
SAME id and never spawns twice (review B2); `acceptance_hash` + run/phase ids pinned at dispatch (review E3); the
REPLAN edge (§2.6); one clock library: UTC timestamps, monotonic durations, reboot-safe (review B20) · **EFFECTS
OUTBOX** `.sode/effects.jsonl` (hawk B1): every EXTERNAL side effect (push · PR upsert · merge · notify · automation
trigger · metric alert) is an effect row `{effect_id, action_id, kind, target, idempotency_key, status, attempts,
result_ref}` written BEFORE execution and resolved after — exactly-once by idempotency key; the actions ledger covers
spawns, the effects outbox covers everything else · the REVIEW FAN-OUT BARRIER (§2.1): `review` launches legs and
collects `artifacts/review/<attempt>/{gate,qa,security,baseline}.json`; `verify` aggregates deterministically · stage
enum incl. `done|halted|cancelled` (§4.1); `halted` is released only by a human `sode release` · `sode tick --until
<stage>` loops ticks until the item reaches the stage or holds.
**Acceptance.** Table test over every (stage, classify-result) pair reaching exactly one next state per §2.1/§3.5
PLUS the invariant table (review D5): no double spawn · no skipped review · no ship without a captured baseline · no
terminal item with an open child · no ship on a stale base (see C10) · corrupt ledger never read as empty;
double-fire test: two concurrent ticks → one lease holder, the other exits 3; a duplicated worker completion for the
same `action_id` cannot double-advance (fixture); PARTIAL → continuation with RESUME preamble; attempts > max →
HALTED + notification; a child HALT fires the parent's replan edge (fixture); a clone with the right number of
commits but a dirty tree or missing trailers classifies PARTIAL, never COMPLETE (fixture — the commit-count trap).
**Failure modes.** Wall-clock lease expiry (use monotonic); a transition firing on missing disk state (each
transition asserts its inputs exist).

## C3 — Worker runtime (provisioner · adapter interface · adapters · secrets)
**Responsibility.** §3.5 lifecycle: local clone (hardlinks) at `base_ref`, scrubbed git env (PORT `git_env`),
per-target PROVISIONING manifest (`setup` · `test_cmd` · `cache` namespaced outside the clone · `services` ·
`healthcheck` · `clean` — review B7), item branch `sode/<id>` under `platform/policy/git.yaml` (review B6), guard
install (via C4), `op run` secret injection scoped to `stage.secrets` from the SECRETS REGISTRY
(`platform/policy/secrets.yaml`: id · allowed stages · redaction pattern; broker unavailable = hold — review B5),
run under the WATCHDOG (port of `dispatch_watchdog`: heartbeat = transcript mtime + commit count · no-output timeout ·
wall-clock cap · process-group kill · classify-on-timeout · clone quarantine — review B3), typed adapter ERRORS
(auth · rate-limited · outage · CLI drift · permission prompt → hold with backoff; CLI drift → adapter DEGRADED, no
auto-ship — review B21), context-limit rule (handoff note + PARTIAL, never compact — review B22), usage read,
REDACTION before any transcript/usage write (review B5); a FRESH clone per STAGE at `branch_ref` (read-only clone for
`plan_only` stages; `dispatch_ref` recorded; GAP-1/GAP-2 decided §3.5), normal teardown when the action resolves,
QUARANTINE of watchdog-killed clones (policy GC / archive = backlog B013, NOT v1 — hawk 5.5); TARGET SERVICE
supervisor (hawk B6: `targets.<t>.services[]` = start · healthcheck · logs · port allocation · teardown · timeout ·
failure_class; T1 runs only after health passes); disk WATERMARK check in `doctor` + before provisioning (refuse a new
clone below the free-space floor);
workers write commit TRAILERS (item · phase · attempt · acceptance hash) via the clone's commit-msg hook; a failed run
carries `failure_class`; `rejected_paths[]` from a failed/PARTIAL attempt are fed into the continuation brief.
**Interface.** `Adapter.run(brief_path, clone_path, stage_cfg, action_id) -> WorkerResult{exit, error_class|None,
commits[], artifacts[], usage{input,output,cache_read,cache_write}, transcript_ref (REDACTED), report_back:
dict|None}` · `Adapter.capabilities() -> {edit, shell_via_shim, interrupt, install_hook, report_usage, resume}` (the
capability suite, review D4; a failed capability = DEGRADED) · adapter REGISTRY entry per provider: `cli_version`
pin · permission mapping · usage-field contract · transcript-fixture version (review E7) · adapters: `mock` (scripted
results from a fixture; no network) · `claude_code_cli` (headless run; installs hooks) · `codex_cli` (headless run;
installs config; LATER wave — review C6) · `Provisioner.create(target, base_ref, item) -> clone_path` (runs
`target.setup` through `sode-run`), `.destroy(clone_path)`, `.gc(policy)` · `Watchdog.watch(action_id, pid, clone)`.
**Acceptance.** AST test: every git spawn in `platform/` passes the scrubbed env; a clone's `.git` is separate
(config write in clone does not touch the target); `mock` adapter drives one item end to end under `make test`;
each real adapter has a contract test against a recorded CLI transcript fixture (no live model in CI) PLUS a manual
live conformance smoke gated by `cli_version` (review B12-Codex); `stage.secrets: []` → the worker env contains no
`OP_*`/token vars; POSITIVE-secret test: a fixture secret injected for a stage appears NOWHERE under git or `.sode/`
after the run (transcript · usage · record · shim log — review B5/F4); watchdog: a mock worker that stops writing for
> `no_output_s` is killed by process group, classified, its clone quarantined (fixture); an `error_class: cli_drift`
result flips the adapter to DEGRADED and `autonomy.yellow_auto_ship` returns False for its stages; a worker push to any
remote not in `git.yaml` is refused.
**Failure modes.** Vendor CLI flag drift (adapter contract tests pinned to a CLI version in `factory.yaml
providers.<p>.cli_version`); hardlink clone on a cross-device path (fallback to copy, logged).

## C4 — Guards: `sode-sh` shim + rule sets + hook installers
**Responsibility.** §8.1–8.2: L1 deny (PORT `destructive_guard` + the 34 deny rules + worker denies + the EVALUATOR
BOUNDARY: non-architecture writes under `evals/`, `platform/gate/registry*`, rubrics, holdout — review F3) and L2
ask (27 ask rules with the three edits) applied BEFORE exec on any provider; every rule carries `id · source_ref ·
threat_class · example` (review E5); an ASK-rule removal must cite an item id with holds evidence (the ask-prune
ledger, gate-checked); HASH-CHAINED append-only shim log + `sode verify-log` (review F7); adapter hook installers as a
second layer; ASK → `needs-info` hold when unattended; **`sode-run`** — the policy runner for every deterministic
command the ENGINE executes (gate checks · acceptance `cmd` · `impact_metric.read_cmd` · setup hooks): env scrub ·
cwd fence · timeout · output cap · the same deny floor · no secrets by default (review B4); shim PATH rules: a worker
writes only inside its clone and never to `work/<id>/record.yaml` or `events.jsonl` (engine-owned — review F9).
**Interface.** `sode-sh -c "<cmd>"` (the worker's shell; exit 126 + reason on deny; on ask: attended → prompt
name/what/command, unattended → write hold + exit 125) · `sode-run --actor engine|worker --stage <stage> --cwd <fence> --timeout <s> [--secrets <ids>]
-- <cmd>` (the engine's policy runner; the actor selects the rule view — hawk A10) · rules in `platform/guards/rules.yaml` (`deny[] / ask[]`, each `{id,
pattern, reason, source_ref, threat_class, example, applies_to: [worker|engine]}`; the SEED catalogue = this repo's
`docs/design/sode_factory_guard_rules_seed.yaml`, generated verbatim from the live 34 deny + 27 ask rules — hawk A7) · `guards.is_denied(cmd, cwd) -> reason|None`,
`guards.needs_ask(cmd)`, `guards.path_allowed(path, clone)` · `sode verify-log` · every rule/check/hook carries CAR ×
{guide|sensor} × {computational|inferential} tags for the enforcement coverage grid (`sode drift --coverage`).
**Acceptance.** Known-bad corpus (every documented variant: flag order, abs-path binary, `git -C` prefix,
`core.bare=true`, pipe-to-shell) → ALL denied; known-good corpus (lockfile sync, push to `sode/<id>`, read-only
git) → allowed; push to `main` from a worker → denied in both profiles; a rule removed from `deny[]` fails
`test_deny_rules_never_shrink` (ratchet: deny set is monotone); an ask-rule removal without a cited holds-evidence item
fails the gate; `sode-run` refuses an acceptance `cmd` that escapes its cwd fence or reads a secret not granted
(fixtures); a worker write to `work/<id>/record.yaml` or outside its clone → denied; a write under `evals/` from a
non-architecture item → denied; a tampered shim-log record breaks the hash chain (`sode verify-log` exit 1); the
GUARD-ENFORCEMENT PROOF MATRIX (review F1): per adapter, a transcript-level test proves raw shell and provider-native
tools cannot bypass the shim; deployed-hook drift vs `rules.yaml` is a doctor FAIL.
**Failure modes.** A worker bypassing the shim (adapter asserts the shell path; the hook layer denies a raw
`/bin/sh` spawn where the provider exposes tool calls); shell-grammar edge cases (honest-mistake threat model,
documented; container runner = the later stronger floor).

## C5 — Brief renderer + acceptance lint + spec-lock brief + report-back contract
**Responsibility.** §4.6/§4.8/§5.2: deterministic, provider-neutral `brief.md` from item + spec + stage config +
department KB slice (may be EMPTY in W2 — review A8; stable prefix FIRST, §9.4 — cache-hit is MEASURED, brief SIZE
budget is the acceptance target, review C7); PORT of `acceptance_lint` folded into the ONE `sode lint` (review C9);
`spec_lock_brief` (seven parts) renderer; `spec_hash` pinned at lock, any `spec.md` change → back to spec stage
(review B14); the report-back block schema (handoff payload: did · did_not · decisions[] · concerns[] · assumptions[]
· rejected_paths[] · suggested_followups[] · confusions[] · tool_failures[] — review D2); every brief PHASE is
idempotent (emission keys off does-X-already-exist) so a continuation never double-emits; stale-context warning when
a KB/checklist slice exceeds its `reviewed_on` threshold (review D6); a RECITATION block (task + acceptance ids) is the
LAST section of every brief; acceptance criteria carry `altitude` (machine|judge|human) and any `human` criterion
forces a spec lock; worker-facing CLI output contract (quiet on success · actionable error + remediation on failure).
**Interface.** `sode brief <id> <stage>` → `work/<id>/brief.md` · `render_brief(item, spec, stage_cfg, dept) ->
str` · `lint_acceptance(item) -> [findings]` · `render_spec_lock_brief(spec) -> str | refuse` ·
`REPORT_BACK_SCHEMA` (did · did_not · decisions[] · concerns[] · assumptions[] · rejected_paths[] ·
suggested_followups[] · confusions[] · tool_failures[] — the FULL handoff payload, hawk A18).
**Acceptance.** Same inputs → byte-identical brief (determinism); brief size within the department budget (test);
the first N bytes are identical across two items of the same department/stage (stable-prefix test — informative,
not blocking); a `spec.md` edit after lock changes `spec_hash` and `sode lint` demands re-lock (fixture); a brief containing a vendor-specific token
(`/hooks`, `AGENTS.md`-only syntax…) fails `test_brief_provider_neutral`; a spec missing any of the seven parts →
renderer refuses; the poisoned-acceptance fixtures FAIL lint, the corrected ones PASS.
**Failure modes.** KB bloat inflating every brief (size budget per department KB slice; gate warns >N tokens).

## C6 — Context record (projection · hooks · completeness gate · PR view)
**Responsibility.** §5: `record.yaml` = pure PROJECTION of `events.jsonl` + stage exit artifacts, rebuilt per
transition (review B15); stop-hook harvest of report-back + usage; REDACTION before every write (review B5); TWO
completeness gates — `record_complete_for_ship` and `record_complete_after_measure` (review A2); `standard`-profile PR
body upsert; human decisions ONLY as hash-bound commands from trusted actors (`/sode approve spec <hash>` · `approve
ship <hash>` · `reject` · `needs-info`; `platform/policy/actors.yaml`; a decision is invalidated when its artifact hash
changes — review B9); free-form comments harvested as notes.
**Interface.** `record.project(item, stage_artifacts) -> record` (pure) · `record.harvest(worker_result)` ·
`sode record <id>` (render) · `record_complete_for_ship(record, klass)` / `record_complete_after_measure(record)` ->
PASS|FAIL[missing] · `pr_view.upsert(id)`, `pr_view.harvest(id) -> (decisions[], notes[])` (GitHub adapter; mockable) ·
`decisions.parse(comment, actor) -> Decision|Note` (hash-bound command grammar) · `record.narrative(item) -> str`
(the literate summary generated at ship — background → intuition → change → proof — rendered into the PR body; the
artifact the 10% human audit reads) · `record.harness_card` = hash from C13.
**Acceptance.** Golden test: a fixture set of stage artifacts → the expected record (byte-exact); a worker result
without report-back → classify PARTIAL; medium item with no human decision → `check_record_complete` FAIL; PR
body rendered from record equals the golden markdown; `/sode approve spec <hash>` from a trusted actor lands in
`decisions[]` with `by: human` and the hash; the same text from an untrusted actor is a NOTE; an approval whose hash
no longer matches `spec_hash` is marked INVALIDATED (fixtures — review B9/F5); a record with a captured baseline but
no measure verdict passes `for_ship` and fails `after_measure` (review A2).
**Failure modes.** Record edited by hand (the projection overwrites; `events[]` preserved); GitHub API down
(upsert retries then queues; the record is still complete on disk).

## C7 — Gate (`sode gate --t0|--t1`) + ratchet tooling
**Responsibility.** §6.3: check registry with per-check remediation, T0 scoped to touched files (<60 s), T1 full
(<5 min, parallel), content-hash cache, exit 0/1/2, `--json`; every check executes through `sode-run` (review B4);
per-target gate config (`targets.<t>.gate`, review B7). Lands in TWO steps (review A9): **C7a** (W2, depends on C0 +
C4) = registry · cache · toolchain checks (tests · lint+format · types · complexity budget · secret scan · dep
pin+audit · license · factory schema · **anti-gaming**: no test deleted/weakened without a citing item · no new skip
markers · assertion count non-decreasing · acceptance `cmd`s untouched by the implementer · no stub where behaviour is
specified — operator 2026-09-18, code quality applies to ALL code); **C7b** (W3, depends on C5 + C6) = item-aware
checks (brief lint · acceptance script · record completeness · port-conformance manifests). Escape log + `sode
ratchet` (fixture scaffold + escape-log row with required refs); GATE OUTCOMES LEDGER `.sode/gate_outcomes.jsonl`
with human TP/FP adjudication feeding the per-check catch/FP metric (review E8); DETERMINISM GUARD: `sode gate
--repeat N --frozen` must return byte-identical JSON verdicts (a flaky check is quarantined from the registry until
fixed); the escape-log row is the four-part regression record (first diverged step · fault locus model|tool|config|code
· fix-hides-nothing attestation · the returning-defect test).
**Interface.** `sode gate --t0|--t1 [--json] [--changed-only]` · `platform/gate/checks/<name>.py` each exposing
`run(ctx) -> CheckResult{status, remediation, evidence}` · `platform/gate/registry.yaml` (which checks in which
tier, tracked wall-time budget) · `sode ratchet <escape-id>`.
**Acceptance.** Every registered check has a non-empty remediation (test); T1 on the skeleton completes under the
budget in CI; cache test: unchanged inputs → 0 re-runs; each check ships with ≥1 known-bad fixture that FAILS it;
escape-log row without `fixture_ref`+`gate_ref` (or an explicit backlog ref) fails the gate; anti-gaming fixtures: a
diff that deletes a test, adds a skip marker, or edits an acceptance `cmd` FAILS T0 (three fixtures); a check whose
adjudicated FP rate exceeds its catch rate over the window is flagged as a factory_ops item (fixture); `--repeat 10
--frozen` on the skeleton returns 10 identical verdicts (CI); an escape-log row missing any of the four parts fails.
**Failure modes.** Gate false positives eroding trust (per-check FP/catch rates recorded → §9 metric; a check
with FP > catch becomes a factory_ops item); a check silently skipping on a missing path (SKIP is reported, and
T1 with 0 checks run = FAIL — the iter-9 lesson).

## C8 — Review: checker + verdict script + canary + fixer + pre-flight + shadow ledger
**Responsibility.** §6.2/6.4/6.5/6.6: checker prompt (PORT `checker.md`; department checklist slot; D1 security
slot), verdict parser + merge gate (PORT `checker_verdict`), planted-bad canary corpus per run family, the fixer
stage body (decoupled), cumulative pre-flight, the shadow-phase agreement ledger + the auto-ship switch.
**Interface.** `review.run(item, diff, gate_json, checklist) -> Verdict{PASS|FAIL|UNKNOWN, evidence[]}` ·
`merge_allowed(verdict) -> bool` (True ONLY for evidence-complete PASS) · `sode canary <family>` · `fixer.run(item,
findings)` · `preflight.cumulative_diff(item)` · `.sode/shadow.jsonl` `{item, machine_verdict, human_verdict}`;
`autonomy.yellow_auto_ship(dept, klass) -> bool` — True only when n >= 50 decisions in the window, the Wilson upper
bound of disagreement < 2%, the canary is < 7 days old, and no model/prompt/adapter change since the window start (a
change RESETS it; review B11) · `.sode/shadow.jsonl` `{item, machine_verdict, human_verdict, class, dept,
disagreement_type, factory_def_version}` · `review.rounds(item)` bounded by `max_review_rounds`; findings carry ids;
a re-check covers only addressed findings; stale findings invalidated on diff change (review B13) · checker input =
T0 result + last T1 if any (review A5) · canary CADENCE: on adapter/model/checker-prompt change, weekly, and before
enabling auto-ship (review C10) · FAN-OUT COMPLETENESS: gate · QA · security are mandatory legs; a dead/timed-out leg
is recorded UNKNOWN + NAMED and `merge_allowed` is False (never a silent pass).
**Acceptance.** PASS without per-acceptance-id evidence → UNKNOWN (fixture); canary corpus miss → auto-ship
disabled + event; the fixer never runs in the author's clone/session (asserted by distinct worker ids); checker
provider family ≠ implementer family when two families are configured (test over factory.yaml; one family → the
degrade is RECORDED in the record, not silent); shadow ledger 0/5 → auto-ship OFF (n too small); 1/60 → ON only if
the Wilson bound clears; a prompt change mid-window → OFF (reset); a review loop hitting `max_review_rounds` →
`needs-info` hold (fixtures); a QA leg killed by the watchdog → verdict UNKNOWN named in the record → ship refused.
**Failure modes.** Poisoned acceptance (mitigated by C5 lint; the checker cannot see a wrong goal — documented
limit); judge-family bias (cross-family default).

## C9 — Departments (plugin contract + SEVEN v1 departments; `data` later)
**Responsibility.** §4A: `platform/departments/<name>/{kb/, roles/<seat>/, tools.yaml, fixtures/,
review_checklist.md, conventions.md}`; SEVEN v1 departments (security · qa_quality · factory_ops · backend · frontend
· devops · architecture) EXIST as contract-satisfying dirs AND each is CURATED before real work routes to it
(operator 2026-09-18): the `kb_ready` gate (every checklist angle covered by >= 1 sourced entry + a conventions
section; unready department → item holds `needs-info`); the KB ENTRY SCHEMA (`platform/schema/kb_entry.schema.json`:
claim · evidence_type external_practice|our_convention|run_lesson · source · applies_when · does_not_apply_when ·
serves[] · reviewed_on · owner · source_hash); the SEEDING pipeline (`sode kb seed <dept> --sources <file>`:
distillation worker with citations → security source scan → owner review → entries; PARTIAL reads recorded); GAP
surfacing (uncovered angle · unowned pattern · stale entry · worker confusion with no coverage → factory_ops item);
security wires D0 tools into C7 and owns the D1–D3 seats; qa_quality owns the §6.5 ten-angle checklist; seats carry
memory + handoff notes (§3.7).
**Interface.** `departments.load(name) -> Department` · `Department.checklist`, `.kb_slice(touches)` (entries tagged
by evidence_type; EMPTY marker when none), `.tools`, `.seat(role)`, `.kb_ready() -> (bool, uncovered_angles[])` ·
`sode kb seed <dept> --sources <file>` · `sode kb gaps [<dept>]` · `routing.yaml` consumed by C1 (route to an unready
department = hold).
**Acceptance.** A department dir missing any of the six parts fails `check_department_contract`; a KB entry
without `source` when `evidence_type: external_practice` fails the schema; `kb_ready` is False for a department with
one uncovered checklist angle and True once the entry lands (fixture pair); routing an item to an unready department
holds it with the stated reason (fixture); `sode kb seed` on a fixture source set produces entries whose `source_hash`
matches the input and records a PARTIAL for a truncated source; `sode kb gaps` lists a planted uncovered angle; every
`tools.yaml` entry names a pinned version; the qa checklist contains all ten §6.5 angles (doc-sync test); a seat's
handoff note written at session end is primed into the next session (mock adapter test).
**Failure modes.** KB rot (stale-entry check warns in the brief and fails the weekly `sode drift` sweep past the
threshold); an empty KB read as authority (the brief marks an empty slice EMPTY, never omits the marker).

## C10 — Ship: merge queue + profiles + kill switch + notify + handoff + governor + control room
**Responsibility.** §3.4/§8.3–8.4 + review B1: **the MERGE QUEUE** — `ship` takes ONE item at a time: rebase the
item branch onto current main → re-run T1 + the checker on the post-rebase diff → ship; a conflict routes to the
CONFLICT-FIXER stage body (spec + both sides + hunks + acceptance ids) then full re-verify; stacks restack in order
(review B12). Profiles = two booleans + kill switch (`allow_push`, `allow_self_fire`; review C8): `standard` (PR flow,
branch protection checked via GitHub API ONLY in this profile, merge via GitHub, worker push to `sode/<id>` only),
`restricted` (local merge + tag; wait-and-resume; no host scheduler), `local` (standalone test). `sode stop-all` (the
kill switch: SIGTERM → SIGKILL per process GROUP, freeze `active.json`, quarantine clones — review F2); `sode revert
<id>` (review B17); notify adapter (CLI + GitHub); `sode handoff` / `sode resume`; the review-backlog governor; the
CONTROL ROOM `sode ps` / `sode status --live --json` (items · stages · clones · pids · leases · provider · spend ·
current command · stuck age) + global `.sode/events.jsonl` + `sode tail` (review D3).
**Interface.** `ship.run(item)` (lane-gated; = `merge_queue.enqueue(item)`) · `merge_queue.next()` (rebase → T1 →
checker → merge, one at a time) · `conflict_fixer.run(item, hunks)` · `sode stop-all` · `sode revert <id>` ·
`notify.send(item, stage, reason)` · `sode handoff <id>` / `sode resume <id>` · `governor.should_dispatch() -> bool`
· `sode ps` / `sode status --live --json` / `sode tail`.
**Acceptance.** GREEN item with all PASS → shipped with no human event in `events[]`; RED item → ship waits for a
hash-bound human decision; STALE-BASE fixture: main moves after the item's T1 → ship rebases and re-runs T1 + checker
before merging (asserted by the second gate run in `events[]`); CONFLICT fixture → conflict-fixer worker, then full
re-verify, never a merge with markers; two ready items → merged one at a time in queue order; `restricted` profile:
any push attempt → refused; `sode stop-all` kills a running mock worker's process group within one tick, freezes
`active.json`, quarantines the clone, and a recovery test resumes from disk; governor: N items awaiting a human → next
`implement` dispatch refused; `sode revert <id>` creates an expedited small item; profile MATRIX test (push · ship ·
continuity · automations · doctor × local/standard/restricted) passes (review F6).
**Failure modes.** Branch-protection misconfig (doctor check against the GitHub API in `standard`); a notification
channel down (falls back to CLI log + hold persists).

## C11 — `measure` stage
**Responsibility.** §4.7: the BASELINE of `impact_metric` is captured during `verify` as a ship prerequisite (review
A2); the after-reading runs after `window` through `sode-run` (review B4); verdict appended to the record
(`record_complete_after_measure`), follow-up item on `excessive`, metric history annotated (§9.5 attribute); default
metric for refactor/maintainability items = code-quality delta (review C4); at ship the engine appends `{item, due_at,
metric, read_cmd_hash}` to `.sode/measure_queue.jsonl` (GAP-5/hawk A16) and the C15 automation drains it.
**Interface.** `measure.baseline(item)`, `measure.read(item)`, `measure.verdict(baseline, after, rule) ->
valuable|neutral|excessive` · runs as an automation after `window`.
**Acceptance.** Fixture metric series → the three verdicts as specified; `excessive` → a new item exists with
`parent` = the measured item; metric history row carries the item id.
**Failure modes.** Metric unreadable (verdict `unmeasured`, recorded, alerts — never silently `neutral`).

## C12 — Cost: usage readers · window headroom · stop rules · prediction ledger
**Responsibility.** §9.1–9.4: per-adapter usage readers; window HEADROOM (5h/7d) — CODEX: parse `rate_limits` from the
latest local session rollout (`~/.codex/sessions/**/*.jsonl` → `primary.used_percent`, `resets_at`; verified
2026-09-18); CLAUDE: PORT of this repo's transcript-usage parser + era-scoped rate model + UI% calibration samples
(`sode headroom calibrate --ui-pct N`); FALLBACK CHAIN (review B10): exact read → estimate + fresh sample → estimate
with widened reserve → hold + notify past `headroom_stale_s`; the two flat stop rules; `.sode/predictions.jsonl` +
empirical p80 caps after ≥10 samples; every trajectory has exactly one prediction row (completeness check); cache-hit
MEASUREMENT (review C7).
**Interface.** `cost.usage(worker_result) -> {rate_pct, cost_m}` · `cost.headroom(provider) -> {h5_pct, d7_pct,
source: exact|estimate|stale, sampled_at}` · `sode headroom [calibrate --ui-pct N]` ·
`cost.stage_cap(item, stage) -> cap` (ledger-derived when ≥10 samples, else hand estimate) · `cost.check(item,
stage, spent) -> OK|HALT|KILL`.
**Acceptance.** Ledger with 10 samples → cap = p80 (test); 9 samples → hand estimate; spent 1.6× cap → HALT,
2.1× → KILL; headroom below reserve → engine waits (mock provider); every stage run appends exactly one prediction
row with `actual` filled at completion.
**Failure modes.** No exact read AND stale estimate (fail-closed: hold + notify; never a silent permanent stall — the
notification names the missing calibration sample); Codex rollout schema drift (parser pinned to a fixture; drift =
adapter DEGRADED).

## C13 — Observe store (v1 = the irreversible part; v1.1 = scorers · replay · distillation)
**Responsibility (v1, review C1).** §7.3–7.4: immutable hash-addressed, HASH-CHAINED trajectories (`.sode/
trajectories/`, every stage run, negatives included, REDACTED); `evals/tasks/` golden-set SKELETON + append-only
history sidecar; `platform/evaluator/MANIFEST.yaml` (hashes of gate registry · rubrics · canary corpus · golden set ·
holdout — review E6); `.sode/active.json` + promotions log with atomic promote/rollback + failure injection (partial
write · bad pointer — review F8); retention policy for transcripts (never for trajectory metadata); `sode harness-card`
— the deterministic 8-field HarnessCard from `factory.yaml` + `active.json` (base model · control artifacts · runtime
policy · action substrate · topology · feedback stack · governance · evaluation protocol); every trajectory carries its
hash; the SYSTEM card is regenerated at every promotion; failed trajectories carry `failure_class`.
**Responsibility (v1.1, after the WALK milestone).** sampled scorers (cross-family judge) · `sode replay` · the
experience-bank distillation job (`sode distill`, evidence refs on every entry).
**Interface (v1).** `trajectories.write(run) -> sha` · `trajectories.verify()` (hash chain) · `sode eval` (golden-set
skeleton runner, sidecar history) · `sode harness-card` · `sode promote <version>` / `sode rollback` · evaluator
manifest check. **Interface (v1.1 = C13b, build row 21):** `scorers.run(sample)` · `sode replay <id> --config
<variant>` · `sode distill` (writes KB entries with evidence refs, as a factory_ops item).
**Acceptance (v1).** Writing the same run twice → one file (content-addressed); tampering a trajectory → hash check
FAIL; golden set file unchanged after `sode eval` (sidecar only); `promote` then `rollback` restores the prior pointer
atomically (+ failure injection); a change under `evals/` or `platform/gate/` from a non-architecture item → gate FAIL
(mutation boundary); `sode harness-card` is byte-identical for identical `factory.yaml` + `active.json`.
**Acceptance (v1.1 / C13b).** replay of a recorded mock item reproduces its terminal outcome under the same config;
scorer judge is cross-family; a distilled entry carries evidence refs.
**Failure modes.** Store growth (retention policy for transcripts, never for trajectory metadata).

## C14 — Metrics registry + `sode metrics` + alerts
**Responsibility.** §9.5–9.6: `metrics/registry.yaml` schema + gate (a registry entry needs definition · drivers ·
owner AND a `metrics.compute` implementation AND every formula field bound to a named schema field — unknown field =
FAIL, review E12); bootstrap SEEDS five hard metrics (lead time · first-pass gate rate · re-dispatch rate · escapes ·
headroom — review C3), the group discussions add the rest; per-window computation from local stores; history under
`.sode/metrics/` with a periodic committed snapshot (append-only files never live on shared branches); dashboard (JSON
+ generated markdown); alert automation → factory_ops item.
**Interface.** `sode metrics [--window w]` · `metrics/registry.yaml` (§9.5 shape) · `metrics.compute(id, window)`
· `metrics.alert(id) -> None | Alert`.
**Acceptance.** A registry entry without `definition`/`drivers`/`owner` fails the gate; a seed metric computed on
a fixture store matches its hand-computed value; a 3-window decline fixture → an alert → a new factory_ops item.
**Failure modes.** Vanity metrics (the registry gate + the per-group discussions are the control).

## C15 — Automations (trigger → action runner)
**Responsibility.** §2.5 crawl set + §9.5 alerts + §4.7 measure windows + the weekly `sode drift` SWEEP (review E14:
doc↔policy render equality · schema versions · rule provenance · adapter pins vs installed · KB staleness · evaluator
manifest hashes · prediction-row completeness · registry compute coverage · port manifests · gate determinism
(`--repeat --frozen`) · the CAR × 2×2 coverage grid with thin cells · prompt/skill/checklist curation candidates):
`factory.yaml automations[]` entries
`{trigger: cron|pr_opened|ci_red|issue_labelled|alert, action: <stage body>, department, budget}`; runs under the
engine (never a top-level self-fire in `restricted`).
**Interface.** `sode automations list|run <name>|enable|disable` · trigger adapters (cron via the host scheduler in
`standard`; in-session timer in `restricted`; GitHub webhooks/polling).
**Acceptance.** A `pr_opened` fixture event → the review stage body dispatched once (idempotent on re-delivery);
`restricted` profile → a cron automation refuses to install a host scheduler entry.
**Failure modes.** Trigger storms (per-automation rate limit + budget).

---

## Standalone-clone acceptance (§1.4) — the cross-cutting test `tests/test_standalone.py`
In a temp HOME with no network and no sibling repo: `git clone` → `make test` GREEN → `sode init --profile local
--provider mock`
→ `sode new "hello" --class small` → `sode tick --until done` (the `--until` verb is in the C2 interface) →
`work/<id>/record.yaml` passes `record_complete_for_ship` → `sode metrics`
renders → `grep` clean of growth-hack-system paths/ids/client names/credentials. This test is C0's acceptance and
the WALK milestone (§2.5).
