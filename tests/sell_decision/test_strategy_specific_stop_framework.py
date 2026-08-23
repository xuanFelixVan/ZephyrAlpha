# [BLUEPRINT] MOD-SELL-014 | docs/03_modules/MOD-SELL-014/
# [MODULE] zephyr.sell_decision.core.strategy_specific_stop_framework
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/sell_decision/test_strategy_specific_stop_framework.py
# [TTL] permanent
"""strategy_specific_stop_framework（策略特异止损框架）单元测试。

覆盖：
- 四类策略风格画像（趋势/均值回归/突破/波段）默认止损参数映射
- 初始止损/移动止损/时间止损/保本上移四类触发
- 止损价取最高（最紧）有效止损
- 非法输入 → InvalidStopFrameworkInputError
"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.strategy_specific_stop_framework import (
    InvalidStopFrameworkInputError,
    StopPositionInput,
    StopReason,
    StrategyProfile,
    compute_stop_state,
    default_stop_params,
)


def _pos(
    entry: float = 10.0,
    current: float = 10.0,
    highest: float = 10.0,
    days: int = 0,
) -> StopPositionInput:
    return StopPositionInput(
        entry_price=entry,
        current_price=current,
        highest_since_entry=highest,
        days_held=days,
    )


class TestDefaultParams:
    def test_all_profiles_have_params(self) -> None:
        """四类风格画像都有默认止损参数。"""
        for profile in StrategyProfile:
            p = default_stop_params(profile)
            assert p.initial_stop_pct > 0
            assert p.trailing_stop_pct > 0
            assert p.time_stop_days >= 1

    def test_trend_wider_than_mean_reversion(self) -> None:
        """趋势策略止损宽于均值回归（给趋势留喘息空间）。"""
        trend = default_stop_params(StrategyProfile.TREND_FOLLOWING)
        mr = default_stop_params(StrategyProfile.MEAN_REVERSION)
        assert trend.initial_stop_pct > mr.initial_stop_pct


class TestStopTriggers:
    def test_initial_stop_triggered(self) -> None:
        """现价跌破入场价×(1−初始止损) → INITIAL_STOP。"""
        mr = default_stop_params(StrategyProfile.MEAN_REVERSION)
        stop_price = 10.0 * (1.0 - mr.initial_stop_pct)
        r = compute_stop_state(
            _pos(current=stop_price - 0.01, highest=10.0),
            StrategyProfile.MEAN_REVERSION,
        )
        assert r.should_stop is True
        assert r.reason is StopReason.INITIAL_STOP

    def test_no_stop_within_band(self) -> None:
        """现价在止损带内 → 不触发。"""
        r = compute_stop_state(_pos(current=9.9, highest=10.0), StrategyProfile.TREND_FOLLOWING)
        assert r.should_stop is False
        assert r.reason is StopReason.NONE

    def test_trailing_stop_triggered(self) -> None:
        """冲高后回落破移动止损线 → TRAILING_STOP。"""
        # 波段: 保本触发先看参数; 高点 12, 现价回落破 trailing 线
        r = compute_stop_state(
            _pos(current=11.0, highest=12.0, days=5),
            StrategyProfile.SWING,
        )
        params = default_stop_params(StrategyProfile.SWING)
        trailing_line = 12.0 * (1.0 - params.trailing_stop_pct)
        assert 11.0 < trailing_line  # 确认测试数据真的破了移动止损线
        assert r.should_stop is True
        assert r.reason is StopReason.TRAILING_STOP

    def test_time_stop_triggered(self) -> None:
        """持有超时间预算 → TIME_STOP。"""
        params = default_stop_params(StrategyProfile.MEAN_REVERSION)
        r = compute_stop_state(
            _pos(current=10.1, highest=10.1, days=params.time_stop_days + 1),
            StrategyProfile.MEAN_REVERSION,
        )
        assert r.should_stop is True
        assert r.reason is StopReason.TIME_STOP

    def test_breakeven_move(self) -> None:
        """涨幅达保本触发线 → 有效止损价上移至入场价（不亏为底）。"""
        r = compute_stop_state(
            _pos(entry=10.0, current=10.5, highest=10.8, days=3),
            StrategyProfile.TREND_FOLLOWING,
        )
        assert r.active_stop_price >= 10.0

    def test_active_stop_is_tightest(self) -> None:
        """有效止损价=max(初始止损, 移动止损, 保本线)（最紧优先）。"""
        r = compute_stop_state(
            _pos(entry=10.0, current=10.6, highest=11.0, days=2),
            StrategyProfile.SWING,
        )
        params = default_stop_params(StrategyProfile.SWING)
        initial = 10.0 * (1.0 - params.initial_stop_pct)
        assert r.active_stop_price >= initial


class TestOverrides:
    def test_override_params(self) -> None:
        """参数覆写生效（如收紧初始止损到 3%）。"""
        base = default_stop_params(StrategyProfile.TREND_FOLLOWING)
        override = type(base)(
            initial_stop_pct=0.03,
            trailing_stop_pct=base.trailing_stop_pct,
            time_stop_days=base.time_stop_days,
            breakeven_trigger_pct=base.breakeven_trigger_pct,
        )
        r = compute_stop_state(
            _pos(current=9.65, highest=10.0),
            StrategyProfile.TREND_FOLLOWING,
            overrides=override,
        )
        assert r.should_stop is True
        assert r.reason is StopReason.INITIAL_STOP


class TestInvalidInput:
    def test_non_positive_entry(self) -> None:
        with pytest.raises(InvalidStopFrameworkInputError):
            compute_stop_state(_pos(entry=0.0), StrategyProfile.SWING)

    def test_non_positive_current(self) -> None:
        with pytest.raises(InvalidStopFrameworkInputError):
            compute_stop_state(_pos(current=-1.0), StrategyProfile.SWING)

    def test_highest_below_entry(self) -> None:
        """高点低于入场价（数据异常）→ 拒绝。"""
        with pytest.raises(InvalidStopFrameworkInputError):
            compute_stop_state(_pos(entry=10.0, highest=9.0), StrategyProfile.SWING)

    def test_negative_days(self) -> None:
        with pytest.raises(InvalidStopFrameworkInputError):
            compute_stop_state(_pos(days=-1), StrategyProfile.SWING)

    def test_invalid_override_params(self) -> None:
        """覆写参数非法（负止损）→ 拒绝。"""
        base = default_stop_params(StrategyProfile.SWING)
        bad = type(base)(
            initial_stop_pct=-0.05,
            trailing_stop_pct=base.trailing_stop_pct,
            time_stop_days=base.time_stop_days,
            breakeven_trigger_pct=base.breakeven_trigger_pct,
        )
        with pytest.raises(InvalidStopFrameworkInputError):
            compute_stop_state(_pos(), StrategyProfile.SWING, overrides=bad)
