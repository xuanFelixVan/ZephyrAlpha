# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.test_compliance_manager_contract
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""ComplianceManagerBase — 抽象接口形状校验。"""

from __future__ import annotations

from zephyr.l10_compliance.compliance_manager import ComplianceManagerBase


def test_compliance_manager_base_is_abstract() -> None:
    expected = {"register_rule", "evaluate", "list_applicable", "deactivate_rule"}
    assert ComplianceManagerBase.__abstractmethods__ == expected
