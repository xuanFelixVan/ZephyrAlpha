# [A_test] module_id: SRC-TST-1990 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-607 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.test_compliance_manager_contract
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
from __future__ import annotations
"""ComplianceManagerBase — 抽象接口形状校验。"""


from zephyr.governance.compliance_manager import ComplianceManagerBase


def test_compliance_manager_base_is_abstract() -> None:
    expected = {"register_rule", "evaluate", "list_applicable", "deactivate_rule"}
    assert ComplianceManagerBase.__abstractmethods__ == expected
