# [A_test] module_id: SRC-TST-0108 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-266 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_script_gate_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-SCRIPT-GATE-001 集成测试——Script Exit Code→Gate决策。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry
from zephyr.orchestrator.contracts.contract_router import ContractRouter


def test_ct_script_gate_registered():
    contract = ContractRegistry().get("CT-SCRIPT-GATE-001")
    assert contract is not None
    assert contract.producer == "Script System"
    assert contract.consumer == "Gate Engine"


def test_ct_script_gate_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-SCRIPT-GATE-001")
    assert result.allowed is True


def test_ct_script_gate_route():
    router = ContractRouter(ContractRegistry())
    result = router.route("CT-SCRIPT-GATE-001")
    assert result.target_system == "gate_engine"
