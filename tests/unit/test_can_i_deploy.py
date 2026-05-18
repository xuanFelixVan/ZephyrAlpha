# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.test_can_i_deploy
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""Can-I-Deploy 预部署门禁单元测试。"""

from __future__ import annotations

import pytest
from zephyr.gates.can_i_deploy import CanIDeploy


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
