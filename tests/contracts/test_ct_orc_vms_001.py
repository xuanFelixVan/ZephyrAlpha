"""CT-ORC-VMS-001 集成测试——Task Output→Vector Memory。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry


def test_ct_orc_vms_registered():
    contract = ContractRegistry().get("CT-ORC-VMS-001")
    assert contract is not None
    assert contract.producer == "Orchestrator"
    assert contract.consumer == "Vector Memory Service"


def test_ct_orc_vms_do_not_call():
    result = ContractRegistry().check_ai_read_only("CT-ORC-VMS-001")
    assert result.allowed is False
