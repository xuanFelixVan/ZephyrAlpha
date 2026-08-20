# [BLUEPRINT] MOD-SELL-017 | docs/03_modules/_domain_sell_decision/blueprint.md
# [MODULE] tests.sell_decision.test_trade_level_circuit_breaker
# [DOMAIN] D_SELL_DECISION
# [INVARIANTS] 2/3/4笔递减0.75/0.50/0.25; ≥5笔阻断; 盈利重置; 零盈亏不动
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""TradeLevelCircuitBreaker 交易级熔断测试（42 号 §3.10，AI-NIGHT-001 包P）。"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.trade_level_circuit_breaker import TradeLevelCircuitBreaker


class TestScalingLadder:
    def test_no_loss_full_scale(self):
        cb = TradeLevelCircuitBreaker()
        assert cb.get_position_scale() == 1.0
        assert cb.is_blocked() is False

    def test_one_loss_not_triggered(self):
        cb = TradeLevelCircuitBreaker()
        cb.on_trade_close(-0.01)
        assert cb.get_position_scale() == 1.0  # threshold=2 未达

    @pytest.mark.parametrize(
        "losses,expected_scale",
        [(2, 0.75), (3, 0.50), (4, 0.25), (5, 0.25)],
    )
    def test_decreasing_ladder(self, losses: int, expected_scale: float):
        cb = TradeLevelCircuitBreaker()
        for _ in range(losses):
            cb.on_trade_close(-0.01)
        assert cb.get_position_scale() == pytest.approx(expected_scale)

    def test_min_scale_floor_never_zero(self):
        cb = TradeLevelCircuitBreaker()
        for _ in range(10):
            cb.on_trade_close(-0.01)
        assert cb.get_position_scale() == 0.25  # 减速非停车


class TestBlocking:
    def test_blocked_at_threshold_plus_3(self):
        cb = TradeLevelCircuitBreaker(consecutive_loss_threshold=2)
        for _ in range(4):
            cb.on_trade_close(-0.01)
        assert cb.is_blocked() is False
        cb.on_trade_close(-0.01)  # 第 5 笔
        assert cb.is_blocked() is True

    def test_custom_threshold(self):
        cb = TradeLevelCircuitBreaker(consecutive_loss_threshold=3)
        for _ in range(2):
            cb.on_trade_close(-0.01)
        assert cb.get_position_scale() == 1.0
        cb.on_trade_close(-0.01)
        assert cb.get_position_scale() == pytest.approx(0.75)


class TestReset:
    def test_win_resets(self):
        cb = TradeLevelCircuitBreaker()
        for _ in range(3):
            cb.on_trade_close(-0.01)
        assert cb.get_position_scale() == pytest.approx(0.50)
        cb.on_trade_close(0.02)
        assert cb.consecutive_losses == 0
        assert cb.get_position_scale() == 1.0
        assert cb.is_blocked() is False

    def test_zero_pnl_no_change(self):
        cb = TradeLevelCircuitBreaker()
        cb.on_trade_close(-0.01)
        cb.on_trade_close(0.0)  # 零盈亏：非亏非赢，证据不足不动
        assert cb.consecutive_losses == 1

    def test_reset_on_win_disabled(self):
        cb = TradeLevelCircuitBreaker(reset_on_win=False)
        cb.on_trade_close(-0.01)
        cb.on_trade_close(0.05)  # 盈利不重置
        assert cb.consecutive_losses == 1
        cb.on_trade_close(-0.01)
        assert cb.get_position_scale() == pytest.approx(0.75)
