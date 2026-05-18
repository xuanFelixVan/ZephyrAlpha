# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_script_gate_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""CT-SCRIPT-GATE-001 集成测试——Script Exit Code→Gate决策。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry
from zephyr.orchestrator.contract_router import ContractRouter


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
