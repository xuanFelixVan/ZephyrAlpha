# [A_test] module_id: SRC-TST-2058 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-675 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_risk_registry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""风险注册表单元测试——验证 R-MOD-1~34 风险追踪。"""


import pytest

from zephyr.orchestrator.governance.risk_registry import RiskRegistry, RiskStatus


@pytest.fixture
def registry():
    return RiskRegistry()


def test_34_risks_registered(registry):
    assert len(registry.list_all()) == 34


def test_get_risk(registry):
    risk = registry.get("R-MOD-1")
    assert risk is not None
    assert risk.risk_id == "R-MOD-1"


def test_all_open_initially(registry):
    assert len(registry.list_open()) == 34


def test_mitigate_risk(registry):
    assert registry.mitigate("R-MOD-1")
    assert registry.get("R-MOD-1").status == RiskStatus.MITIGATED


def test_accept_risk(registry):
    assert registry.accept("R-MOD-2")
    assert registry.get("R-MOD-2").status == RiskStatus.ACCEPTED


def test_invalid_risk(registry):
    assert registry.get("R-UNKNOWN") is None
    assert not registry.mitigate("R-UNKNOWN")
