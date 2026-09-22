"""tests.schema.test_checks — factory-schema/doc anti-drift (gate check).

Passes on the real tree; a doc whose section 3.3 block drifts from the schema is
caught with a remediation string.
"""
from __future__ import annotations

from platform.core import paths
from platform.schema.checks import check_factory_schema_doc_sync

_DRIFTED_DOC = """# fake architecture doc

### 3.3 Per-stage binding
```yaml
schema_version: 1
policy_profile: standard
stages:
  spec: {}
  deploy: {}
```
"""


def test_passes_on_the_real_tree():
    root = paths.find_repo_root(__file__)
    ok, findings = check_factory_schema_doc_sync(root)
    assert ok, findings


def test_detects_drift_and_names_remediation(tmp_path):
    doc = tmp_path / "docs" / "design" / "sode_factory_architecture.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(_DRIFTED_DOC, encoding="utf-8")

    ok, findings = check_factory_schema_doc_sync(tmp_path)
    assert ok is False
    # The schema carries keys the drifted doc omits, and the stage sets differ.
    assert any("top-level keys NOT in section 3.3" in f for f in findings)
    assert any("stage names drift" in f for f in findings)
    # Every finding ends with a remediation clause ("-- ...").
    assert all("--" in f for f in findings)
