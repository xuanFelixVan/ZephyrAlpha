# [A_test] module_id: MOD-GOV_test_liquidity_stress_exit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.risk.core.test_liquidity_stress_exit
# [TESTS] src/zephyr/risk/core/liquidity_monitor.py（90 号 Phase2 扩展段）
# [TTL] task_bound
"""90 号 Phase2 项（#8 流动性）：liquidity_monitor 扩展已知答案 toy 断言。

裁定真源：90_methodology_open_questions.md §8（v2.0.0 简化采纳）——
  ① 压力退出时间=持仓/(ADV×0.3 压力折扣×10% 参与率)，>1 天→禁新开仓；
  ③ LVaR 简化式=VaR×√退出天数+半价差；
  ④ A 股特有维度：跌停/停牌/ST→禁开仓（比 ILLIQ 更致命）。
"""

from __future__ import annotations

import pytest

from zephyr.risk.core.liquidity_monitor import (
    LiquidityMonitor,
    compute_lvar,
    compute_stress_exit_days,
)


class TestStressExitDays:
    """退出天数=持仓/(ADV×0.3×0.1)。"""

    def test_known_answer_below_one_day(self):
        # 10万持仓 / (1000万ADV×0.3×0.1=30万) = 0.3333 天
        days = compute_stress_exit_days(position_value=100_000.0, adv_value=10_000_000.0)
        assert days == pytest.approx(1 / 3)

    def test_known_answer_above_one_day(self):
        # 40万 / 30万 = 1.333 天
        days = compute_stress_exit_days(position_value=400_000.0, adv_value=10_000_000.0)
        assert days == pytest.approx(4 / 3)

    def test_zero_adv_is_infinite(self):
        assert compute_stress_exit_days(position_value=1.0, adv_value=0.0) == float("inf")

    def test_negative_position_raises(self):
        with pytest.raises(ValueError):
            compute_stress_exit_days(position_value=-1.0, adv_value=1.0)


class TestLvar:
    """LVaR=VaR×√退出天数+半价差。"""

    def test_known_answer(self):
        # 0.02×√4 + 0.001 = 0.041
        assert compute_lvar(var=0.02, exit_days=4.0, half_spread=0.001) == pytest.approx(0.041)

    def test_exit_one_day_equals_var_plus_spread(self):
        assert compute_lvar(var=0.02, exit_days=1.0, half_spread=0.0) == pytest.approx(0.02)


class TestOpeningPermission:
    def test_normal_allowed(self):
        mon = LiquidityMonitor()
        perm = mon.assess_opening_permission(symbol="600000.SH", position_value=100_000.0, adv_value=10_000_000.0)
        assert perm.allowed is True
        assert perm.exit_days == pytest.approx(1 / 3)

    def test_exit_over_one_day_blocked(self):
        mon = LiquidityMonitor()
        perm = mon.assess_opening_permission(symbol="600000.SH", position_value=400_000.0, adv_value=10_000_000.0)
        assert perm.allowed is False
        assert any("退出时间" in r for r in perm.reasons)

    def test_ashare_dimensions_block(self):
        """跌停/停牌/ST 任一→禁开仓（裁定④）。"""
        mon = LiquidityMonitor()
        for flags in (
            {"is_limit_down": True},
            {"is_suspended": True},
            {"is_st": True},
        ):
            perm = mon.assess_opening_permission(
                symbol="600000.SH",
                position_value=1_000.0,
                adv_value=10_000_000.0,
                **flags,
            )
            assert perm.allowed is False, flags

    def test_zero_adv_blocked(self):
        mon = LiquidityMonitor()
        perm = mon.assess_opening_permission(symbol="600000.SH", position_value=1_000.0, adv_value=0.0)
        assert perm.allowed is False
