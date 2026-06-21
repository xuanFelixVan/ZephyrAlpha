# [A_test] module_id: SRC-TST-1982 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-599 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.test_can_i_deploy
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
from __future__ import annotations
"""Can-I-Deploy 预部署门禁单元测试。"""


import pytest
from zephyr.governance.rule_enforcement.can_i_deploy import CanIDeploy


@pytest.fixture
def gate():
    return CanIDeploy()


def test_all_ok_deploy_allowed(gate):
    result = gate.check(True, True, True, True)
    assert result.allowed is True
    assert len(result.blockers) == 0


def test_single_fail_blocks(gate):
    result = gate.check(True, False, True, True)
    assert result.allowed is False
    assert "schema_version" in result.blockers


def test_multiple_fails_blocks(gate):
    result = gate.check(False, False, True, True)
    assert result.allowed is False
    assert len(result.blockers) == 2
