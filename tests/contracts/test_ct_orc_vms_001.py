# [A_test] module_id: SRC-TST-0105 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-263 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_orc_vms_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-ORC-VMS-001 集成测试——Task Output→Vector Memory。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry


def test_ct_orc_vms_registered():
    contract = ContractRegistry().get("CT-ORC-VMS-001")
    assert contract is not None
    assert contract.producer == "Orchestrator"
    assert contract.consumer == "Vector Memory Service"


def test_ct_orc_vms_do_not_call():
    result = ContractRegistry().check_ai_read_only("CT-ORC-VMS-001")
    assert result.allowed is False
