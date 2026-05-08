"""CT-SCRIPT-KB-001 集成测试——Finding→KE入库。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry


def test_ct_script_kb_registered():
    contract = ContractRegistry().get("CT-SCRIPT-KB-001")
    assert contract is not None
    assert contract.producer == "Script System"
    assert contract.consumer == "Knowledge Base"


def test_ct_script_kb_impl_required():
    result = ContractRegistry().check_ai_read_only("CT-SCRIPT-KB-001")
    assert result.allowed is False
    assert "需先完成实现" in result.message
