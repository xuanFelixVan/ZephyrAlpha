# [A_test] module_id: SRC-TST-0104 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-262 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_orc_script_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-ORC-SCRIPT-001 集成测试——Task Blocking→Task创建。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry
from zephyr.orchestrator.contracts.contract_router import ContractRouter


def test_ct_orc_script_registered():
    registry = ContractRegistry()
    contract = registry.get("CT-ORC-SCRIPT-001")
    assert contract is not None
    assert contract.producer == "Orchestrator"
    assert contract.consumer == "Script System"


def test_ct_orc_script_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-ORC-SCRIPT-001")
    assert result.allowed is True


def test_ct_orc_script_route():
    router = ContractRouter(ContractRegistry())
    result = router.route("CT-ORC-SCRIPT-001", {"finding_id": "F-001"})
    assert result.target_system == "script_system"


def test_ct_orc_script_telemetry():
    contract = ContractRegistry().get("CT-ORC-SCRIPT-001")
    assert len(contract.telemetry_metrics) == 3
