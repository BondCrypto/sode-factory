---
name: current_state
description: "The single NOW anchor for sode advisor sessions — HEAD, status, what landed, the immediate next step, in-flight sessions, open operator decisions. Read first at every session open. Update at every wrap. Keep lean."
metadata:
  type: project
---

> Standing rule: this file records the LIVE position only. Landed work belongs in git and tags; durable lessons in
> topic memories; tasks in `backlog.yaml`. If you append a block, delete one.

### NOW (2026-09-21): SPEC LOCKED · REPO INITIATED · BUILD NOT STARTED

- **HEAD:** the initial commit set (spec set + backlog + CLAUDE.md + role prompt + memory). No code. No tags yet.
- **Status:** `docs/design/sode_factory_{architecture,component_specs,build_plan,build_sessions}.md` +
  `guard_rules_seed.yaml` + `docs/audits/sode_factory_spec_review_2026-09-18.md` are LOCKED (operator 2026-09-21).
- **Gate / standalone test:** do not exist until S1 lands.
- **Backlog:** 53 items — 21 code sessions (S1–S21), 7 KB seeding sessions (K1–K7), 25 seeds (B001–B025).

### IMMEDIATE NEXT
1. **S1 — C0 skeleton.** Render the brief from `docs/references/build_session_brief_template.md` + build plan §4
   W1-1 + component spec C0; dispatch to a fresh session (or run inline); verify; tag `s1-skeleton`.
2. **K1–K3 in parallel** (security · qa_quality · factory_ops KBs) from our own material; K4–K6 wait for
   operator-brought sources (backend · frontend · devops).

### IN-FLIGHT
none.

### OPEN OPERATOR DECISIONS
none. (Product-plane design session = seed B005; waits for a `paper_validated_card`.)
