# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_kb_vms_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""CT-KB-VMS-001 集成测试——KB→Vector。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry
from zephyr.orchestrator.contract_router import ContractRouter


def test_ct_kb_vms_registered():
    contract = ContractRegistry().get("CT-KB-VMS-001")
    assert contract is not None
    assert contract.producer == "Knowledge Base"
    assert contract.consumer == "Vector Memory Service"


def test_ct_kb_vms_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-KB-VMS-001")
    assert result.allowed is True


def test_ct_kb_vms_route():
    router = ContractRouter(ContractRegistry())
    result = router.route("CT-KB-VMS-001")
    assert result.target_system == "vector_memory"
