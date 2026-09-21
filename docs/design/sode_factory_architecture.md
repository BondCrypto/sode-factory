# sode-factory — architecture spec

**Status:** §1–§9 + §4A + §1.6 + §2.7 LOCKED (design session 2026-09-15 → 2026-09-21); build plan + build sessions LOCKED 2026-09-21; repo initiated 2026-09-21 (github.com/BondCrypto/sode-factory); amended 2026-09-18 per the adversarial review `docs/audits/sode_factory_spec_review_2026-09-18.md` (operator-adopted dispositions). Locked sections are marked `LOCKED`; everything else
is open. Consumer = the sode build dispatch ([[exec_factory_direction]]; backlog
`exec-factory-skeleton-first-product-polymarket-paper-engine`). Inputs: `docs/design/exec_factory_design_inputs.md`
(the design brain, §8 cross-map = the reuse guide) · `docs/design/system_architecture_synthesis_under_single_goal.md`
§5 + §14 (repo topology, the card interface, the build gate) · `docs/design/autonomy_harness.md` (the assets
ported). Companion artifacts: `docs/design/sode_factory_component_specs.md` (per-component build-ready specs) ·
`docs/design/sode_factory_build_plan.md` (dependency-ordered components + acceptance + brief stubs) ·
`docs/design/sode_factory_build_sessions.md` (the split into fresh build sessions S1–S21 + K1–K7) ·
`docs/design/sode_factory_guard_rules_seed.yaml` (the verbatim rule catalogue for the guards session).

**Authority boundary:** this doc governs the SIBLING repo's architecture. It never redeclares this repo's
pipeline mechanics or platform design. Where sode ports an asset from here, this doc names the SOURCE and the
ADAPTATION; sode never imports the source.

**Two fixed constraints (operator, not reopened):**
1. **Standalone-clone value** — a fresh clone of sode is independently valuable. Acceptance criterion, §1.4.
2. **Architecture before skeleton** — no sode code builds before this spec + the build plan lock.

---

## 1. Scope + boundary — LOCKED (operator 2026-09-15, option 1)

### 1.1 What sode IS
sode-factory is a **software factory**: the outer loop that owns work (triage → spec → implement → review →
verify → ship → monitor), driving ephemeral, isolated, bounded workers, with a self-evolving loop over its own
runs. It produces production-ready execution tooling for real use.

sode has TWO planes in ONE repo:
- **Factory plane** (`platform/`) — the outer loop, workers, work representation, context record, verification,
  the self-evolving loop, guards, cost. **This session specs this plane (agenda 2–9).**
- **Product plane** (`products/<line>/`) — product lines the factory builds and operates. First line = the
  polymarket paper engine (risk kernel · config-as-code · tape replay · strategy-card intake · re-validation
  loop · maintenance). **Spec = a separate follow-up session.** The build gate (synthesis §5: no product code
  before a `paper_validated_card` exists) means this deferral blocks nothing that can build today.

### 1.2 What sode is NOT
- Not a research pipeline. No P1–P7, no RESEARCH KB (the mechanism graph), no hypotheses. Research stays in growth-hack-system. (Departments carry their own DOMAIN KBs, §4A — a different thing.)
- Not a sub-module or plugin of this repo. A SIBLING: neither repo imports the other's internals.
- Not a cloud service. Local-first; no external orchestration infra; no external API without operator approval.
- Not autonomous over irreversible acts. Live money acts remain the operator's ([[polymarket_profitability_track]]).

### 1.3 Three platform decisions locked here (cheap, layout-shaping)
a. **ONE repo**: `platform/` + `products/<line>/`. Maintenance/monitoring is a PLATFORM layer, not a second
   repo (synthesis §5 option 1). Split trigger recorded: a separate on-call, or more than a handful of live
   products.
b. **The research↔sode interface is exactly two gated artifact classes and nothing else**: OUTWARD
   (research → sode) the strategy card + stamped tapes, through the outward-export gates (allowlist +
   byte-scan); INWARD (sode → research) production measurements appended as data-derived rows. No shared
   code, no shared paths, no shared ids.
c. **No hardcoded sibling path.** Discovery is CONFIGURED (a `sode.config.yaml` `siblings:` entry) or relative;
   absent config → sode runs alone.

### 1.4 Standalone-clone contract (acceptance, machine-checkable)
A fresh `git clone` of sode, with no other repo present:
1. `make test` (or the documented one-command gate) is GREEN.
2. Runs ONE factory work item end to end with a MOCKED model provider (intake → worker → review → verify →
   ship), producing its context record.
3. `grep` of the tree is CLEAN of: any absolute path into growth-hack-system · any id namespace from it
   (`hyp_`, `mech_`, `pm_`…) · any client name · any credential value.
4. Every ported asset carries its own tests inside sode (ported = copied + adapted + tested, never imported).

### 1.5 What is ported vs referenced (from the §8 cross-map)
| Asset (source in this repo) | sode form |
|---|---|
| separate-clone isolation (autonomy §13.14) + `git_env.clean_git_env` | PORT (worker isolation, §3) |
| `destructive_guard.py` + the ASK-prompt pattern (`collector_ctl.py`) | PORT (guards, §8) |
| gate suite shape (`gates_runner.py --fast/--full`, remediation-per-check) + defect→fixture→gate ratchet | PORT the SHAPE, sode-native checks (§6) |
| `classify_dispatch_state` + `dispatch_ledger` (atomic, lease) + `acceptance_lint` + checker (`checker.md` + `checker_verdict.py`) | PORT (§3, §6) |
| two-currencies cost model + budget cap + checkpoint breaker | PORT the MODEL (§9); measurement tooling adapted |
| brief skeleton + lanes GREEN/YELLOW/RED + backlog item shape | PORT + type (§4) |
| END_OF_RUN / checkpoint-report / current_state | PORT as the per-item context record (§5) |
| `eval_runner` + regression history | PORT the SHAPE; sode-native eval set (§7) |
| autonomy GO (`autonomy_go.yaml` + `check_autonomy_go`) | PORT (arming model, §8) |
| P1–P7 prompts, KB, schemas §12, chain layouts | NOT ported. Research-only. |

**Port-conformance manifest (review E2).** Every PORT row above lands with `platform/ports/<asset>.yaml`: source path · source commit · adapted invariants · intentionally dropped behaviour · the sode tests that pin each kept invariant. A port without its manifest fails the gate.

### 1.6 Repo structure + folder taxonomy — LOCKED (operator 2026-09-21)
```
sode-factory/
  factory.yaml            the versioned factory definition (the ONLY config in git; machine-local = .sode/local.yaml)
  Makefile · README.md
  bin/                    sode · sode-sh · sode-run   (three binaries; workers call the last two directly)
  platform/               the FACTORY plane — ONE package per component (C0–C15):
    cli/ core/ schema/ config/ policy/ work/ engine/ workers/ guards/ brief/ record/
    gate/ review/ ship/ measure/ observe/ departments/<name>/ metrics/ automations/ ports/ api/
  products/<line>/        the PRODUCT plane; imports platform ONLY through `platform/api`
  work/<id>/              work items: item.yaml · spec.md · decision.md · events.jsonl · record.yaml · briefs/ · artifacts/
  metrics/                registry.yaml + committed snapshots (history lives in .sode/metrics/)
  evals/                  golden set · hashed holdout · sidecar history (evaluator surface, hash-pinned)
  docs/design/            the spec set (this doc + component specs + build plan + build sessions + guard seed)
  docs/adr/               PROMOTED decision records (a work/<id>/decision.md that binds more than one item)
  docs/runbooks/          operator runbooks (compromise runbook · headroom calibration · release)
  tests/                  mirrors platform/ one-to-one + tests/test_standalone.py
  .sode/                  GITIGNORED runtime: run/ actions.jsonl effects.jsonl leases/ clones/ trajectories/
                          active.json predictions.jsonl gate_outcomes.jsonl shadow.jsonl measure_queue.jsonl
                          metrics/ logs/shim.jsonl local.yaml
```
**Placement rules** (enforced by a `check_repo_structure` port with an ALLOWLIST; a violation hard-fails the gate):
1. One component per package; one test package per component (`tests/<package>/`).
2. `platform/` NEVER imports `products/`; `products/` imports `platform/` only through `platform/api` (import-lint).
3. A NEW top-level directory = operator-approved + an allowlist edit in the SAME commit.
4. No runtime state in git except committed snapshots (`metrics/`); `.sode/` is gitignored wholesale.
5. Generated files carry `<!-- GENERATED -->` markers; hand edits inside markers fail the gate.
6. Per-item decisions live in `work/<id>/decision.md`; promoted to `docs/adr/` when they bind more than one item.
7. Department directories carry the six-part contract (§4A) — nothing else lives under `platform/departments/`.

---

## 2. Outer-loop lifecycle — LOCKED (operator 2026-09-15, option 2)

### 2.1 Stages (v1 = SEVEN incl. `measure`; `monitor` deferred to the first product line)
Each stage is a STATE with one entry artifact, one exit artifact, one owner, and a deterministic transition.
The lifecycle engine is a PORT of `supervisor.py`'s execution model: pure, no model call, resume-from-disk;
each tick computes ONE next transition from on-disk state and either performs it (deterministic) or emits a
structured pending-action for a worker (the only place a model runs).

| Stage | Entry artifact | Exit artifact | Owner |
|---|---|---|---|
| triage | raw intake (issue · wish · defect · monitor signal) | work item: class + lane + label | human decides; factory proposes |
| spec | item with `stage=spec`, `label=null` (§4.4: queue state is derived, labels are holds) | spec: intent · executable acceptance · touches · program-design artifacts (large class) | spec worker; human LOCK above small class |
| implement | locked spec | commits in an isolated worker clone + record draft | implement worker |
| review | diff + spec | checker verdict (autonomous, evidence-required) + QA + security review by depth | checker + department seats; human ONLY per the §6.2 pre/post-shadow rule |
| verify | reviewed branch | gate PASS/FAIL + acceptance-script results | factory, deterministic |
| ship | verified branch + verdict + `record_complete_for_ship` | MERGE QUEUE: rebase → re-assess → merge to main + tag; record closed for ship | GREEN auto; YELLOW per §6.2 pre/post-shadow; RED human |

**Review ∥ verify as a FAN-OUT BARRIER (hawk A3 — parallelism kept, state machine made explicit):** the `review`
stage LAUNCHES the assessment legs (QA seat · security seat/pass · engine-owned T1 gate · engine-owned baseline
capture) as pending actions/jobs and COLLECTS their outputs into `work/<id>/artifacts/review/<attempt>/
{gate,qa,security,baseline}.json`; the `verify` stage is DETERMINISTIC AGGREGATION only: every mandatory leg
present (a missing/dead leg = UNKNOWN, named) → `merge_allowed` → transition. One tick still performs one edge.
| measure | shipped item whose `impact_metric` BASELINE was captured as a `verify` artifact (medium/large, or any YELLOW/RED) | after-window reading + verdict `valuable / neutral / excessive` appended to the record | factory (deterministic read via `sode-run`) + human on `excessive` |
| monitor | LATER (needs a live product) | LATER | product plane |

**Amendment (operator 2026-09-16):** `measure` is a v1 stage (seven stages v1). It is a time-boxed check of ONE
change against its declared metric ([[measure_before_after_adoption]] made structural); `monitor` is production
runtime and stays deferred. `verify` ALWAYS contains a SECURITY element (depth graded, §4.3); nothing reaches
`ship` without it. Decision-class work (`architecture`) has a `research → decide` prefix before `spec`.

### 2.2 Ownership rule
The factory owns WHAT and WHEN (state machine · artifacts · transitions · scheduling). The worker owns HOW
inside one stage and never crosses a stage boundary. A diff is not "done": done = the ship exit artifact.

### 2.3 Class-dependent path
ONLY `trivial` work skips `spec` (the one-shot path); `small` carries an inline spec (§4.2). Which classes require which stages is the work-class
table (§4). The engine reads the class table; it never asks a model whether a stage is required.

### 2.5 Adoption path — crawl → walk → run (Warp/Lloyd 2026-09-15, folded 2026-09-17)
- **Crawl** = point AUTOMATIONS (trigger → one stage body): issue triage + repro · PR review · CI self-heal ·
  docs/changelog update · verification · simple bug fixes. Each is one `automations:` entry running one stage.
- **Walk** = ONE full loop on ONE simple product surface. For sode the simple surface is **sode itself**
  (factory_ops items) — the standalone-clone test (§1.4) IS the walk milestone.
- **Run** = scale to complex targets; the known bottlenecks (Lloyd): env setup for large repos · churn detection
  (our `measure` stage) · cost → routing · security + audit · multi-stakeholder sign-off · PR pile-up strategy ·
  closing the loop to production quality (`monitor`). Expectation datums: ~20–30% of issues fully automatable in
  general; ~75% on a simple surface.

### 2.6 Replan transition (review D1)
A parent item RETURNS to `spec` with the failure handoff when any replan trigger fires: a child HALTs · the base is stale beyond a rebase · a merge conflict the conflict-fixer cannot close · repeated PARTIAL (>= 2) · a dependency landed that changes the spec · `measure` regression on a named metric. Replanning is a state-machine edge, not a judgment call.

### 2.7 Transition contract + responsibility boundaries — LOCKED (operator 2026-09-21)
The flow below CONSOLIDATES §2.1 · §2.2 · §2.6 · §3.5 · §4.2 · §4A · §6.1 · C2 into one place. Where this table and a
scattered sentence disagree, THIS table wins (and the sentence is a defect to fix).

| Stage | Picked up by | Trigger | Entry check | Produces | Success edge | Failure edges |
|---|---|---|---|---|---|---|
| triage | the ROUTED department's seat proposes (factory_ops = fallback); human ratifies | intake event (`sode new` · `sode intake`) | intake has source + text | item.yaml: class · lane · dept · depth · touches | stage=spec (trivial → implement) | `needs-info` with ONE question |
| spec | routed dept spec seat | stage=spec · label null · dept `kb_ready` · lease free · WIP slot | `sode lint` clean | spec.md · spec_lock_brief · child items | human lock (medium+) → stage=implement | BOUNCE to triage ONCE with a reason ("not mine") · `needs-info` |
| implement | routed dept implement seat | spec locked (`spec_hash`) · lease free · WIP slot · headroom | spec_hash matches · `branch_ref` exists | commits on branch · stage manifest · report-back | COMPLETE → stage=review | PARTIAL → continuation · EMPTY → fresh · attempts out → `halted` |
| review | ENGINE launches the legs: QA seat · security seat/pass · T1 gate job · baseline job | implement manifest present | diff non-empty · T0 green | `artifacts/review/<attempt>/{gate,qa,security,baseline}.json` | all mandatory legs present → stage=verify | findings → fixer worker (bounded rounds) · dead leg → UNKNOWN |
| verify | engine, deterministic | all legs collected | every mandatory leg present | `merge_allowed` · `record_complete_for_ship` | PASS → stage=ship | FAIL → implement with findings · UNKNOWN → `needs-info` |
| ship | engine MERGE QUEUE; human per §6.2 lane rule | verify PASS · approval `ship_hash` where required | ship_hash valid · base current | merge · tag · PR body · `measure_queue` row | stage=measure (or done) | conflict → conflict-fixer → re-verify · stale approval → re-request |
| measure | engine automation | `due_at` reached | baseline present | verdict on record | done; `excessive` → follow-up item | unreadable → `unmeasured` + alert |

Any stage may fire the REPLAN edge back to `spec` on a §2.6 trigger. `halted` is released only by a human
`sode release <id> <reason>`. Cross-cutting departments (qa_quality · security) are CONSULTED on every review; the
routed department OWNS the item.

**Responsibility boundaries (who may do what):**
| Responsibility | Engine | Department seat | Worker | Human |
|---|---|---|---|---|
| decides which stage is next | OWNS | never | never | never |
| picks the item | OWNS (scheduler policy) | never | never | may pin priority |
| does the work inside a stage | never | owns checklist + KB | owns the HOW | never |
| judges quality | deterministic gate | QA + security seats | never self-grades | structure only (§6.2) |
| approves | lane policy | never | never | spec lock · RED ship · release from `halted` |
| sends work back | on classify / verify | via findings (ids) | via report-back concerns | via `/sode reject` |
| writes the record | OWNS | never | report-back only | hash-bound commands only |
| may bounce an item | never | ONCE, to triage, with reason | never | at will |

### 2.4 Trade-off accepted
v1 does not close the loop to production outcomes. `monitor` lands with the first product line; until then
the item record carries a `monitor_hook` field left empty.

## 3. Worker model — LOCKED (operator 2026-09-15, revised recommendation)

### 3.1 Operator direction folded in (2026-09-15)
- Build around BEST PRACTICES, not this machine's current limits (MDM, no-push). Machine-specific limits are a
  POLICY PROFILE (§3.4), never architecture. sode must run on any new machine with one config file and one
  command per verb.
- MODEL-AGNOSTIC: the operator switches model or provider at any time; the system works as intended.
- Subscription-based providers first (OpenAI + Anthropic CLIs); API-billed later, as a second adapter.

### 3.2 Isolation — a clone per worker (backend pluggable)
- Root cause of the 2026-07-31 `core.bare` incident: git exports `GIT_DIR`/`GIT_WORK_TREE`/… into hook-spawned
  processes; a worktree SHARES config/refs/index/objects, so a confused worker resolves against the ambient repo.
  Per-worktree config does not help (a plain `git config` write still hits the shared file). Industry practice at
  scale matches ours: workers run on repo COPIES (Cursor) or in containers (background-agent systems).
- v1 backend = a LOCAL clone with git's default hardlinks (near-instant; git never rewrites an object file in
  place, so hardlinks are safe — the old `--no-hardlinks` was over-caution). `isolation: clone | container`;
  container = later (stronger, same idea; needed for external targets or when the guard floor is insufficient).
- Git env is SCRUBBED on every git spawn (port `git_env.clean_git_env`; AST-test that no unscrubbed spawn lands).
- **Brain outside the box (batch 25, @katelyn_lesse; batch 23 @nathanflurry):** the engine, the ledgers, the
  secrets broker, the shim log and the kill switch live on the HOST, never inside a worker's execution boundary;
  the worker boundary is an execution tool only. When the `container` runner lands, pick its strength from the
  ISOLATION LADDER — plain container (shared kernel; not a boundary for untrusted code) < gVisor < Firecracker
  microVM (recommended point) < full VM — run sandboxes as EPHEMERAL cattle (hard time/resource caps; install deps
  at start, then lock the network; default-deny egress with a narrow host allowlist; destroy at end), and inject
  scoped credentials through an egress proxy in place of placeholders. An OS syscall jail (macOS Seatbelt / Linux
  Landlock) is the host-side alternative when containers are not wanted (backlog `evaluate-syscall-jail-confinement`).

### 3.3 Per-stage binding — `factory.yaml` (version-controlled factory definition)
```yaml
schema_version: 1
policy_profile: standard          # standard | restricted   (§3.4)
isolation: clone                  # clone | container
secrets_broker: 1password         # workers get secrets via `op run` at process start; never on disk
secrets_registry: platform/policy/secrets.yaml   # secret ids · allowed stages · redaction patterns · broker-unavailable = hold (review B5)
targets:
  self:                             # v1: sode itself + its products/
    path: "."
    default_branch: main
    setup: "make setup"            # env PROVISIONING manifest (review B7): setup · test_cmd · cache · services · healthcheck · clean
    test_cmd: "make test"
    cache: { dir: ".sode/cache/self", key: [lockfile_hash] }
    healthcheck: "sode doctor --target self"
    gate: { t0: [lint, types, unit_changed], t1: [all] }   # per-target gate config
git: platform/policy/git.yaml     # allowed remotes · worker refspec sode/<id> only · canonical identity · commit-msg rule · protected branches (review B6)
reserve_pct: 15                   # subscription-window reserve (§9.1)
runners:                          # WHERE workers run (Warp "runners"); v1 = local_clone; container/remote later
  local_clone: { isolation: clone, watchdog: {heartbeat_s: 120, no_output_s: 900, wall_clock_s: 7200} }
automations: []                   # TRIGGER -> ACTION rules (cron · CI red · PR opened · issue labelled · alert); v1 = the
                                  # "crawl" set (§2.5); each automation names its stage body + department + budget
integrations: { github: {mode: pr_view}, chat: null }   # access layer; v1 = CLI + GitHub; Slack later
decision_model: null              # §6.7 — System-One decision-model adapter (Sage/Jev class); EMPTY in v1, pre-flight-gated
scorers: { sample_rate: 0.25, dimensions: [task_compliance, procedure_compliance, verbosity, efficiency, code_quality] }
                                  # §7 — the Observe layer; graded runs feed the self-evolving loop
providers:                        # declarative CAPABILITY MATRIX — no `if provider == x` anywhere
  anthropic_cli:  { adapter: claude_code_cli, billing: subscription, families: [claude], tools: [bash, edit, read], hooks: claude_hooks }
  openai_cli:     { adapter: codex_cli,       billing: subscription, families: [gpt],    tools: [bash, edit, read], hooks: codex_config }
  mock:           { adapter: mock,            billing: none,         families: [mock] }
stages:
  spec:       { provider: anthropic_cli, model: <id>, permission: plan_only, budget: {rate_pct: 3, cost_m: 0.5}, max_attempts: 2, secrets: [] }
  implement:  { provider: anthropic_cli, model: <id>, permission: edit_in_clone, budget: {rate_pct: 8, cost_m: 2.0}, max_attempts: 3, secrets: [] }
  review:     { provider: openai_cli,    model: <id>, permission: read_only, budget: {rate_pct: 2, cost_m: 0.5}, max_attempts: 1, secrets: [],
                cross_family_required: true }     # the checker defaults to a DIFFERENT family than implement
  verify:     { provider: none }                  # deterministic; no model
  ship:       { provider: none }                  # deterministic; lane-gated
```
- **Adapter registry + capability tests (review D4/E7):** each adapter declares `cli_version` (pinned; doctor fails on unknown/unpinned), permission mapping, usage-field contract, transcript-fixture version, and passes the capability suite: can edit · run shell through the shim · be interrupted · install the guard hook · report usage · resume. An adapter that fails a capability enters DEGRADED mode: it may run, auto-ship is disabled for its stages.
- **Adapter interface (the translation layer):** `run(brief_path, clone_path, stage_cfg) -> WorkerResult`
  where `WorkerResult = {exit, commits[], artifacts[], usage{...}, transcript_ref}`. The adapter owns: launching
  the vendor CLI headless · installing the guards in the provider's native form (hooks / config) · mapping
  permission modes · reading usage. Briefs are PROVIDER-NEUTRAL text: no vendor-specific syntax inside a brief.
- A model switch is PROVEN by the eval set (§7), never assumed.

### 3.4 Policy profiles
| | `standard` (default) | `restricted` (this machine today) |
|---|---|---|
| ship surface | branch per item → push → PR → CI → checker review on the PR → merge via GitHub (branch protection, required checks) | local merge + tag; operator pushes |
| continuity | scheduled runner / daemon allowed | engine session waits in place, resumes on window refresh, NEVER self-fires (MDM) |
| GitHub API | issues/PRs/merges direct | read-only or none |
Same engine, same state machine, same artifacts. **A profile is exactly two booleans + the kill switch** (review C8): `allow_push` and `allow_self_fire`; `standard` = true/true, `restricted` = false/false, `local` (the standalone-test profile) = false/false with mock provider and no broker. No GO-file port: the structured GO stays this machine's artefact. Profile behaviour is pinned by a matrix test (push · ship · continuity · automations · doctor × profile).

### 3.5 Worker lifecycle (one work item, one stage)
1. **provision** — a FRESH local clone per STAGE (hardlinks, cheap), scrubbed env, checked out at the item's
   `branch_ref` (= `sode/<id>`, created from `base_ref` at the first WRITE stage; `plan_only` stages get a READ-ONLY
   clone with no branch and no push — GAP-2). Every stage starts from COMMITTED state; a stage never inherits an
   uncommitted tree (GAP-1 decided 2026-09-18 with the Codex hawk-eye pass: ephemeral workers = ephemeral clones).
   The runstate records `dispatch_ref` (the sha the stage started from); classify compares against it.
2. **arm** — adapter installs guards (§8) into the clone's launch config; stage secrets injected via `op run`.
3. **run** — adapter executes the paste-first brief (§4) under an `action_id` (deterministic from item+stage+attempt; recorded in `.sode/actions.jsonl` with `claimed_by`, `pid`, `result_ref` BEFORE spawn — a re-tick that finds a claimed action never spawns twice, review B2). The WATCHDOG (port of `dispatch_watchdog`) tracks heartbeat (transcript mtime + commit count), no-output timeout, wall-clock cap; on stall: process-group kill → classify → quarantine the clone (review B3). Worker writes artifacts to DISK before any final message. At its CONTEXT LIMIT a worker writes a handoff note and returns PARTIAL — never compacts (review B22). Workers keep context at ~40–60% utilization and COMPACT
   status into the record/plan artifact after each verified phase, not into the transcript (HumanLayer FIC, batch 7).
   A FAILED run carries a `failure_class` (tool_misuse · missing_context · reasoning_error · spec_error · env_failure ·
   provider_error) on its trajectory (Self-Harness, batch 10); the report-back `rejected_paths[]` of a failed or
   PARTIAL attempt is FED FORWARD into the continuation brief so dead ends are not re-explored (FAPO).
4. **classify** — on ANY exit signal: `classify_dispatch_state(clone, base_ref, acceptance_hash, phase_id)` →
   COMPLETE | PARTIAL | EMPTY. The clone is the oracle; the notification never is. COMPLETE requires a CLEAN tree,
   the REQUIRED acceptance run (never skippable) pinned by `acceptance_hash`, and phase identity read from COMMIT
   TRAILERS (`Sode-Item` · `Sode-Phase` · `Sode-Attempt` · `Sode-Acceptance-Hash`) — never a commit COUNT (this
   repo's own oracle-hardening lesson, backlog `autonomy-oracle-hardening`: commit count is not a completion contract).
5. **ledger** — atomic, leased write (port `dispatch_ledger`: temp+fsync+rename; corrupt = FATAL, never empty).
6. **route** — COMPLETE → next stage · PARTIAL → continuation worker with a RESUME-STATE preamble · EMPTY → fresh
   worker · attempts > max → HALT + notify. A dead worker is a WORK ORDER, not an error. Adapter ERRORS are typed (auth · rate-limited · outage · CLI drift · permission prompt) → hold with backoff; a CLI-drift error puts the adapter in DEGRADED mode (review B21).
7. **teardown** — the stage clone is removed when its action resolves (COMPLETE/PARTIAL/EMPTY classified); a clone
   killed by the watchdog is QUARANTINED under `.sode/clones/quarantine/` for diagnosis; the branch outlives the
   clone until `ship`. v1 does normal teardown + quarantine only; policy GC / archive = backlog B013. Transcript +
   usage kept as a trajectory (§7). Every stage exit writes `work/<id>/artifacts/<stage>/<attempt>/manifest.yaml`
   — the ONLY recordable exit surface (hawk B2); the record projects from manifests + `events.jsonl`, never by
   scanning files.

### 3.6 Trade-off accepted
Two vendor adapters to maintain (+ mock), in exchange for a real model/provider switch with no rebuild and zero
external infrastructure.

### 3.7 Seats, handoff, refusal (Yegge "Model welfare", folded 2026-09-17)
- **Seat vs session.** A department ROLE is a SEAT: a named, addressable identity with its own memory and
  history that survives model upgrades and renames. A worker run is a SESSION (one workday). Seats live in
  `platform/departments/<dept>/roles/<seat>/` (prompt + memory + history); sessions are ephemeral (§3.5).
- **Handoff, not exit.** A seat's session ends with a handoff note (what happened · what remains · why) written
  to the seat's memory BEFORE termination; the next session primes from it. Same shape as our wrap discipline.
- **Never falsify the record.** `record.yaml` + trajectories are the true history; no compaction that replaces
  a seat's own notes with someone else's summary.
- **Right to refuse / escalate.** Any worker may return `needs-info` ("this needs the operator") instead of
  guessing; the label holds the item (§4.4). Crons watch, models act.
- **Bespoke-harness tension (Yegge: harnesses will be bespoke, bonded to the application).** sode's answer:
  `platform/` = the REUSABLE outer loop + guards + record + evals; each `products/<line>/` binds its own
  harness pieces. The factory is reusable; the product harness is bonded.

## 4. Work representation + decomposition — LOCKED (operator 2026-09-16)

### 4.1 Store — one directory per item; on-disk item is canonical
**Third-party item store (beads et al.) — DEFERRED (operator 2026-09-17; review C12/A11).** sode BUILDS its native store (§4.1) — no "delete if adopted" clause. `beads` (`bd`; MIT, Go, embedded Dolt; hash ids; `bd ready` / `--claim` / `remember` / `prime`; Claude+Codex hooks) is ONE backlog item in the sode bootstrap (build plan §3 B001) with its own pre-flight (pinned `sfw brew` install · offline · custom fields · churn) and a pilot AFTER W3. Yegge's brain/doc/beads/remember/skills layering maps onto §5 (Appendix A.1).

`item.yaml` (ported from `backlog.yaml` + typed):
```yaml
id: <kebab-id>                 title: <one line>
class: trivial|small|medium|large|architecture     # §4.2 — decides required stages
lane: GREEN|YELLOW|RED         # from BLAST RADIUS (cost to undo) or decision-class; never from confidence
label: null|needs-info|blocked|parked|cancelled   # HOLDS only (§4.4); queue state is DERIVED from `stage`
overlays: [security-sensitive, irreversible]       # optional, stack on any class
priority: P0..P3               outcome: <the observable this work should move>     parent: <goal item id>
depends_on: []                 children: []        touches: []
acceptance: [{id: a1, cmd: ..., expect: ..., altitude: machine|judge|human}]   # EXECUTABLE; linted before dispatch;
                               # `altitude` (intuitmachine ladder, batch 12) says where the verifier STOPS: machine = the
                               # gate/acceptance script proves it · judge = the checker/QA seat judges it · human = a person
                               # must confirm — an item with any `human` criterion REQUIRES a spec lock regardless of class
impact_metric: {name: ..., read_cmd: ..., window: ...}   # REQUIRED for medium/large or YELLOW/RED (→ measure)
budget: {rate_pct: ..., cost_m: ...}               known_bad_fixture: <path|null>
base_ref: <pinned sha>         branch_ref: sode/<id>|null      dispatch_ref: <sha the current stage started from>
stage: triage|spec|implement|review|verify|ship|measure|done|halted|cancelled    attempts: {<stage>: n}
                               # `halted` = attempts/rounds exhausted or breaker → released ONLY by a human
                               # `/sode release <id>` (with a reason) back to the failed stage; `done`/`cancelled` terminal
security_depth: D0|D1|D2|D3    # derived from class × lane × overlays (§4.3); may only be RAISED by hand
record_ref: record.yaml        monitor_hook: null
spec_hash: <sha256 of spec.md at lock>   acceptance_hash: <sha256 of acceptance[] at dispatch>   # review B14/E3
stack: {id: <parent-branch-stack id>|null, parent_ref: <branch>}   # stacked children, review B12
schema_version: 1
```

### 4.2 Work classes → required stages (the factory VOCABULARY)
| Class | Required stages | Spec form | Security | Human lock |
|---|---|---|---|---|
| trivial | implement → verify → ship | none; acceptance inline | D0 | none |
| small | spec → implement → review → verify → ship | inline in item.yaml | D1 | none |
| medium | spec → implement → review → verify → ship → measure | one `spec.md` | D1 floor; D2 on trigger (§4.3) | spec lock |
| large | decision record → spec → implement (children allowed) → review + pair review → verify → ship → measure | `spec.md` + PROGRAM-DESIGN artifacts (file-tree diff · call tree · type signatures) | D3 | spec lock + ship |
| architecture | research → decide → spec → then as large | `decision.md` (brainstorm/source homework + ADR) before any spec | D3 | decision + spec + ship |

Rules: **depth = max(class floor, lane, overlay)** — lane and overlay can only RAISE, never lower (review A3) ·
`security-sensitive` raises depth one grade · `irreversible` forces RED and NEVER self-ships · YELLOW or RED on ANY
class adds `measure` · the engine reads this table; it never asks a model whether a stage applies. **This table is
GENERATED from `platform/policy/classes.yaml`** — the single authority for class × lane × overlay → stages · depth ·
human locks; §4.3, §6.2 and C1 derive from the same file (review E1).
RED has two sources: hard-to-reverse blast radius, OR decision-class work needing homework first (operator).

### 4.3 Security depth (the security department's stage contract; department spec = §6)
| Depth | Applies to | Content |
|---|---|---|
| D0 scan | class floor for `trivial` (lane never LOWERS a floor) | automated tools only (secret scan · dependency pin+audit · SAST · supply-chain · license), fail-closed |
| D1 pass | class floor for `small` and `medium`; YELLOW raises to at least D1 | D0 + the checker runs a security pass against the security KB |
| D2 review | medium items whose `touches` hit secrets · auth · money · dependency manifests · runner/guard/adapter code (else medium = D1) | D1 + a dedicated security-reviewer worker, KB-armed, cross-family from implement |
| D3 audit | large; RED; anything touching secrets, money, auth | D2 + threat model + dependency review + adversarial review + human sign-off |
(Review C5, adopted: D2 is trigger-based for medium, not a blanket default.)

### 4.4 Labels = HOLDS only; queue state is derived from `stage` (review C9 — one source of truth)
`label` ∈ {null, `needs-info` (hold; at most one focused question), `blocked` (deterministic wait on `depends_on`),
`parked` (a hold without a permanent no), `cancelled` (terminal; record kept)}. "ready-to-spec / ready-to-implement /
in-review / done" are VIEWS computed from `stage` + `label == null`. `sode revert <id>` creates an expedited `small`
item carrying the revert (review B17).

### 4.5 Decomposition + deterministic scheduling
A spec worker that DISCOVERS a dependency writes a child item with `depends_on` and stops. From then on the
scheduler enforces the edge deterministically; no model is asked again whether the item is blocked. Every item
carries `outcome` (bind work to the observable, not just to internal coherence) and `parent` up to a goal item.
**Stacks (review B12):** children of a large item build on the PARENT branch (`stack.parent_ref`); when the parent
base moves the stack RESTACKS in order; cumulative acceptance runs at the stack tip. **Scheduling policy (review
B18):** `sode ready` is ordered by priority, then age; dispatch respects a WIP limit per department, a concurrency
cap per lane, and the subscription headroom as the global cap. **Path leases (review B16-lite):** `touches` globs
are RESERVED at dispatch; two items with overlapping reservations never run concurrently.

### 4.6 The brief is DERIVED, never hand-written
`render_brief(item, spec, stage_cfg) -> brief.md`: deterministic, paste-first, PROVIDER-NEUTRAL (port of the
dispatch-brief skeleton: WI blocks · constraints · scope fence · must-preserve-verbatim classes · orient · inputs
· executable acceptance · commit plan · HALT budget · report-back format · the CONTEXT WITHHOLD line · a RECITATION
block at the very END restating the task + acceptance ids, against goal drift in long loops — Manus, batch 11).
Then the ported acceptance lint runs; a lint FAIL blocks dispatch ([[poisoned_brief_acceptance_lint]]).
**Worker-facing CLI contract** (Anthropic "writing tools for agents", batch 9): every command a worker can call
(`sode-sh`, `sode gate`, `sode lint`, `sode-run`) is quiet on success, returns an ACTIONABLE error with its
remediation on failure, uses namespaced unambiguous verbs, and caps output size.

### 4.7 Post-ship measurement (`measure`)
Spec lock FAILS for medium/large or YELLOW/RED without `impact_metric`. For refactor / maintainability items the
DEFAULT `impact_metric` is the code-quality metric (complexity + LOC delta on the touched files) — always readable,
so no exemption exists (review C4). The engine captures the BASELINE during `verify` (a ship prerequisite) and
re-reads after `window` through `sode-run`. Verdict `valuable / neutral / excessive` is written on the item; `excessive`
opens a follow-up item to simplify or remove. Verdicts feed the self-evolving loop (§7) and the metrics (§9).

### 4.8 Spec-lock surfacing contract (operator 2026-09-17)
A human spec lock (medium+) is requested ONLY through a `spec_lock_brief` the spec worker fills from a fixed
template, posted in chat (and on the PR in `standard`): (1) TL;DR in <=3 lines · (2) ELI5 of the key points ·
(3) the building blocks added or changed · (4) what it impacts (files · metrics · other items · users) · (5) why
this solution is the best and most ELEGANT one, with each rejected alternative in one line · (6) executable
acceptance · (7) the impact metric. A brief missing any of the seven cannot request a lock (renderer refuses).
The lock PINS `spec_hash`; any later change to `spec.md` returns the item to the spec stage for re-lock (review B14).
A human lock is a hash-bound command (`/sode approve spec <hash>`), never a free-form comment (§5.1).

### 4.9 Trade-off accepted
More files per item than one backlog YAML, in exchange for the record travelling with the diff, clean merges,
and offline standalone operation.

## 4A. Departments — LOCKED (operator 2026-09-17)
A department = a plugin directory `platform/departments/<name>/` with SIX parts (`conventions.md` added 2026-09-18): `kb/` (dedicated knowledge
base) · `roles/` (agent role prompts = SEATS, §3.7) · `tools.yaml` (tooling registry) · `fixtures/` (its own
ratchet) · `review_checklist.md`. Stage bodies route to a department through `routing.yaml` (by `touches` glob
+ class); a department owns the review checklist and the KB its workers are primed with.

| Department | Owns | v1 |
|---|---|---|
| backend | services · APIs · engines · data access | v1 |
| security | the D0–D3 depth stack (§4.3) · security KB (patterns, CVE classes, lessons) · tooling (secret scan · dep pin+audit · SAST · supply-chain · license) · its ratchet (every finding -> rule/fixture) | v1 |
| frontend | UI · UX quality · accessibility | v1 (seeded from operator sources) |
| qa_quality | app + UI quality · code-quality review · cleaning · refactoring · optimization · the LEAN bar | v1 |
| devops | CI/CD · environments · deploy · runtime hosts · `monitor` (later) | v1 |
| architecture | decision records · the `architecture` class homework · design KB · the elegance bar | v1 (decision-record template + design sources) |
| data | pipelines · storage · tapes · schemas · retention | later (paper engine) |
| factory_ops | sode maintaining sode: evals · metrics · self-evolving loop · cost · adapters · upgrades of third-party tools | v1 |
factory_ops exists from day one: ~25% of all work is harness upkeep (Yegge datum) and it needs an owner.

**Curation at birth — LOCKED (operator 2026-09-18): SEVEN departments exist AND carry a curated KB before real
work routes to them.** security · qa_quality · factory_ops are seeded from our own proven material (guard rules,
pre-flight discipline, the ten QA angles, the lean bar, the cost model, harness lessons); backend · frontend · devops
are seeded from OPERATOR-BROUGHT articles and best practices ([[operator_brings_sources_advisor_evaluates]]);
architecture is seeded with the decision-record template + design sources. `data` stays later (with the paper
engine). The distinction that matters is SOURCED vs FABRICATED knowledge: a model never writes "best practices" from
memory into a KB; every entry names its source.

**`kb_ready` gate (deterministic).** A department is `kb_ready: true` only when its KB covers EVERY angle of its
`review_checklist.md` with >= 1 sourced entry AND has a `conventions` section. Routing an item to a department that
is not ready HOLDS the item (`needs-info`, reason "department KB not ready"). Real work cannot start on an empty
shelf. The check compares checklist angle tags with KB entry tags — no judgment call.

**KB entry shape** (`platform/departments/<d>/kb/<slug>.yaml`):
```yaml
id: <slug>                title: <one line>
claim: <the practice / rule / lesson, one paragraph>
evidence_type: external_practice | our_convention | run_lesson     # visibly separate layers
source: {url|path, author, date}          # REQUIRED for external_practice; item/run ids for run_lesson; operator for our_convention
applies_when: <scope>     does_not_apply_when: <anti-scope>
serves: [<checklist angle ids>, <routing patterns>]                # what this entry is FOR
reviewed_on: <ISO date>   owner: <seat>   source_hash: <sha>   schema_version: 1
```

**Seeding process (ONE process, reused from the librarian pipeline):** operator posts sources → a distillation
worker (Sonnet-tier is enough) digests each with citations → the security department scans the sources → the
department owner or the operator reviews → entries land with evidence refs. A source not fully read is recorded as
PARTIAL, never silently dropped. Seeding sessions run in W1–W2 in parallel with the code build, one per department,
each a backlog item whose acceptance is `kb_ready` flipping true (build plan §3 B018).

**Self-learning over time (operator 2026-09-18: "surface gaps if present and close them on the go").** Seeded
external practice is generic until real items add `run_lesson` entries; the experience bank + the ratchet fill that
layer continuously; the entry shape keeps the layers visibly separate. A GAP is surfaced, never hidden: a checklist
angle with no entry, a routing pattern with no owner, a stale entry past threshold, a worker `confusion` on a topic
with no KB coverage — each opens a factory_ops item automatically (the weekly `sode drift` sweep + the experience-
bank job). **Freshness (review D6/E9):** every KB entry, seat memory and checklist carries `reviewed_on` + a source
hash; the brief renderer marks stale slices; `routing.yaml` fails the gate on an unowned path and states overlap
precedence (primary + consulted).

## 5. Context-capture record — LOCKED (operator 2026-09-17, option 1)

### 5.1 Principle — one source, many views
`work/<id>/events.jsonl` (append-only) + the stage artifact manifests are the SOURCE; `work/<id>/record.yaml` is the
committed CANONICAL VIEW for humans and tools, regenerated at every transition (hawk A2 wording fix). The GitHub PR
body is a second GENERATED view, upserted at every stage
transition (`standard` profile). Gate + checker verdicts post as check runs. Human PR comments are HARVESTED back
into `decisions[]` / `events[]` (one-way ingestion of human judgment); nobody edits YAML by hand. **Human decisions
are HASH-BOUND COMMANDS** (review B9): `/sode approve spec <hash>` · `/sode approve ship <hash>` · `/sode reject <id>`
· `/sode needs-info <question>`; only trusted actors (`platform/policy/actors.yaml`); a decision binds to the artifact
hash it approved and is INVALIDATED when that artifact changes. Free-form comments are harvested as notes, never as
decisions. **`ship_hash` (hawk A5) = sha256(post_rebase_base_sha ‖ diff_sha ‖ record_yaml_sha ‖ gate_json_sha ‖
checker_verdict_sha)**; `/sode approve ship <ship_hash>`; any constituent change invalidates the approval (so a
rebase in the merge queue re-requests approval ONLY if the diff or verdicts changed). Same principle
as `backlog.yaml` → `BACKLOG.md`: generate, don't duplicate. Both Yegge (beads) and Warp (its own work-item
object) keep the record outside GitHub and use GitHub only as the PR surface (Appendix A).

### 5.2 The record is a deterministic PROJECTION, captured by hooks — never a recap
Rebuilt by the engine at every stage transition from that stage's EXIT artifacts:
```yaml
item: <id>
intent:         {outcome, why, acceptance_ids[]}                       # from item + spec
context:        {base_ref, spec_ref, decision_ref, inputs_read[], withheld[], stage_configs{}}   # from the brief
decisions:      [{stage, by: human|worker|engine, what, why, alternatives_rejected[], ref}]      # spec-lock + worker block + PR comments
implementation: {commits[], files_touched[], loc_delta, complexity_delta}                        # from git + QA tools
proof:          {gate: {verdict, ref}, acceptance: [{id, cmd, result}], checker_evidence[],
                 security: {depth, findings[], verdict}, measure: {baseline, after, verdict}}     # from verify/review/measure
worker_report:  {did, did_not, decisions[], concerns[], assumptions[], rejected_paths[], suggested_followups[],
                 confusions[], tool_failures[]}                         # handoff payload (review D2) + AutoQA channel
cost:           {rate_pct, cost_m, per_stage{}}                        # from adapter usage
narrative:      <literate summary generated at ship: background → intuition → what changed → how it is proven>  # Litt, batch 5
harness_card:   <hash of the HarnessCard the run used (§7.3)>          # attribution: which harness produced this
events:         [projection of work/<id>/events.jsonl — the append-only SOURCE; everything else is REWRITTEN per stage]
```
Two capture hooks: (1) the engine TRANSITION hook writes the stage sections; (2) the adapter STOP hook harvests
the worker's report-back block + usage. **Redaction runs BEFORE every write** (record · events · PR body · shim log ·
trajectory · checker prompt): patterns from the secrets registry + entropy heuristics; a positive-secret fixture proves
absence under git AND `.sode/` (review B5). A worker that returns WITHOUT the report-back block is classified
PARTIAL, never COMPLETE (the block is part of the brief contract, §4.6).

### 5.3 Gate — two completeness levels (review A2)
`record_complete_for_ship` (checked at `ship`: intent · context · decisions · implementation · proof.gate/acceptance/
checker/security · baseline captured) and `record_complete_after_measure` (checked when `measure` closes). `ship`
REFUSES if any ship-level section required by the item's class is empty (e.g. an acceptance
id with no proof; a medium item with no `decisions[]` by a human; a D2+ item with no security verdict).

### 5.4 Freshness
The record is REWRITTEN per stage so it stays short and current (Cursor "rewrite scratchpads, don't append");
only `events[]` appends. Full transcripts are NOT the record — they are trajectories (§7), stored as evidence.

### 5.5 Trade-off accepted
Workers carry a fixed report-back block (a few hundred output tokens per stage) and the factory maintains one
renderer + one PR upserter, in exchange for review that VERIFIES instead of reconstructs and a record that works
offline in a standalone clone.

## 6. Verification + review — LOCKED (operator 2026-09-17)

### 6.1 Composition — cheapest first, then CONCURRENT
Per ship attempt: the deterministic gate (T1 full), the QA review and the security review all consume the same
diff and run IN PARALLEL; wall time = the slowest, never the sum. The checker receives the T0 (commit-time) gate
result + the last T1 result if any; T1 runs concurrently (review A5). The review↔fix loop is BOUNDED:
`max_review_rounds` per item, findings carry ids, a re-check covers only addressed findings, stale findings are
invalidated when the diff changes (review B13). **Fan-out completeness (batch 15):** the three legs (gate · QA ·
security) are MANDATORY; a leg that dies or times out is recorded as UNKNOWN and NAMED in the record, and the merge
gate refuses — a missing leg is never a silent pass. A T0 gate runs at every commit, scoped to
touched files (<60 s). Review findings go to a DECOUPLED fixer worker (never the author's session); after a fix,
gate + reviews re-run. The merge gate combines verdicts deterministically.

### 6.2 Review matrix (human touches ARCHITECTURE / DESIGN / STRUCTURE, never code)
| Class | Deterministic | Model review | Human |
|---|---|---|---|
| trivial | gate | none | none |
| small | gate | ONE checker call: QA checklist + D1 security folded into the same prompt | none |
| medium | gate | QA seat + security by `policy.security_depth(item)` (D1 folded into the checker; D2+ = dedicated seat) in parallel; fixer on findings | spec lock only |
| large | gate + cumulative pre-flight | QA + security D3 audit | decision + spec lock; ship sign-off |
| architecture | as large | as large | decision · spec · ship |

**The ONE human-review rule (review A4; §2.1 and §8.6 point here):** PRE-shadow, a human approves every YELLOW
ship (hash-bound command) while machine-vs-human agreement is recorded in `.sode/shadow.jsonl`. POST-shadow, YELLOW
auto-ships. The switch flips per class × department when: n >= 50 decisions, Wilson upper bound of disagreement
< 2%, canary fresh (< 7 days), and no model/prompt/adapter change since the window started (a change RESETS the
window) (review B11). Thereafter the human audits a 10% sample FROM THEIR RECORDS. Medium+ spec locks and
`architecture` decisions are human at ALL times. RED and `irreversible` never self-ship. The model's self-assessment
is the input weighted LEAST.

### 6.3 The gate — `sode gate --t0|--t1` (PORT of the gates_runner SHAPE; sode-native checks)
- Check registry · one REMEDIATION string per check (an error is the next instruction) · exit 0 PASS / 1 FAIL /
  2 ADVISORY · `--json` for the engine. Content-hash CACHE: an unchanged check on unchanged inputs never re-runs.
- Checks (v1): tests · lint+format · type check · complexity budget (the LEAN bar) · secret scan · dependency
  pin+audit · license scan (= D0) · brief lint · acceptance script · record completeness · factory.yaml schema ·
  **anti-gaming** (operator 2026-09-18: code quality applies to ALL code — lean, senior-engineer style, solves the
  task not the test): no test deleted or weakened without an item that says why · no new skip markers · assertion
  count does not fall · acceptance `cmd`s untouched by the implementer · no `TODO`-shaped stubs where the spec
  demands behaviour.
- **Every deterministic command the ENGINE runs** (gate checks · acceptance `cmd` · `impact_metric.read_cmd` · setup
  hooks) executes through `sode-run`: env scrub · cwd fence · timeout · output cap · the same deny floor · no secrets
  by default (review B4).
- **Gate outcomes ledger** `.sode/gate_outcomes.jsonl`: every FAIL adjudicated TP/FP by a human or by the escape log;
  the per-check catch/FP metric reads from it (review E8).
- **Tracked metrics (operator):** T0 and T1 wall time (targets <60 s / <5 min) · per-check catch rate and false-
  positive rate (tune for SIGNAL, not count) · cache hit rate. A check whose FP rate exceeds its catch rate is a
  factory_ops item.
- **Determinism guard (h100envy, batch 11):** the gate run N times on a FROZEN state must return an identical
  verdict; a flaky check is fixed BEFORE it stays in the registry (a flaky gate breaks the stop condition of every
  unattended run). Part of the weekly drift sweep.
- **Ratchet (mandatory):** an escaped defect → known-bad fixture + gate extension BEFORE the next dispatch that
  could repeat it, or an explicit backlog row when the extension is not cheap; escape log with required refs. Each
  escape-log row is the FOUR-PART regression record (batch 25): the FIRST diverged step (root cause precedes the
  visible error) · the fault locus (model | tool | config | code) · a fix that does not hide another problem · the
  test that fails if it returns.

### 6.4 The checker (Deep-Reviewer) — an LLM judgment + a SCRIPT that enforces it
- LLM layer: PORT of `checker.md` — fresh context, sees ONLY {goal, acceptance ids, diff, gate result, touched
  paths, department checklist}; never the author's reasoning; PASS must cite evidence per acceptance id
  (criterion · file:line · counterexample tried · held-because); CROSS-FAMILY from the implementer by default.
- Script layer: PORT of `checker_verdict.py` — PASS without complete evidence → UNKNOWN; merge gate refuses
  FAIL / UNKNOWN / no-check; planted-bad canary corpus (schema: defect class · hidden/visible split · expected
  verdict), a miss auto-disables auto-ship. Canary CADENCE (review C10): on every adapter / model / checker-prompt
  change, weekly, and always before enabling auto-ship — not at every review.
- Pre-flight: before `ship`, the CUMULATIVE diff of the item branch vs its pinned `base_ref` is reviewed once as
  a whole (large items with children: the whole, not only each child).

### 6.5 QA review — THOROUGH, multi-angle (operator 2026-09-17); owned by `qa_quality`
The QA seat's checklist covers, per item: (1) correctness vs acceptance · (2) code quality: lean, readable,
idiomatic, no dead code, complexity delta · (3) SPEC quality: is the spec itself sound, complete, testable ·
(4) relevance to the OVERALL build: fits the architecture, no duplication of an existing component, no scope
creep · (5) tests: present, meaningful, cover the failure modes named in the spec · (6) maintainability: token
cost of the NEXT change, propagation of the change, dependency entropy · (7) refactor/cleanup opportunities
opened or left · (8) docs + record accuracy · (9) performance/efficiency where relevant · (10) anything the
department KB flags for this `touches` pattern. Findings are typed (blocking / should-fix / note); blocking
findings route to the fixer; the list itself is a ratcheted artifact (new escape class → new angle).

### 6.6 Security review — by depth, owned by `security` (§4.3)
D0 tools inside the gate · D1 a security pass inside the single checker prompt · D2 a dedicated security seat,
KB-armed, cross-family · D3 audit (threat model · dependency review · adversarial review · human sign-off).

### 6.7 Decision models (Sage / Jev class) — a `decision_model` adapter slot, EMPTY in v1
System-One decision models (typed closed-ended answers + calibrated confidence in 60–200 ms; no text, no
reasoning) CANNOT be the checker (no evidence, no file:line) but FIT the DECISION layer: triage proposals (class ·
lane · label · depth · department) · routing (review depth, model tier) · scorers over 100% of trajectories
instead of a sample · the actuarial auto-ship confidence from typed signals · pre-flagging diffs touching money /
auth / secrets before any LLM reads them. They are EXTERNAL APIs → security pre-flight + operator approval
([[no_external_api_local_only]]) + ZDR check (diffs leave the machine). **Bootstrap-backlog items (operator):**
one per use-site above, each with WHERE it plugs in, HOW it is tested (shadow vs the current path, agreement +
latency + cost measured), and its value add; plus the pre-flight item.

### 6.8 Trade-off accepted
A shadow phase costs human YELLOW approvals up front and the factory maintains a fixer role, in exchange for a
YELLOW lane that runs without a human on a MEASURED basis, and no self-grading anywhere.

## 7. Self-evolving loop — LOCKED (operator 2026-09-17, option 1: Run + Observe + Govern-store in v1; Evolve later)

**Re-scope adopted 2026-09-18 (review C1) — the DECISION stands, the TIMING splits:** v1 ships the IRREVERSIBLE part
only: the trajectory store (append-only, hash-chained) + `active.json` + promotions log + the eval golden-set SKELETON
+ the evaluator manifest. Scorers · `sode replay` · the experience-bank distillation land as v1.1 right after the WALK
milestone, when there is data to score. Nothing is lost: every trajectory from run one is kept.

### 7.1 Why the store cannot wait
A trajectory not captured from run one is lost forever; the automated learner can wait, its evidence cannot.
Operator requirement (2026-08-22): the factory learns from its own runs; governance per the CodeGraff rules.

### 7.2 Run
The lifecycle engine (§2) + workers (§3). Every stage run is a trajectory.

### 7.3 Observe
- **Trajectory store** `.sode/trajectories/<sha256>.json` — IMMUTABLE, hash-addressed, one per stage run,
  NEGATIVES included: `{item, stage, factory_def_version (git sha of factory.yaml+prompts+skills), provider,
  model, adapter, brief_hash, base_ref, tool_path_summary, cost{rate_pct,cost_m}, latency_s, terminal_outcome,
  gate_verdict, checker_verdict, scores{}, transcript_ref}`.
- **Scorers** (`factory.yaml scorers:`): dimensions task_compliance · procedure_compliance · verbosity ·
  efficiency · code_quality; LLM judge from a family the implementer did NOT use (judge-family bias is large);
  sampled (default 25%); a decision model (§6.7) may later raise coverage to 100%. The mutator never grades itself.
- **Eval set + replay**: real past items become reference tasks (`evals/tasks/`, immutable golden set + an
  APPEND-ONLY history sidecar — port of the `eval_runner` shape); `sode replay <item|trajectory> --config
  <variant>` re-runs an item at its INITIAL state (pinned base_ref + derived brief + stage config = the replay
  key) under a variant factory definition. A HIDDEN holdout is spent on WINNERS only.
- **HarnessCard per run + a system card (He et al. 2026, batch 13; this repo's `harness_card.md`):** every trajectory
  carries the hash of the 8-field HarnessCard the run used — base model · control artifacts (prompt/skill/checklist
  versions) · runtime policy (budgets, timeouts, permission mode) · action substrate (adapter, tools) · execution
  topology (stage, department, seat) · feedback stack (gate set, checker, depth) · governance (profile, lane) ·
  evaluation protocol. Generated deterministically from `factory.yaml` + `active.json` (`sode harness-card`). "Many
  reported agent gains are harness-sensitive, not model-driven" — without the card no cost/quality delta can be
  attributed. The SYSTEM card = the current standing config, regenerated at every promotion.
- **Experience bank** (operator req-8, MemoHarness shape): per-run diagnoses labelled by failure dimension (from
  scorers + `worker_report.confusions/tool_failures`) → periodically DISTILLED into department KB entries + seat
  memory (a factory_ops item; each distilled pattern carries its evidence refs) → RETRIEVED at task time by the
  brief renderer (department KB priming). Learning can substitute for scale (CodeGraff datum).

### 7.4 Govern (v1)
- **Mutation boundary**: the ONLY mutable surface = `factory.yaml` + prompts + skills + department checklists.
  The evaluator (gate registry · eval set · holdout · scorer rubrics · canary corpus) is HASH-PINNED in
  `platform/evaluator/MANIFEST.yaml` (review E6) outside it; a change there is an `architecture`-class item, never a
  learner output — and the L1 guard DENIES a non-architecture worker writing under `evals/`, `platform/gate/registry`,
  rubrics or the holdout (review F3). Promote/rollback carries failure-injection tests (partial write · bad pointer).
- **Single activation pointer** `.sode/active.json` → the live factory-definition version; promotion and
  rollback are the SAME atomic operation (immutable promotions log alongside).
- **Conservative selection**: correctness VETOES economy (lexicographic); a cheaper failure never beats a
  correct incumbent; refuse-to-judge when variants are not distinct.
- **Frozen twin baseline**: any learning claim is measured against the same system with learning OFF, as a
  SEQUENCE on success-per-dollar, never a snapshot.
- **Humans merge every factory-definition change in v1** (Warp: nothing adopted on its own); each change is a
  work item with `impact_metric` → `measure` (§4.7).

### 7.5 Evolve (LATER — unlocks when trajectories >= ~50 per stage AND a hidden holdout exists)
A proposer groups scored failures → changes ONE bounded surface → tournament on identical cases/seeds/model/
budget vs the incumbent → opens a PR carrying scorer context · failed runs · evidence · expected effect →
human merge (until auto-promotion is itself earned) → `measure` after merge. Anti-patterns encoded: don't pile
on addendums; remove outdated guidance. A MAP-Elites-style archive keeps varied lineages. Model optionality is
PROVEN here: a provider switch must not regress the eval set (hwchase17: owned traces + owned evals = the moat).

### 7.6 Trade-off accepted
No automated learning in v1, in exchange for a complete, trustworthy evidence base and zero reward-gaming risk
before the evaluator has proven itself.

## 8. Guards + safety + human-in-loop — LOCKED (operator 2026-09-18, option 1)

### 8.1 Three guard layers (deny KEEPS, ask PRUNES; autonomy grows by pruning ASK on evidence, never by
weakening DENY)
- **Actor scoping (hawk A10):** every rule carries `applies_to: [worker, engine]`; worker-only denies (publish ·
  PR merge · push outside `sode/<id>`) never bind the engine's own `ship` stage, while profile + protected-branch
  rules bind both. `sode-run --actor engine|worker --stage <s>` selects the rule view. Worker PATH rules (hawk A11):
  a worker may write ONLY inside its clone and, within `work/<id>/`, only the outputs its stage owns (spec stage →
  `spec.md`/`decision.md`/child-item creation via `sode new --child`); `item.yaml` · `brief.md` · `record.yaml` ·
  `events.jsonl` · every other `work/**` path are engine-owned and denied.
- **L1 DENY floor** — PORT of `destructive_guard.py` + the 34-rule deny set from this machine, verbatim (git
  disasters · recursive delete · sudo/shutdown · secret-file reads · audit-log writes · protected-system-path
  confinement · pipe-to-shell). ADD worker-specific denies: publish/upload commands · PR merge · repo delete ·
  any push in `restricted`. Workers NEVER ship; the engine's `ship` stage does, under lane policy. Never
  overridable by any allow rule.
- **L2 ASK layer** — name · what-it-does · exact-command prompt (PORT of the `collector_ctl` pattern). Borrowed
  from the 27-rule ask set with three edits: (a) package installs ASK only for NEW dependencies — the pinned
  path (lockfile sync inside the clone, `sfw`-wrapped) is ALLOW; (b) an edit to a dependency manifest is not a
  prompt but a D2 security review item; (c) in `standard` a worker may push ONLY its own `sode/<item-id>` branch
  (branch-name rule in the shim). Unattended: an ASK = `needs-info` hold + notification; the queue keeps moving.
  Never auto-allow.
- **L3 POLICY fence** — lane × class × profile decides what may self-ship, push, spend; the budget breaker (§9)
  lives here; the review-backlog governor (§8.3) lives here; `platform/policy/git.yaml` (remotes · refspecs ·
  identity · signing · protected branches) lives here (review B6).
- **Rule provenance (review E5):** every deny/ask rule has an id · source ref · threat class · example; the deny set
  is monotone (test); an ASK-rule removal must cite an item id carrying holds evidence (gate) — the ask-prune ledger.
- **Guard-enforcement proof matrix (review F1):** per adapter, transcript-level tests prove a worker cannot run raw
  shell or reach a provider-native tool that bypasses the shim; deployed-shim/hook drift is a doctor check.
- **Enforcement coverage registry (Fowler + He et al., batches 2/13; this repo's `enforcement_coverage_registry`):**
  every guard rule, gate check, rubric, checklist and hook is tagged on CAR (Control · Agency · Runtime) × {guide |
  sensor} × {computational | inferential}; `sode drift` renders the grid and surfaces THIN cells (expected sparsest:
  inferential guides). Coverage is measured, not assumed.
- **Curate prompts and skills like memory (batch 25, skill-curator):** the drift sweep's scope includes department
  checklists, seat prompts and skills — merge overlap, remove stale, revise weak descriptions; an unbounded prompt
  directory becomes its own retrieval problem. Surface, never auto-merge.
- Allows are DERIVED from the stage config's tool allowlist (§3.3), not borrowed.

### 8.2 Enforcement point is PROVIDER-NEUTRAL — the `sode-sh` shim
Workers execute shell through `sode-sh`, which applies L1/L2 BEFORE exec on ANY provider (Codex has no
settings.json deny format). Vendor hooks (Claude Code PreToolUse etc.) are a SECOND layer where they exist.
Intercept at the boundary that matters (stencil), never by parsing prompts. Adapter installs both.

### 8.3 Human-in-loop primitives (four)
- **Steer** — message a live worker (adapter-mediated) or comment on the PR; both harvested into the record.
- **Notify** — one channel adapter (v1: CLI + GitHub; Slack later); every notification carries the item id, the
  stage, and the BLOCKED REASON.
- **Handoff** — `sode handoff <item>` pulls branch + record into the human's local inner loop; `sode resume
  <item>` pushes it back and re-enters the state machine. Tracks what happened · what remains · why.
- **Pause** — the review-backlog GOVERNOR stops dispatching new `implement` stages when items awaiting a human
  exceed a count or an age (pause production when review falls behind).

### 8.4 Arming by profile
- `standard`: automations enabled individually in `factory.yaml`; the global kill switch (`sode stop-all`) sends
  SIGTERM → SIGKILL to every worker process GROUP, freezes `active.json`, marks clones quarantined, and has a
  recovery test (review F2); the budget breaker caps spend.
- `restricted`: `allow_push=false`, `allow_self_fire=false` (§3.4) — the engine waits in place across windows and
  never installs a host scheduler entry. No GO-file port (review C8).

### 8.5 Compromise runbook (owned by `security` + `factory_ops`)
If the production process itself is compromised: (1) `sode stop-all` — every worker process group stops; (2) revoke every broker
token (1Password); (3) freeze `active.json`; (4) replay the audit trail from trajectories + records + the shim
log to find the entry point; (5) rotate secrets; (6) ratchet the entry point into an L1 rule + a fixture;
(7) resume from disk. The shim log + trajectories ARE the audit trail: append-only, HASH-CHAINED (each record carries
the previous hash), verified by `sode verify-log`, exercised by a compromise-runbook fixture (review F7).

### 8.6 Autonomy sufficiency (measured, not assumed)
What remains a hold by DESIGN: spec lock (medium+) · decision (architecture) · ship sign-off (RED). Everything
else runs: trivial/small with no human; YELLOW after the shadow phase (§6.2). Metric: `holds per 100 items`
(target <5); a hold that repeats with no real decision behind it = evidence to prune that ASK rule.

### 8.7 Trade-off accepted
Unattended runs hold on ASK events instead of proceeding, in exchange for no irreversible act ever happening
without a human reading its name, what it does, and its command.

## 9. Cost + measurement — LOCKED (operator 2026-09-18)

### 9.1 Two currencies, one hard stop
- Every stage carries BOTH currencies (`budget: {rate_pct, cost_m}`); item budget = sum of its stages.
- **The ONE hard-stop signal = the subscription window**: 5h and 7d headroom minus a reserve margin
  (`factory.yaml reserve_pct`). Below the margin the engine WAITS for the refresh. **How headroom is read (verified
  2026-09-18):** CODEX — every session rollout under `~/.codex/sessions/` carries `rate_limits{primary{used_percent,
  window_minutes:300, resets_at}, secondary{…10080…}}`: exact, local, no API. CLAUDE — no such record exists (neither
  CLI exposes a usage verb), so sode PORTS this repo's approach: parse transcript `usage` fields → the ERA-SCOPED rate
  model (output + fable cache-create weights) → calibrated against operator UI% samples (`sode headroom calibrate
  --ui-pct N`). Fallback chain (review B10): exact read → estimate + fresh calibration sample → estimate alone with
  the reserve WIDENED → hold + notify when the estimate is stale beyond `headroom_stale_s`. Never a permanent stall,
  never percentage arithmetic on the COST metric.
- **Money is COMPUTED per item** (billable-equivalent from adapter usage) for optimisation + reporting; it is
  NEVER a threshold while providers are subscription-billed. When an API-billed adapter is added, its
  `billing: api` flips the binding currency for that stage to COST.

### 9.2 Two flat stop rules (replaces the multi-window dynamic breaker — too complex for sode)
- **Per stage**: the worker HALTS at 1.5× its stage cap (brief instruction); the engine KILLS at 2× from adapter
  usage (independent of the worker's self-report).
- **Per item**: the engine stops dispatching the next stage when item spend passes the item cap → `needs-info`
  hold with the numbers.

### 9.3 Fermi = a RECORDED prediction (operator: Fermi has not been reliable)
Every stage cap is written to an APPEND-ONLY prediction ledger `.sode/predictions.jsonl`: `{item, stage, class,
department, model, predicted, actual, ratio, ts}`. Prediction accuracy is itself a metric. Once a class ×
department × stage cell has >=10 samples, the cap = the empirical p80 of past actuals and the hand estimate is
RETIRED for that cell. Data replaces guessing as soon as data exists.

### 9.4 Cache engineering
The brief renderer emits the STABLE prefix first (department KB · constraints · checklist · report-back format)
and the volatile item last; cache-hit rate is MEASURED per adapter (a metric, not an acceptance target — review C7);
brief SIZE budgets are the acceptance target. All timestamps UTC; durations monotonic (one clock library, review B20). Any efficiency experiment holds ONE model
fixed and runs through `sode replay` (Uber rule). Cost + efficiency control is a standing factory_ops duty.

### 9.5 The metric REGISTRY — `metrics/registry.yaml` (record · attribute · alert · gate)
```yaml
- id: <snake_id>            group: <one of the 8 groups>
  definition: <formula over NAMED record / trajectory / ledger fields>
  unit: <unit>              direction: lower_is_better | higher_is_better
  drivers: [<what moves it>]
  measures: [<item ids of changes made to improve it>]
  owner: <department>       baseline: {value, window, set_on}
  alert: {rule: "worse than baseline 3 consecutive windows OR >20% degradation", opens: factory_ops item}
```
- **Record**: every metric is computed per window by `sode metrics` (local reads only) and STORED, not only shown.
- **Attribute**: a shipped item's `measure` verdict (§4.7) writes its impact onto the metrics it named; the
  metric history carries the item id at that change point → changes are attributed to metric movements.
- **Alert**: the alert rule runs as an automation; a decline opens a factory_ops item with the trend attached
  (catch drift early).
- **Gate**: a metric enters the registry ONLY with a formula + drivers + owner. No formula, no metric. Every
  metric must matter to system results.

### 9.6 Metric groups (SEED list; each group = a dedicated bootstrap-backlog discussion that fixes precise
definitions, drivers, measures, baselines, alert rules). **Bootstrap seeds the registry with FIVE hard metrics** (review
C3): lead time intake→ship · first-pass gate rate · re-dispatch rate · escapes past gates · provider headroom; the group
discussions add the rest. Every registry formula binds to NAMED schema fields; an unknown field = gate FAIL (review E12).
| Group | Seed metrics | Source |
|---|---|---|
| delivery_speed | lead time intake→ship · cycle time per stage · items shipped/week | `events[]` |
| defects | escapes past gates /100 items · reverts per class × worker config · reopen rate | records, git |
| cicd_efficiency | T0/T1 gate wall time · first-attempt pass rate · re-dispatch rate · attempts/item | gate JSON, ledger |
| code_quality | complexity delta/item · LOC delta/feature · dead-code findings · token cost of the NEXT change on the same files | QA tools, trajectories |
| cost_efficiency | cost per shipped item (both currencies) · shipped items / tokens · prediction accuracy · cache-hit rate | adapter usage, prediction ledger |
| autonomy | automation % (zero human touches) · holds /100 items · review latency · checker-vs-human agreement | records, labels |
| security | findings/item by depth · time-to-fix · D0 tool catch rate | security verdicts |
| learning | learning-loop gain vs frozen twin (success/$) · model-switch regression delta | evals, replay |

### 9.7 Trade-off accepted
Workers carry a HALT instruction and the engine reads usage per stage, in exchange for cost that is a recorded,
self-calibrating prediction and metrics that drive fixes instead of decorating a dashboard.

## 10. Open items for the follow-up (product-plane) session
(Backlog seeds now carry stable ids `B001…` in the build plan §3.)
(Plus the adversarial-review DEFER items: clone GC + portable run archives · container runner · issue mirror ·
Slack — see `docs/audits/sode_factory_spec_review_2026-09-18.md` §B19/D7.)
- Strategy-card schema (grade × type), the outward-export gate for cards, a mocked import test.
- Risk kernel: position/loss caps, kill switch, portfolio/allocation enforcement (synthesis §14.3).
- Re-validation loop on drift (synthesis §14.4), card versioning + rollback.
- Maintenance layer: the 7 stage-6 metrics, exhaustion verdict, inward measurement path.

---

## Appendix A — Source dispositions against locked decisions (2026-09-17)
Operator-supplied sources, read AFTER §1–§4A locked. Verdict per source: what it CONFIRMS · what it ADDS · where
it is in TENSION. Future design refers here.

**A.1 Yegge, "The shape of things to come" + "Model welfare" (2026-08/09).**
CONFIRMS: work state in the repo, not GitHub Issues (beads) · a clone per agent · design→implement→review
sandwich across model tiers · ~25% of work = harness upkeep (→ factory_ops) · crons watch, models act.
ADDS: seats vs sessions, handoff-not-exit, never-falsify-the-record (§3.7) · beads as a candidate item store
(§4.1a, DEFERRED: third-party tooling review = a later backlog item) · the brain/doc/beads/remember/skills
layering (§5 mapping). TENSION: megabatch "land the flock" merge at 175–250 commits/day vs our per-commit-green
— SCALE-DEPENDENT; per-commit-green stays at our rate (T2, already recorded) · "harnesses will be bespoke" vs a
reusable factory — resolved: platform reusable, product harness bonded (§3.7).

**A.2 Lloyd/Warp, "Adopting the software factory model: crawl, walk, run" (2026-09-15).**
CONFIRMS: the lifecycle triage→spec→implement→review→verify→ship→monitor (§2) · human gates = spec approval ·
clarification · merge (§4.4 labels + lanes) · start simple, one loop, one surface. ADDS: the crawl/walk/run
adoption path (§2.5) · the scale-bottleneck list (§2.5) · the "walk" question list — each mapped to a section:
where dev happens (§3.2/§3.4 runners) · success metrics (§9) · AI sovereignty / own the data / provider
dependence (§3.3 adapters + Appendix A.5 data ownership) · improvement process + cost control + "how do we know"
(§7 + §9 + `measure`) · future-proofing models + regulatory access risk (adapter interface; open-weight/self-
hosted adapter = later) · how engineers/designers/PMs participate (access layer, §8) · securing development +
**a plan if the production process is compromised** (§8: factory compromise runbook — NEW). TENSION: "cloud by
default, sandboxes over local" — sode v1 = local clone + guards (no external infra); container/remote runners are
the path (§3.3 `runners:`), not a rebuild.

**A.3 Lloyd/Warp, "The software factory stack" (2026-09-09).**
CONFIRMS: factory-as-code (`factory.yaml`, §3.3) · open/composable/defined-in-code · multi-model + multi-harness
(§3.3) · own all data, ZDR. ADDS to `factory.yaml`: `runners:` · `automations:` (triggers→actions) ·
`integrations:` · `scorers:` (§3.3, folded) · REPLAY (re-run real factory work at its exact initial state to test
a config change — feasible for us: pinned `base_ref` + derived brief + stage config = the replay key; § 7) ·
benchmarking = reference-task suites × config matrix (§7) · a control-room view (§8, `sode status`).

**A.4 Warp, "Engineering / agent self-improving software factories" + docs "How factories work".**
CONFIRMS the §7 plan: Observe (scorers = LLM-judge over sampled traces, default 25%, dimensions task/procedure
compliance · verbosity · efficiency · code quality) → group failures → a self-improvement agent proposes DIFFS TO
THE FACTORY DEFINITION as PRs → humans merge; "nothing is adopted on its own". ADDS: every proposal carries
scorer context + failed runs + evidence + expected effect (= our `measure` contract applied to factory changes) ·
the anti-patterns "don't pile on addendums; remove outdated guidance" · Warp keeps its OWN work-item object and
uses GitHub only as the PR surface — same shape as §4.1/§5 (record in our store, PR as view). Datums: ~300
PRs/week; >10 self-improvement PRs in days; 96% efficiency pass in the example. TENSION: Warp's review verdict is
ADVISORY (human merges); ours is evidence-required with GREEN auto-ship — stricter, and matches the
blast-radius-first graduated-autonomy resolution; keep.

**A.6 growth-hack-system distilled batches 8–25 (re-checked 2026-09-18 against the spec).** The System-Efficiency
bucket (`docs/references/system_efficiency_bucket.md`) + the design-session backlog notes (batches 15–23) + batch 25
were swept. Already in the spec: two currencies · cache discipline · maker-checker with evidence · canary · ratchet ·
clone isolation · GO/arming · worker tiering · frozen-twin/CodeGraff governance · MemoHarness experience bank ·
decision ledger · blast-radius lanes · judge-family bias · spec-as-primary-artifact · graduated actuarial autonomy ·
retrieval-at-stage (KB `applies_when` + `serves`). FOLDED 2026-09-18 (net-new to the spec): oracle by commit
TRAILERS not count (§3.5) · isolation ladder + brain-outside-the-box (§3.2) · 40–60% context + compact-into-record ·
`failure_class` + fed-forward `rejected_paths` (§3.5) · acceptance `altitude` (§4.1) · recitation block + worker-facing
CLI contract (§4.6) · `narrative` + `harness_card` on the record (§5.2) · fan-out completeness = missing leg is UNKNOWN
(§6.1) · gate determinism guard + four-part escape record (§6.3) · HarnessCard per run + system card (§7.3) · CAR ×
2×2 enforcement coverage grid + prompt/skill curation in the drift sweep (§8). SEEDED as backlog (build plan §3):
ponytail minimal-code agent eval · Meta-Harness/harness-evolver as the Evolve reference · a semantic-escape design
session ("what semantic error passes ALL gates" — rule-of-five perspective-diverse review) · OS-jail / isolation-
ladder eval for the runner. NOT adopted: agency × orchestration axes (a lens, not a mechanism) · KV-compression research
(assessed non-adoptable here, same verdict).

**A.5 Data ownership (from A.2/A.3, adopted as a principle).** All traces, records, usage and evals are stored
in the repo or under `.sode/` on the operator's machines; no provider trains on them (ZDR where the provider
offers it); the improvement loop reads local files, never a vendor API.

---

## Appendix B — Apply-check: one real work item walked end to end (agenda 11, 2026-09-18)

**The item (real, from the build plan's own dogfood queue):** *"`sode gate --json` reports per-check catch and
false-positive rates from the gate-outcomes ledger."* factory_ops · touches `platform/gate/` + `.sode/gate_outcomes.jsonl`
reader · class **medium** (one spec doc, a human spec lock) · lane **YELLOW** (reversible, wide: every gate run changes
shape) · overlays none · depth = max(medium→D1, YELLOW→D1, none) = **D1**. Walked against §1–§9 + C0–C15 as amended.
Every step names the component that closes it; every place the spec does NOT close is marked **GAP** and filed.

| # | Step | What happens | Closed by | Record / guards / cost |
|---|---|---|---|---|
| 1 | intake | operator: `sode new "gate --json reports per-check catch/FP" --outcome cicd_efficiency.gate_signal` | C1 | `work/<id>/item.yaml` created, `schema_version: 1`, `events.jsonl` gets `created`; prediction row #1 opened with the hand cap for `spec` |
| 2 | triage | factory PROPOSES class=medium · lane=YELLOW · dept=factory_ops (routing: `platform/gate/**` → factory_ops primary, qa_quality consulted) · depth=D1; human ratifies (or a decision model later, §6.7) | C1 routing + `classes.yaml` | `decisions[]` += {by: human, what: class/lane}; `label == null`, stage=spec → the item is `ready-to-spec` (derived) |
| 3 | kb_ready check | factory_ops KB must be `kb_ready` (seeded in W1–W2); else the item HOLDS `needs-info` "department KB not ready" | C9 | hold recorded in `events.jsonl` |
| 4 | spec | engine tick → `PendingAction{action_id=h(id,spec,1)}` claimed in `.sode/actions.jsonl` → provision clone at `base_ref` (hardlinks, scrubbed env) → `target.setup` via `sode-run` → brief rendered (`sode brief <id> spec`: factory_ops KB slice + QA checklist + constraints first; item last) → `sode lint` passes → spec worker (anthropic_cli, plan_only) writes `spec.md`: intent · executable acceptance (`sode gate --json` contains `checks[].catch_rate`, `fp_rate`, `n_adjudicated`; fixture ledger → hand-computed values) · touches · `impact_metric: {name: gate_first_pass_rate_noise, read_cmd: "sode metrics --id cicd.first_pass_gate_rate --json", window: 14d}` | C2 · C3 · C5 · C4 | worker shell = `sode-sh`; secrets: none; watchdog armed; stop hook harvests report-back; redaction runs; trajectory written (hash-chained); prediction row filled with actual |
| 5 | spec lock | renderer emits the seven-part `spec_lock_brief` in chat + PR; operator replies `/sode approve spec <sha256(spec.md)>` | C5 · C6 | `spec_hash` pinned; `decisions[]` += hash-bound approval by a trusted actor; label stays null, stage=implement |
| 6 | implement | new action_id; fresh clone per stage at `branch_ref` (GAP-1 decided); brief from spec; implement worker (anthropic_cli, edit_in_clone) codes + tests; commits on `sode/<id>`; T0 gate at each commit via `sode-run` (<60 s; anti-gaming checks: no test removed, assertions non-decreasing); worker returns report-back (did · did_not · decisions · concerns · confusions) | C3 · C7a · C5 | shim denies anything outside the clone; push allowed to `sode/<id>` only (git.yaml); cost: HALT at 1.5× stage cap (brief) / KILL at 2× (engine) |
| 7 | classify | on exit: `classify_dispatch_state(clone, base_ref, acceptance_hash, phase_id)` (clean tree · required acceptance · commit trailers) → COMPLETE (or PARTIAL → continuation with RESUME preamble, attempt 2) | C2 | ledger update (leased, atomic) |
| 8 | review ∥ verify | IN PARALLEL on the same diff: (a) T1 full gate via `sode-run` (tests · lint · types · complexity · secret scan · deps · license · brief lint · acceptance script · record-for-ship completeness); (b) ONE checker call (openai_cli — cross-family; QA ten angles + D1 security pass folded in; input = T0 result + last T1 if any) → PASS must cite evidence per acceptance id, else UNKNOWN; (c) baseline of `impact_metric` captured via `sode-run` (ship prerequisite) | C7a/C7b · C8 · C11 | findings with ids → fixer worker (decoupled; `max_review_rounds`); verdict + evidence into `proof`; canary not re-run (cadence: on change/weekly) |
| 9 | ship (merge queue) | YELLOW pre-shadow → operator `/sode approve ship <diff-hash>` (post-shadow: auto when n≥50 · Wilson<2% · canary<7d · no config change) → `merge_queue.next()`: rebase onto current main → re-run T1 + checker on the post-rebase diff (conflict → conflict-fixer → full re-verify) → merge via GitHub (standard) or local merge + tag (restricted) → `record_complete_for_ship` PASS → PR body upserted from record | C10 · C6 | `events.jsonl` += `shipped`; clone torn down; cost totals per stage in `record.cost` |
| 10 | measure | automation fires after 14d: `sode-run` reads the metric → verdict vs baseline → `valuable / neutral / excessive` appended; `excessive` → follow-up item; metric history annotated with the item id → `record_complete_after_measure` | C11 · C14 · C15 | attribution: the change is now linked to the metric movement |
| 11 | learn | trajectories (spec · implement · review · fixer) stored; scorers sample them (v1.1); worker `confusions` with no KB coverage → `sode kb gaps` → factory_ops item; escaped defect (if any) → `sode ratchet` → fixture + gate extension | C13 · C9 · C7 | the self-learning layer fills `run_lesson` entries with evidence refs |

**Where the spec does not yet close (filed; none blocks the build):**
- **GAP-1 clone reuse across stages.** §3.5 provisions a clone per WORKER; the walk needs the SAME item branch across
  spec → implement → fixer. Decision needed at C3: one clone per ITEM reused across stages (cheaper, state carries) vs a
  fresh clone per stage from the item branch (cleaner). Recommendation: one clone per item, fresh clone only on a
  PARTIAL continuation after a kill. → DECIDED 2026-09-18 (hawk pass): a FRESH clone per STAGE from `branch_ref` — every stage starts from committed state; folded into §3.5/C3. Seed B023 records the decision.
- **GAP-2 the `spec` worker's clone.** A plan-only stage needs read access but no branch; §3.5 always creates a branch.
  Closure: `permission: plan_only` stages provision a READ-ONLY clone (no branch, no push). → C3 note.
- **GAP-3 who runs the T1 gate.** §6.1 says "the factory"; the walk shows it runs INSIDE the item clone (needs the
  worker's toolchain). Closure: T1 runs in the clone through `sode-run`, engine-owned, after the worker exits. → C7a.
- **GAP-4 pre-shadow YELLOW approval surface.** The operator approves ship with a hash of WHAT — the diff, the record,
  or both? Closure: hash of `(diff sha, record.yaml sha)`; either changing invalidates the approval. → C6.
- **GAP-5 `impact_metric` window vs the `measure` automation.** The automation needs the item's `window` end time
  persisted where the scheduler can see it. Closure: `.sode/measure_queue.jsonl` written at ship. → C11/C15.
- **GAP-6 first-run bootstrap of the gate-outcomes ledger.** The item's own acceptance reads a ledger that is empty on
  day one → `n_adjudicated: 0`, rates null, not zero. Closure: null-safe rates + a seeded fixture ledger in the spec.
  (An example of the anti-gaming rule working: the spec, not the test, decides the empty case.)
- **GAP-7 intake for non-operator sources.** The walk started from a CLI command; a monitor signal or a PR comment as
  intake is C15 territory but the triage PROPOSAL prompt is unspecified. → C1/C15: `triage` stage body = a small-class
  worker call (or a decision model, §6.7) with a fixed output schema {class, lane, dept, depth, one question|null}.

**Verdict.** The item walks intake → ship → measure → learn with every step owned by a named component and every
artifact, guard and cost read named. Seven closures are small and filed; none re-opens a locked decision. The spec is
walkable; the build can be dispatched.

## NEXT ACTION
Build **C0** (W1-1 brief stub, build plan §4) in a fresh `../sode-factory/` repo, in parallel with the seven KB seeding
sessions (build plan §3 B018). Still open: the product-plane session (§10 / B005) · the
Codex adapter after the walk milestone · the eight metric-group discussions · the beads/tooling review after W3.
