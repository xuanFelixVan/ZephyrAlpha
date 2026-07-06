# [A_test] module_id: SRC-TST-1982 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-599 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_can_i_deploy
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""Can-I-Deploy 预部署门禁单元测试。"""


import pytest

from zephyr.governance.rule_enforcement.can_i_deploy import CanIDeploy


@pytest.fixture
def gate():
    return CanIDeploy()


def test_all_ok_deploy_allowed(gate):
    result = gate.check(
        consumer_expectations_ok=True,
        schema_version_ok=True,
        contract_consistency_ok=True,
        health_ok=True,
    )
    assert result.allowed is True
    assert len(result.blockers) == 0


def test_single_fail_blocks(gate):
    result = gate.check(
        consumer_expectations_ok=True,
        schema_version_ok=False,
        contract_consistency_ok=True,
        health_ok=True,
    )
    assert result.allowed is False
    assert "schema_version" in result.blockers


def test_multiple_fails_blocks(gate):
    result = gate.check(
        consumer_expectations_ok=False,
        schema_version_ok=False,
        contract_consistency_ok=True,
        health_ok=True,
    )
    assert result.allowed is False
    assert len(result.blockers) == 2
