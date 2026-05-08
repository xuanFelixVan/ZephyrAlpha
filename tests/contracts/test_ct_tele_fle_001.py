"""CT-TELE-FLE-001 集成测试——Telemetry→FLE。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry


def test_ct_tele_fle_registered():
    contract = ContractRegistry().get("CT-TELE-FLE-001")
    assert contract is not None
    assert contract.producer == "System Telemetry"
    assert contract.consumer == "Feedback Loop Engine"


def test_ct_tele_fle_do_not_call():
    result = ContractRegistry().check_ai_read_only("CT-TELE-FLE-001")
    assert result.allowed is False
