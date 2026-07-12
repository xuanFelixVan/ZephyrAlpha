# [A_test] module_id: SRC-TST-0092 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-250 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contract.test_contract_test_anchors
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""contract-test-anchors.yaml 中登记的路径必须存在。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from zephyr.shared.io.paths import REPO_ROOT

ANCHORS = REPO_ROOT / "tests/contract/contract-test-anchors.yaml"


def _paths_for_entry(rel: Any) -> list[str]:
    if isinstance(rel, list):
        return [str(x).replace("\\", "/") for x in rel]
    return [str(rel).replace("\\", "/")]


def test_anchor_files_exist() -> None:
    data = yaml.safe_load(ANCHORS.read_text(encoding="utf-8"))
    anchors = data.get("anchors", {})
    assert anchors, "anchors 为空"
    for contract_id, rel in anchors.items():
        for rel_one in _paths_for_entry(rel):
            path = REPO_ROOT / rel_one
            assert path.is_file(), f"{contract_id} → {path} 不存在"
