# [A_test] module_id: SRC-TST-0110 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-268 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_tele_fle_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-TELE-FLE-001 集成测试——Telemetry→FLE。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry


def test_ct_tele_fle_registered():
    contract = ContractRegistry().get("CT-TELE-FLE-001")
    assert contract is not None
    assert contract.producer == "System Telemetry"
    assert contract.consumer == "Feedback Loop Engine"


def test_ct_tele_fle_do_not_call():
    result = ContractRegistry().check_ai_read_only("CT-TELE-FLE-001")
    assert result.allowed is False
