---
name: brief_per_session_rendered
description: "Every build session starts from ONE rendered brief with the spec sections inlined; a stub or a doc pointer is not a brief. Render from docs/references/build_session_brief_template.md; lint before dispatch; the report-back file is part of the contract."
metadata:
  type: feedback
---

Operator question (2026-09-21): are the build docs self-sufficient, or is a brief needed per phase? Answer: the
docs are the SOURCE; a session needs a rendered paste-first brief. The build plan carries stubs, not briefs.

**Why:** a fresh session has no context. A pointer to a doc makes the maker assemble the contract from six files
and choose where they disagree. Inlining the exact sections removes the choosing. The research repo learned this
through a series of poisoned and under-specified briefs.

**How to apply:**
- Fill `docs/references/build_session_brief_template.md`: goal · inlined spec sections · entry tag · touches ·
  do-not-touch · ordered steps · executable acceptance · quality bar · budget row · commit plan · report-back
  schema · context withhold · recitation last.
- Until component C5 exists the advisor renders by hand; after C5 the factory renders.
- A brief without executable acceptance, without the do-not-touch list, or without the recitation block does not
  dispatch.
- Verify the session's output yourself against the acceptance before committing; never trust the report alone.
