# [TTL] permanent
# [TESTS] src/zephyr/pf_core/core/strategy_capacity_estimator.py (MOD-PF-012)
"""MOD-PF-012 strategy_capacity_estimator 单元测试（B3-05544 PC-08 策略容量估算器）。"""

from __future__ import annotations

import pytest

from zephyr.pf_core.core.strategy_capacity_estimator import (
    BindingConstraint,
    CapacityAlertLevel,
    CapacityConfig,
    CapacityEstimationError,
    ExpansionAdvice,
    StrategyCapacityEstimator,
    StrategyCapacityReport,
)

ADV = {"A": 2e8, "B": 3e8}  # 日成交额合计 5 亿


class TestCapacity:
    def test_participation_binding(self) -> None:
        # 参与率 5% → 可交易 5e8×0.05=2.5e7；换手 0.10 → 容量 2.5e8
        # 冲击: coef=50bps×√0.05≈11.2bps ≤ 50bps 容忍 → 不约束
        est = StrategyCapacityEstimator()
        rep = est.estimate(adv_values=ADV, daily_turnover=0.10)
        assert isinstance(rep, StrategyCapacityReport)
        assert rep.binding is BindingConstraint.PARTICIPATION
        assert abs(rep.capacity_aum - 2.5e8) < 1.0
        assert rep.effective_participation == pytest.approx(0.05)

    def test_impact_tolerance_binding(self) -> None:
        # 冲击容忍 2bps → participation ≤ (2/50)²=0.0016 < 0.05 → 冲击约束绑定
        est = StrategyCapacityEstimator()
        rep = est.estimate(adv_values=ADV, daily_turnover=0.10, impact_tolerance_bps=2.0)
        assert rep.binding is BindingConstraint.IMPACT_TOLERANCE
        assert rep.effective_participation == pytest.approx(0.0016)
        assert abs(rep.capacity_aum - 5e8 * 0.0016 / 0.10) < 1.0

    def test_custom_participation_max(self) -> None:
        est = StrategyCapacityEstimator()
        rep = est.estimate(adv_values=ADV, daily_turnover=0.10, participation_max=0.02)
        assert rep.effective_participation == pytest.approx(0.02)
        assert abs(rep.capacity_aum - 5e8 * 0.02 / 0.10) < 1.0

    def test_utilization_and_warning(self) -> None:
        est = StrategyCapacityEstimator()  # 容量 2.5e8
        rep = est.estimate(adv_values=ADV, daily_turnover=0.10, current_aum=2.1e8)
        assert rep.utilization == pytest.approx(0.84)
        assert rep.alert is CapacityAlertLevel.WARNING  # ≥80% 预警线

    def test_breach_alert_and_deleverage(self) -> None:
        est = StrategyCapacityEstimator()
        rep = est.estimate(adv_values=ADV, daily_turnover=0.10, current_aum=3e8)
        assert rep.alert is CapacityAlertLevel.BREACH
        assert ExpansionAdvice.DELEVERAGE in rep.advice

    def test_ok_level_minimal_advice(self) -> None:
        est = StrategyCapacityEstimator()
        rep = est.estimate(adv_values=ADV, daily_turnover=0.10, current_aum=1e8)
        assert rep.alert is CapacityAlertLevel.OK

    def test_expansion_advice_by_binding(self) -> None:
        est = StrategyCapacityEstimator()
        rep_p = est.estimate(adv_values=ADV, daily_turnover=0.10, current_aum=2.2e8)
        assert ExpansionAdvice.EXPAND_UNIVERSE in rep_p.advice
        rep_i = est.estimate(adv_values=ADV, daily_turnover=0.10, impact_tolerance_bps=2.0, current_aum=7e6)
        assert rep_i.binding is BindingConstraint.IMPACT_TOLERANCE
        assert ExpansionAdvice.REDUCE_TURNOVER in rep_i.advice


class TestFailClosed:
    def test_empty_adv(self) -> None:
        with pytest.raises(CapacityEstimationError):
            StrategyCapacityEstimator().estimate(adv_values={}, daily_turnover=0.1)

    def test_non_positive_adv(self) -> None:
        with pytest.raises(CapacityEstimationError):
            StrategyCapacityEstimator().estimate(adv_values={"A": 0.0}, daily_turnover=0.1)
        with pytest.raises(CapacityEstimationError):
            StrategyCapacityEstimator().estimate(adv_values={"A": -1}, daily_turnover=0.1)

    def test_invalid_turnover(self) -> None:
        with pytest.raises(CapacityEstimationError):
            StrategyCapacityEstimator().estimate(adv_values=ADV, daily_turnover=0.0)
        with pytest.raises(CapacityEstimationError):
            StrategyCapacityEstimator().estimate(adv_values=ADV, daily_turnover=float("nan"))

    def test_invalid_participation(self) -> None:
        with pytest.raises(CapacityEstimationError):
            StrategyCapacityEstimator().estimate(adv_values=ADV, daily_turnover=0.1, participation_max=0.0)
        with pytest.raises(CapacityEstimationError):
            StrategyCapacityEstimator().estimate(adv_values=ADV, daily_turnover=0.1, participation_max=1.5)

    def test_negative_aum_rejected(self) -> None:
        with pytest.raises(CapacityEstimationError):
            StrategyCapacityEstimator().estimate(adv_values=ADV, daily_turnover=0.1, current_aum=-1)

    def test_invalid_config(self) -> None:
        with pytest.raises(CapacityEstimationError):
            CapacityConfig(participation_max=0.0)
        with pytest.raises(CapacityEstimationError):
            CapacityConfig(warn_ratio=1.5)
        with pytest.raises(CapacityEstimationError):
            CapacityConfig(impact_coef_bps=-1)
