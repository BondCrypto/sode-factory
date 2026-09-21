---
name: spec_is_the_constitution
description: "The locked spec set (architecture + component specs + build plan + sessions) is the constitution: a locked section changes only through an architecture-class work item + a decision record + an operator lock; code that disagrees with the spec is the defect."
metadata:
  type: project
---

The spec set was locked by the operator on 2026-09-21 after an eleven-item design session and two independent
Codex review passes. Every locked section is marked `LOCKED` with the date.

**Why:** the whole point of architecture-before-skeleton is that makers build, they do not re-decide. A maker
that quietly re-decides produces divergent implementations and an untraceable design.

**How to apply:**
- A maker or session that must re-decide an architecture item stops that part, records the concern in its
  report-back, and the advisor surfaces the decision to the operator as numbered prose with a recommendation.
- On a lock: edit the architecture doc AND write `docs/adr/<n>-<slug>.md` in the same commit.
- Spec vs code disagreement: the spec is right until it is changed; open a defect item and fix the code. If the
  spec is wrong, say so and route it through the decision path.
- The transition contract (§2.7) wins over any scattered sentence in the docs; a conflict is a doc defect.
