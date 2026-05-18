# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_fle_db_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""CT-FLE-DB-001 集成测试——FLE Metrics→DB。"""

from __future__ import annotations

import pytest

from zephyr.orchestrator.contract_registry import ContractRegistry


def test_ct_fle_db_registered():
    contract = ContractRegistry().get("CT-FLE-DB-001")
    assert contract is not None
    assert contract.producer == "Feedback Loop Engine"
    assert contract.consumer == "Database"


def test_ct_fle_db_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-FLE-DB-001")
    assert result.allowed is True
    assert "部分功能" in result.message
