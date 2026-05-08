"""CT-ORC-GATE-001 集成测试——Task Lifecycle Gate。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry
from zephyr.orchestrator.contract_router import ContractRouter


def test_ct_orc_gate_registered():
    contract = ContractRegistry().get("CT-ORC-GATE-001")
    assert contract is not None
    assert contract.producer == "Orchestrator"
    assert contract.consumer == "Gate Engine"


def test_ct_orc_gate_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-ORC-GATE-001")
    assert result.allowed is True


def test_ct_orc_gate_route():
    router = ContractRouter(ContractRegistry())
    result = router.route("CT-ORC-GATE-001")
    assert result.target_system == "gate_engine"
