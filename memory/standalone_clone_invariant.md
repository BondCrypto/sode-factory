---
name: standalone_clone_invariant
description: "A fresh clone of sode is independently valuable: make test green, one item shipped end to end on the mock provider, the tree free of any other repo's paths, ids, client names or credentials. Ideas from the sibling research repo are ported by name with a manifest, never imported."
metadata:
  type: project
---

Operator constraint (2026-08-22, restated 2026-09-15): at any point sode must be cloneable as a standalone valuable
instance. Acceptance = architecture §1.4, executed by `tests/test_standalone.py` in a temp HOME with no network.

**Why:** sode is the seed of a unified software factory, not a plugin of the research repo. A hidden dependency on
the sibling would make every clone worthless outside this machine.

**How to apply:**
- Never write an absolute path, an id namespace, a client name or a credential from another repo into this one.
- A ported asset (guards, ledger shape, checker, gate shape, cost model) is copied, adapted, tested here, and
  carries `platform/ports/<asset>.yaml` naming its source, source commit, kept invariants and dropped behaviour.
- The only runtime interface to the research repo, when the product plane exists, is two gated artifact classes
  (architecture §1.3). No shared code, paths or ids.
- The grep in the standalone test excludes the spec docs themselves, which list the forbidden namespaces as the rule.
