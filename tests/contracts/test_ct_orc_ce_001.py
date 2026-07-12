# [A_test] module_id: SRC-TST-0102 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-260 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_orc_ce_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-ORC-CE-001 集成测试——Session Context请求。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry


def test_ct_orc_ce_registered():
    contract = ContractRegistry().get("CT-ORC-CE-001")
    assert contract is not None
    assert contract.producer == "Orchestrator"
    assert contract.consumer == "Context Engine"


def test_ct_orc_ce_do_not_call():
    result = ContractRegistry().check_ai_read_only("CT-ORC-CE-001")
    assert result.allowed is False
