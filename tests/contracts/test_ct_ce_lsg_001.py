"""CT-CE-LSG-001 集成测试——Context Injection Safety。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry


def test_ct_ce_lsg_registered():
    contract = ContractRegistry().get("CT-CE-LSG-001")
    assert contract is not None
    assert contract.producer == "Context Engine"
    assert contract.consumer == "LLM Security Gateway"


def test_ct_ce_lsg_do_not_call():
    result = ContractRegistry().check_ai_read_only("CT-CE-LSG-001")
    assert result.allowed is False
