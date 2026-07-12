# [A_test] module_id: SRC-TST-0099 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-257 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_fle_orc_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-FLE-ORC-001 集成测试——异常检测→调度调整。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry


def test_ct_fle_orc_registered():
    contract = ContractRegistry().get("CT-FLE-ORC-001")
    assert contract is not None
    assert contract.producer == "Feedback Loop Engine"
    assert contract.consumer == "Orchestrator"


def test_ct_fle_orc_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-FLE-ORC-001")
    assert result.allowed is True
    assert result.hint.value == "CAUTION_STUB"
