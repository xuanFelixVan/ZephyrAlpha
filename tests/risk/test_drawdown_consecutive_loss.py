# [A_test] module_id: MOD-RK-DCL | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] 35_drawdown_protocol_impl | §3.5/§6.2
# [MODULE] tests.risk.test_drawdown_consecutive_loss
# [INVARIANTS] 连亏≥5→cap_multiplier=0.5; pnl=0重置; 盈利重置; 同日幂等; NaN拒绝
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_consecutive_loss.py
# [TTL] task_bound
"""连续亏损降仓测试（35 号 §6.2：连续 5 天亏损 → 降仓 50%）。"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from zephyr.risk.core.drawdown_consecutive_loss import (
    ConsecutiveLossConfig,
    ConsecutiveLossTracker,
    InvalidConsecutiveLossInputError,
    check_consecutive_loss,
)

D0 = date(2026, 8, 3)


def _day(n: int) -> date:
    return D0 + timedelta(days=n)


class TestCheckConsecutiveLoss:
    def test_five_consecutive_losses_triggers(self):
        alert = check_consecutive_loss([-100.0] * 5)
        assert alert.triggered is True
        assert alert.consecutive_loss_days == 5
        assert alert.cap_multiplier == 0.5

    def test_four_losses_not_triggered(self):
        alert = check_consecutive_loss([-100.0] * 4)
        assert alert.triggered is False
        assert alert.cap_multiplier == 1.0

    def test_trailing_streak_only(self):
        """只数序列末尾连亏：更早的亏损被盈利日隔断。"""
        alert = check_consecutive_loss([-100.0] * 10 + [500.0, -1.0, -2.0])
        assert alert.triggered is False
        assert alert.consecutive_loss_days == 2

    def test_zero_pnl_resets_streak(self):
        """pnl=0 非亏损日（重置连亏计数）。"""
        alert = check_consecutive_loss([-100.0] * 6 + [0.0])
        assert alert.triggered is False
        assert alert.consecutive_loss_days == 0

    def test_empty_series(self):
        alert = check_consecutive_loss([])
        assert alert.triggered is False
        assert alert.consecutive_loss_days == 0

    def test_long_streak_counts_all(self):
        alert = check_consecutive_loss([-1.0] * 8)
        assert alert.triggered is True
        assert alert.consecutive_loss_days == 8

    def test_custom_config(self):
        cfg = ConsecutiveLossConfig(consecutive_days=3, reduction_pct=0.25)
        alert = check_consecutive_loss([-1.0] * 3, cfg)
        assert alert.triggered is True
        assert alert.cap_multiplier == 0.75

    def test_nan_rejected(self):
        with pytest.raises(InvalidConsecutiveLossInputError):
            check_consecutive_loss([-1.0, float("nan")])

    def test_invalid_config(self):
        with pytest.raises(InvalidConsecutiveLossInputError):
            ConsecutiveLossConfig(consecutive_days=0)
        with pytest.raises(InvalidConsecutiveLossInputError):
            ConsecutiveLossConfig(reduction_pct=1.5)


class TestConsecutiveLossTracker:
    def test_daily_progression(self):
        tracker = ConsecutiveLossTracker()
        for i in range(4):
            alert = tracker.update(_day(i), -100.0)
            assert alert.triggered is False
        alert = tracker.update(_day(4), -100.0)
        assert alert.triggered is True
        assert alert.cap_multiplier == 0.5

    def test_profit_day_resets(self):
        tracker = ConsecutiveLossTracker()
        for i in range(5):
            tracker.update(_day(i), -100.0)
        alert = tracker.update(_day(5), 1.0)
        assert alert.triggered is False
        assert tracker.consecutive_loss_days == 0
        alert = tracker.update(_day(6), -1.0)
        assert alert.consecutive_loss_days == 1

    def test_same_day_idempotent(self):
        """同日重复 update 以最新 pnl 重算，不重复推进。"""
        tracker = ConsecutiveLossTracker()
        for i in range(4):
            tracker.update(_day(i), -100.0)
        tracker.update(_day(4), -100.0)  # 第 5 日亏损
        alert = tracker.update(_day(4), 50.0)  # 同日修正为盈利
        assert alert.triggered is False
        assert tracker.consecutive_loss_days == 0
        # 同日再修正回亏损 → 回到 5
        alert = tracker.update(_day(4), -100.0)
        assert alert.triggered is True
        assert alert.consecutive_loss_days == 5

    def test_date_regression_raises(self):
        tracker = ConsecutiveLossTracker()
        tracker.update(_day(2), -1.0)
        with pytest.raises(InvalidConsecutiveLossInputError):
            tracker.update(_day(1), -1.0)
