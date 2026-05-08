"""CT-CE-VMS-001 集成测试——Context→Vector Search。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry


def test_ct_ce_vms_registered():
    contract = ContractRegistry().get("CT-CE-VMS-001")
    assert contract is not None
    assert contract.producer == "Context Engine"
    assert contract.consumer == "Vector Memory Service"


def test_ct_ce_vms_ai_can_call():
    result = ContractRegistry().check_ai_read_only("CT-CE-VMS-001")
    assert result.allowed is True
