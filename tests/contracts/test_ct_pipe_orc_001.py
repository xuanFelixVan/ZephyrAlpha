# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_pipe_orc_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""CT-PIPE-ORC-001 集成测试——Task→Pipeline路由。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry
from zephyr.orchestrator.contract_router import ContractRouter


def test_ct_pipe_orc_registered():
    contract = ContractRegistry().get("CT-PIPE-ORC-001")
    assert contract is not None
    assert contract.producer == "Task Pipeline"
    assert contract.consumer == "Orchestrator"


def test_ct_pipe_orc_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-PIPE-ORC-001")
    assert result.allowed is True


def test_ct_pipe_orc_route():
    router = ContractRouter(ContractRegistry())
    result = router.route("CT-PIPE-ORC-001")
    assert result.target_system == "pipeline"
