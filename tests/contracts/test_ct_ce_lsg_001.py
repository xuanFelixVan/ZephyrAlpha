# [A_test] module_id: SRC-TST-0096 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-254 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_ce_lsg_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-CE-LSG-001 集成测试——Context Injection Safety。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry


def test_ct_ce_lsg_registered():
    contract = ContractRegistry().get("CT-CE-LSG-001")
    assert contract is not None
    assert contract.producer == "Context Engine"
    assert contract.consumer == "LLM Security Gateway"


def test_ct_ce_lsg_do_not_call():
    result = ContractRegistry().check_ai_read_only("CT-CE-LSG-001")
    assert result.allowed is False
