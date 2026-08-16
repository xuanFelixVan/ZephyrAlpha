# [A_test] module_id: MOD-GOV_token_budget_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-696 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_token_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""Token 预算管理器单元测试——验证三级预算控制与 degraded 标记。"""


import pytest

from zephyr.infrastructure.capacity_assurance.token_budget import (
    BUDGET_CAPS,
    DEGRADED_THRESHOLD,
    BudgetState,
    TokenBudgetManager,
    TokenBudgetTier,
)


@pytest.fixture
def manager():
    return TokenBudgetManager(session_id="test-session-001")


class TestBudgetLevels:
    def test_l1_cap_is_500(self):
        assert BUDGET_CAPS[TokenBudgetTier.L1] == 500

    def test_l2_cap_is_1500(self):
        assert BUDGET_CAPS[TokenBudgetTier.L2] == 1500

    def test_l3_cap_is_8000(self):
        assert BUDGET_CAPS[TokenBudgetTier.L3] == 8000


class TestInitialState:
    def test_default_level_is_l1(self, manager):
        assert manager.level == TokenBudgetTier.L1

    def test_default_cap_is_500(self, manager):
        assert manager.cap == 500

    def test_default_consumed_is_zero(self, manager):
        assert manager.consumed == 0

    def test_default_not_degraded(self, manager):
        assert not manager.degraded


class TestSetLevel:
    def test_switch_to_l2(self, manager):
        manager.set_level(TokenBudgetTier.L2)
        assert manager.level == TokenBudgetTier.L2
        assert manager.cap == 1500

    def test_switch_to_l3(self, manager):
        manager.set_level(TokenBudgetTier.L3)
        assert manager.level == TokenBudgetTier.L3
        assert manager.cap == 8000

    def test_switch_preserves_consumed(self, manager):
        manager.consume(100)
        manager.set_level(TokenBudgetTier.L2)
        assert manager.consumed == 100


class TestConsume:
    def test_consume_within_budget(self, manager):
        result = manager.consume(300)
        assert result is True
        assert manager.consumed == 300
        assert manager.remaining == 200

    def test_consume_exact_budget(self, manager):
        result = manager.consume(500)
        assert result is True
        assert manager.consumed == 500
        assert manager.remaining == 0

    def test_consume_exceeds_budget(self, manager):
        result = manager.consume(600)
        assert result is False
        # All-or-nothing contract: a refused consume leaves consumed unchanged
        assert manager.consumed == 0

    def test_multiple_consumes(self, manager):
        assert manager.consume(100)
        assert manager.consume(200)
        assert manager.consume(150)
        assert manager.consumed == 450

    def test_can_consume_check(self, manager):
        assert manager.can_consume(400) is True
        assert manager.can_consume(600) is False


class TestDegradedFlag:
    def test_degraded_at_90_percent_l1(self, manager):
        manager.consume(450)
        assert manager.degraded is True

    def test_not_degraded_below_90_percent(self, manager):
        manager.consume(400)
        assert manager.degraded is False

    def test_degraded_at_threshold_l3(self, manager):
        manager.set_level(TokenBudgetTier.L3)
        manager.consume(DEGRADED_THRESHOLD)
        assert manager.degraded is True

    def test_degraded_above_threshold_l3(self, manager):
        manager.set_level(TokenBudgetTier.L3)
        manager.consume(7500)
        assert manager.degraded is True

    def test_degraded_false_after_reset(self, manager):
        manager.consume(450)
        assert manager.degraded is True
        manager.reset()
        assert manager.degraded is False


class TestReset:
    def test_reset_clears_consumed(self, manager):
        manager.consume(300)
        manager.reset()
        assert manager.consumed == 0

    def test_reset_clears_degraded(self, manager):
        manager.consume(490)
        assert manager.degraded is True
        manager.reset()
        assert manager.degraded is False


class TestToDict:
    def test_to_dict_contains_keys(self, manager):
        manager.consume(200)
        d = manager.to_dict()
        assert d["level"] == "L1"
        assert d["cap"] == 500
        assert d["consumed"] == 200
        assert d["remaining"] == 300
        assert d["degraded"] is False
        assert "usage_ratio" in d


class TestBudgetState:
    def test_budget_state_default(self):
        state = BudgetState()
        assert state.level == TokenBudgetTier.L1
        assert state.cap == 500
        assert state.consumed == 0
        assert state.degraded is False
