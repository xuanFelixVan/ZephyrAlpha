# [A_test] module_id: MOD-RK-DLG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] 35_drawdown_protocol_impl | §3.5.1/§6.14
# [MODULE] tests.risk.test_drawdown_liquidation_guard
# [INVARIANTS] 撤单率12%预警/15%blocked/分母0不预警; 全清30s超时残余非空才告警; 负输入抛错
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_liquidation_guard.py
# [TTL] task_bound
"""全清超时告警 + 撤单率预检测试（35 号 §6.14，A 股 2026 新规适配）。"""

from __future__ import annotations

import pytest

from zephyr.risk.core.drawdown_liquidation_guard import (
    InvalidLiquidationGuardInputError,
    check_cancel_rate,
    check_liquidation_timeout,
)


class TestCancelRatePrecheck:
    def test_normal_rate(self):
        r = check_cancel_rate(5, 100)
        assert r.cancel_rate == 0.05
        assert r.warning is False and r.blocked is False
        assert r.remaining_cancel_budget == 10  # floor(0.15*100) - 5

    def test_zero_total_no_constraint(self):
        """分母 0：无撤单率概念，不预警。"""
        r = check_cancel_rate(0, 0)
        assert r.cancel_rate == 0.0
        assert r.warning is False and r.blocked is False

    def test_warning_at_12pct(self):
        """超 12% 预警留 3% buffer（§6.14）。"""
        r = check_cancel_rate(13, 100)
        assert r.warning is True
        assert r.blocked is False
        assert r.remaining_cancel_budget == 2

    def test_blocked_at_15pct(self):
        r = check_cancel_rate(15, 100)
        assert r.blocked is True
        assert r.remaining_cancel_budget == 0

    def test_blocked_when_budget_exhausted(self):
        """额度耗尽即 blocked（再撤一笔即超红线）。"""
        r = check_cancel_rate(1, 10)  # floor(1.5)=1 → budget=0
        assert r.blocked is True

    def test_boundary_exactly_12pct(self):
        r = check_cancel_rate(12, 100)
        assert r.warning is True  # ≥ 阈值即预警

    def test_invalid_counts(self):
        with pytest.raises(InvalidLiquidationGuardInputError):
            check_cancel_rate(-1, 100)
        with pytest.raises(InvalidLiquidationGuardInputError):
            check_cancel_rate(101, 100)  # 已撤 > 总委托

    def test_invalid_thresholds(self):
        with pytest.raises(InvalidLiquidationGuardInputError):
            check_cancel_rate(1, 100, warn_threshold=0.20, hard_limit=0.15)


class TestLiquidationTimeout:
    def test_cleared_no_alert(self):
        """已全清（无残余）不告警，即便超时。"""
        assert check_liquidation_timeout(started_monotonic=0.0, now_monotonic=999.0, remaining_positions={}) is None

    def test_within_timeout_no_alert(self):
        assert (
            check_liquidation_timeout(
                started_monotonic=100.0,
                now_monotonic=120.0,
                remaining_positions={"600519": {"qty": 100}},
            )
            is None
        )

    def test_exactly_at_timeout_no_alert(self):
        """边界：恰好 30s 不告警（严格超过才告警）。"""
        assert (
            check_liquidation_timeout(
                started_monotonic=0.0,
                now_monotonic=30.0,
                remaining_positions={"600519": {"qty": 100}},
            )
            is None
        )

    def test_timeout_with_remaining_alerts(self):
        alert = check_liquidation_timeout(
            started_monotonic=0.0,
            now_monotonic=31.0,
            remaining_positions={
                "600519": {"qty": 100},
                "000001": {"qty": 0},  # 零持仓不计残余
                "300750": {"qty": 50},
            },
        )
        assert alert is not None
        assert alert.elapsed_seconds == 31.0
        assert set(alert.remaining_symbols) == {"600519", "300750"}
        assert "人工介入" in alert.reason

    def test_plain_qty_mapping_supported(self):
        alert = check_liquidation_timeout(
            started_monotonic=0.0,
            now_monotonic=45.0,
            remaining_positions={"600519": 100},
        )
        assert alert is not None
        assert alert.remaining_symbols == ("600519",)

    def test_inverted_time_raises(self):
        with pytest.raises(InvalidLiquidationGuardInputError):
            check_liquidation_timeout(started_monotonic=10.0, now_monotonic=5.0, remaining_positions={})

    def test_invalid_timeout_raises(self):
        with pytest.raises(InvalidLiquidationGuardInputError):
            check_liquidation_timeout(
                started_monotonic=0.0,
                now_monotonic=1.0,
                remaining_positions={},
                timeout_seconds=0.0,
            )
