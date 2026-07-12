# [A_test] module_id: SRC-TST-0098 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-256 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.contracts.test_ct_fle_db_001
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""CT-FLE-DB-001 集成测试——FLE Metrics→DB。"""

from __future__ import annotations

from zephyr.orchestrator.contracts.contract_registry import ContractRegistry


def test_ct_fle_db_registered():
    contract = ContractRegistry().get("CT-FLE-DB-001")
    assert contract is not None
    assert contract.producer == "Feedback Loop Engine"
    assert contract.consumer == "Database"


def test_ct_fle_db_caution_stub():
    result = ContractRegistry().check_ai_read_only("CT-FLE-DB-001")
    assert result.allowed is True
    assert "部分功能" in result.message
