# [A_test] module_id: SRC-TST-0109 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-267 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_script_kb_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-SCRIPT-KB-001 集成测试——Finding→KE入库。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry


def test_ct_script_kb_registered():
    contract = ContractRegistry().get("CT-SCRIPT-KB-001")
    assert contract is not None
    assert contract.producer == "Script System"
    assert contract.consumer == "Knowledge Base"


def test_ct_script_kb_impl_required():
    result = ContractRegistry().check_ai_read_only("CT-SCRIPT-KB-001")
    assert result.allowed is False
    assert "需先完成实现" in result.message
