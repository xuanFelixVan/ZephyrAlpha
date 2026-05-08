"""CT-FLE-ORC-001 集成测试——异常检测→调度调整。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry


def test_ct_fle_orc_registered():
    contract = ContractRegistry().get("CT-FLE-ORC-001")
    assert contract is not None
    assert contract.producer == "Feedback Loop Engine"
    assert contract.consumer == "Orchestrator"


def test_ct_fle_orc_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-FLE-ORC-001")
    assert result.allowed is True
    assert result.hint.value == "CAUTION_STUB"
