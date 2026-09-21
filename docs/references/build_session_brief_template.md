# Build-session brief template (the skeleton every session brief is rendered from)

The build docs are the SOURCE, not the paste. A build session starts from ONE rendered brief: this skeleton
filled with the exact spec sections inlined. The brief is the whole prompt of a fresh session; nothing
load-bearing lives outside it. Until component C5 exists the advisor renders briefs by hand from this file;
after C5 the factory renders them. Rules the skeleton already obeys and a filled brief must keep: the file opens
at the first H1 task line with nothing above it; every acceptance is an executable command with an expected
result; every number names the command that derives it; the recitation block is the last section.

--- RENDER BELOW THIS LINE; replace every <…> ---

# sode-factory — <S-id> <session name> — build brief

You are a build agent working in the sode-factory repo at `<absolute path>` on branch `main` at tag/sha
`<entry tag>`. You build ONE component: <C-id> <component name>. You work alone on the main tree; nobody else
commits while you run. Per-commit-green: run the gate, read its output, then commit. Tag at the end. Read this
whole brief before you start.

## Goal
<one paragraph: what the component is for, from the architecture section it serves; the win condition>

## Read first (inlined below; the files are also in the repo)
- Architecture: <the §-sections this component realises — INLINE their text here>
- Component spec <C-id> — INLINE its four parts: Responsibility · Interface/contract · Acceptance · Failure modes
- Build plan row <n> · build sessions row <S-id> (entry state · exit acceptance · dependencies)
- <any policy tables the component derives from, e.g. classes.yaml rules, guard rule seed — INLINE the rows>

## Entry state
- Entry tag: `<tag>`; `make test` <green|not yet present>; `tests/test_standalone.py` <green|skeleton|absent>.
- Components already landed: <list>. Components NOT yet present that this one must not assume: <list>.

## Touches
<exact package paths this component owns, e.g. platform/<pkg>/, tests/<pkg>/, bin/…>

## Do not touch
Every other package under `platform/` · `docs/design/*` (the spec set is read-only for makers) · `factory.yaml`
schema fields outside this component's own · `memory/` · `backlog.yaml`. If you believe you must, STOP, write
the reason into your report-back, and finish what you can.

## Architecture decisions are closed
If the spec forces you to re-decide an architecture item, stop that part, record it under `concerns[]` in the
report-back, and continue with the rest. Do not choose for the operator.

## What to build (ordered)
1. <concrete step — exact files + the contract it must satisfy>
2. <…>

## Acceptance (executable; every line = command → expected)
```
make test                                   # → green
python3 -m pytest tests/<pkg> -q            # → <N> passed (derive N from the tests you write; report the count)
<component acceptance command 1>            # → <expected>
<component acceptance command 2>            # → <expected>
python3 -m pytest tests/test_standalone.py -q   # → green (skeleton form until S9)
```
Known-bad fixtures that MUST fail: <list>. Known-good that MUST pass: <list>.

## Quality bar (applies to all code)
Lean, senior-engineer style; solves the task, never the test; passes lint, types and the complexity budget; no
test deleted or weakened; no skip markers; one component per package; every check ships with a remediation
string and a known-bad fixture. <RED sessions: the full process-genesis kit — bar · deterministic checker ·
fixtures · pilot · risk table · run report.>

## Budget
Prediction row: `<S-id>` hand cap <n> (units: <rate_pct|cost_m>). Halt at 1.5× the cap and write a partial
report; the engine kills at 2×.

## Commit plan
One logical change per commit; subject `type(scope): description` ≤72 chars; body = why; no provider attribution
trailers. Final commit tags `<s-id>-<name>`.

## Report-back (write this file BEFORE your final message: `work/sessions/<S-id>/report.yaml`)
```yaml
did: [...]            did_not: [...]
decisions: [{what, why, alternatives_rejected}]
concerns: [...]       assumptions: [...]      rejected_paths: [...]      suggested_followups: [...]
confusions: [...]     tool_failures: [...]
acceptance_results: [{cmd, expected, actual, pass}]
cost: {tokens_or_pct: <as reported by your session>}
```

## Context withhold
<what this session must NOT read and why — e.g. a prior implementation, another repo's source — or "none">

## Recitation (read this last)
You are building <C-id> <component name> for session <S-id>. Done means: <the acceptance lines above pass>,
`make test` is green, the standalone test is green, the report-back file exists, and the tag `<s-id>-<name>`
is on the final commit. Stop and report rather than guess on any architecture question.
