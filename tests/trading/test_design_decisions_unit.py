# [A_test] module_id: SRC-TST-2008 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-625 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_design_decisions
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""设计决策注册表单元测试——验证 DD-1~DD-14 决策记录与过滤。"""


import pytest

from zephyr.orchestrator.contracts.design_decisions import (
    DECISIONS,
    DecisionRegistry,
)


@pytest.fixture
def registry():
    return DecisionRegistry()


class TestDecisionCount:
    def test_14_decisions_registered(self):
        assert len(DECISIONS) == 14


class TestGet:
    def test_get_dd1(self, registry):
        dd = registry.get("DD-1")
        assert dd is not None
        assert "之间" in dd.title

    def test_get_nonexistent(self, registry):
        assert registry.get("DD-99") is None


class TestListAll:
    def test_list_all_14(self, registry):
        assert len(registry.list_all()) == 14

    def test_all_active(self, registry):
        assert len(registry.list_active()) == 14


class TestGetByImpact:
    def test_find_by_pipeline(self, registry):
        results = registry.get_by_impact("Pipeline")
        assert len(results) >= 1
        assert any(d.dd_id == "DD-8" for d in results)

    def test_find_by_circuit(self, registry):
        results = registry.get_by_impact("熔断")
        assert len(results) >= 1
        assert any(d.dd_id == "DD-4" for d in results)


class TestReEvaluate:
    def test_re_evaluate_condition_met(self, registry):
        assert registry.check_re_evaluate("DD-3", True) is True

    def test_re_evaluate_condition_not_met(self, registry):
        assert registry.check_re_evaluate("DD-3", False) is False
