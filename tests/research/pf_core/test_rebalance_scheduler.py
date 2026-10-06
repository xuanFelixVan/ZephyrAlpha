# [BLUEPRINT] MOD-PF-003 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""Rebalance Scheduler 单元测试 (MOD-PF-003)。"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from zephyr.pf_core.core.portfolio_optimizer import PortfolioOptimizer
from zephyr.pf_core.core.rebalance_scheduler import (
    InvalidRebalanceInputError,
    RebalanceConfig,
    RebalanceDecision,
    RebalanceEvaluation,
    RebalanceScheduler,
    RebalanceTriggerSource,
)
from zephyr.shared.contracts.risk_limits import RiskLimits

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)  # 周六
FRIDAY = datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc)  # 周五


def _rl(**kw) -> RiskLimits:
    base = dict(
        as_of_date=T0,
        idempotency_key="rl-1",
        max_single_position=0.99,
        max_gross_leverage=1.0,
    )
    base.update(kw)
    return RiskLimits(**base)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_invalid_drift_threshold():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceConfig(portfolio_drift_threshold=0)


def test_config_invalid_single_drift_threshold():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceConfig(single_asset_drift_threshold=-0.1)


def test_config_invalid_calendar_weekday():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceConfig(calendar_weekday=7)


def test_config_invalid_improvement_ratio():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceConfig(improvement_ratio=0)


def test_config_invalid_stress_multiplier():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceConfig(stress_cost_multiplier=0.5)


def test_config_invalid_cost_rate():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceConfig(cost_rate=0)


# ── 触发源 ────────────────────────────────────────────────────────────────────


def test_no_trigger_when_close():
    scheduler = RebalanceScheduler()
    result = scheduler.evaluate(
        {"A": 0.50, "B": 0.50},
        {"A": 0.51, "B": 0.49},
        market_state=3,
        now=T0,
    )
    assert result.trigger_source == RebalanceTriggerSource.NONE
    assert result.triggered is False
    assert result.decision == RebalanceDecision.SKIP_NO_TRIGGER


def test_drift_threshold_trigger_portfolio():
    scheduler = RebalanceScheduler()
    # 组合漂移 0.10 > 0.02
    result = scheduler.evaluate(
        {"A": 0.40, "B": 0.60},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
    )
    assert result.trigger_source == RebalanceTriggerSource.DRIFT_THRESHOLD
    assert result.triggered is True


def test_drift_threshold_trigger_single_asset():
    scheduler = RebalanceScheduler()
    # 单标的漂移 0.05 > 0.03 (组合漂移 0.025 < 0.02? 不, 0.025>0.02 也触发组合)
    # 用 3 标的让组合漂移小但单标的大
    result = scheduler.evaluate(
        {"A": 0.30, "B": 0.35, "C": 0.35},
        {"A": 0.25, "B": 0.35, "C": 0.40},
        market_state=3,
        now=T0,
    )
    # 单标的 A/C 漂移 0.05 > 0.03
    assert result.triggered is True
    assert result.max_single_drift > 0.03


def test_calendar_trigger_friday():
    scheduler = RebalanceScheduler()
    result = scheduler.evaluate(
        {"A": 0.50, "B": 0.50},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=FRIDAY,  # 周五
    )
    assert result.trigger_source == RebalanceTriggerSource.CALENDAR


def test_event_trigger():
    scheduler = RebalanceScheduler()
    result = scheduler.evaluate(
        {"A": 0.50, "B": 0.50},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
        event_trigger=True,
    )
    assert result.trigger_source == RebalanceTriggerSource.EVENT


def test_risk_breach_highest_priority():
    """风控告警优先级最高, 即使周五也报 risk_breach。"""
    scheduler = RebalanceScheduler()
    result = scheduler.evaluate(
        {"A": 0.50, "B": 0.50},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=FRIDAY,
        risk_alert=True,
    )
    assert result.trigger_source == RebalanceTriggerSource.RISK_BREACH


def test_drift_overrides_calendar_and_event():
    scheduler = RebalanceScheduler()
    result = scheduler.evaluate(
        {"A": 0.30, "B": 0.70},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=FRIDAY,
        event_trigger=True,
    )
    assert result.trigger_source == RebalanceTriggerSource.DRIFT_THRESHOLD


# ── 成本收益 ──────────────────────────────────────────────────────────────────


def test_cost_benefit_passed_when_drift_large():
    """大漂移: benefit 远大于 cost → 通过。"""
    scheduler = RebalanceScheduler(config=RebalanceConfig(cost_rate=0.001))
    result = scheduler.evaluate(
        {"A": 0.20, "B": 0.80},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
    )
    assert result.cost_benefit_passed is True
    assert result.decision == RebalanceDecision.REBALANCE


def test_cost_benefit_failed_when_drift_small():
    """小漂移但超阈值: cost 可能 > benefit → 不通过。"""
    # cost_rate 极高让 cost 远大于 benefit
    scheduler = RebalanceScheduler(config=RebalanceConfig(cost_rate=1.0))
    result = scheduler.evaluate(
        {"A": 0.47, "B": 0.53},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
    )
    # 单标的漂移 0.03 触发, 但 cost 极高
    assert result.triggered is True
    assert result.cost_benefit_passed is False
    assert result.decision == RebalanceDecision.SKIP_COST_BENEFIT


def test_stress_market_increases_cost():
    """压力市场 ⑦⑧⑨ 成本 ×1.5。"""
    cfg_normal = RebalanceConfig(cost_rate=0.001)
    s = RebalanceScheduler(config=cfg_normal)
    r_normal = s.evaluate(
        {"A": 0.30, "B": 0.70},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
    )
    r_stress = s.evaluate(
        {"A": 0.30, "B": 0.70},
        {"A": 0.50, "B": 0.50},
        market_state=7,
        now=T0,  # 压力市场
    )
    assert r_stress.estimated_cost == pytest.approx(r_normal.estimated_cost * 1.5)


def test_stress_market_may_flip_cost_benefit():
    """压力市场成本升高可能使原本通过的变为不通过。"""
    # 用边界 case: 正常通过, 压力不通过
    s = RebalanceScheduler(config=RebalanceConfig(cost_rate=0.05, improvement_ratio=2.0))
    r_normal = s.evaluate(
        {"A": 0.40, "B": 0.60},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
    )
    r_stress = s.evaluate(
        {"A": 0.40, "B": 0.60},
        {"A": 0.50, "B": 0.50},
        market_state=9,
        now=T0,
    )
    assert r_stress.estimated_cost > r_normal.estimated_cost


# ── 重优化 ────────────────────────────────────────────────────────────────────


def test_reoptimize_produces_new_target_portfolio():
    opt = PortfolioOptimizer()
    scheduler = RebalanceScheduler(optimizer=opt)
    cov = np.eye(2)
    result = scheduler.evaluate(
        {"A": 0.20, "B": 0.80},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
        covariance=cov,
        risk_limits=_rl(),
        strategy_id="s1",
        portfolio_id="p1",
    )
    assert result.decision == RebalanceDecision.REBALANCE
    assert result.new_target_portfolio is not None
    assert result.new_target_portfolio.rebalance_reason == "drift_threshold"


def test_no_reoptimize_when_skipped():
    opt = PortfolioOptimizer()
    scheduler = RebalanceScheduler(optimizer=opt)
    result = scheduler.evaluate(
        {"A": 0.50, "B": 0.50},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
        covariance=np.eye(2),
        risk_limits=_rl(),
    )
    assert result.new_target_portfolio is None


def test_no_reoptimize_without_optimizer():
    scheduler = RebalanceScheduler(optimizer=None)
    result = scheduler.evaluate(
        {"A": 0.20, "B": 0.80},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=T0,
        covariance=np.eye(2),
        risk_limits=_rl(),
    )
    # 触发+成本通过, 但无 optimizer → decision=REBALANCE 但 new_tp=None
    assert result.decision == RebalanceDecision.REBALANCE
    assert result.new_target_portfolio is None


def test_reoptimize_reason_matches_trigger():
    opt = PortfolioOptimizer()
    scheduler = RebalanceScheduler(optimizer=opt)
    result = scheduler.evaluate(
        {"A": 0.50, "B": 0.50},
        {"A": 0.50, "B": 0.50},
        market_state=3,
        now=FRIDAY,  # 周五触发
        covariance=np.eye(2),
        risk_limits=_rl(),
    )
    # 周五触发但漂移=0, benefit=0 不 > cost → skip_cost_benefit
    assert result.trigger_source == RebalanceTriggerSource.CALENDAR
    assert result.decision == RebalanceDecision.SKIP_COST_BENEFIT


# ── 漂移计算 ──────────────────────────────────────────────────────────────────


def test_portfolio_drift_zero_when_matching():
    scheduler = RebalanceScheduler()
    result = scheduler.evaluate(
        {"A": 0.5, "B": 0.5},
        {"A": 0.5, "B": 0.5},
        market_state=3,
        now=T0,
    )
    assert result.portfolio_drift == 0.0
    assert result.max_single_drift == 0.0


def test_portfolio_drift_nonzero():
    scheduler = RebalanceScheduler()
    result = scheduler.evaluate(
        {"A": 0.4, "B": 0.6},
        {"A": 0.6, "B": 0.4},
        market_state=3,
        now=T0,
    )
    # Σ|Δw| = 0.4, portfolio_drift = 0.2
    assert result.portfolio_drift == pytest.approx(0.2)
    assert result.max_single_drift == pytest.approx(0.2)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_empty_weights_raises():
    scheduler = RebalanceScheduler()
    with pytest.raises(InvalidRebalanceInputError):
        scheduler.evaluate({}, {}, market_state=3, now=T0)


def test_negative_weights_raises():
    scheduler = RebalanceScheduler()
    with pytest.raises(InvalidRebalanceInputError):
        scheduler.evaluate({"A": -0.1, "B": 1.1}, {"A": 0.5, "B": 0.5}, now=T0)


# ── 结果属性 ──────────────────────────────────────────────────────────────────


def test_evaluation_has_idempotency_key():
    scheduler = RebalanceScheduler()
    r1 = scheduler.evaluate({"A": 0.5, "B": 0.5}, {"A": 0.5, "B": 0.5}, now=T0)
    r2 = scheduler.evaluate({"A": 0.5, "B": 0.5}, {"A": 0.5, "B": 0.5}, now=T0)
    assert r1.idempotency_key
    assert r1.idempotency_key != r2.idempotency_key


def test_should_rebalance_property():
    scheduler = RebalanceScheduler()
    triggered = scheduler.evaluate(
        {"A": 0.2, "B": 0.8},
        {"A": 0.5, "B": 0.5},
        now=T0,
    )
    not_triggered = scheduler.evaluate(
        {"A": 0.5, "B": 0.5},
        {"A": 0.5, "B": 0.5},
        now=T0,
    )
    assert triggered.should_rebalance is True
    assert not_triggered.should_rebalance is False


def test_to_dict():
    scheduler = RebalanceScheduler()
    result = scheduler.evaluate(
        {"A": 0.2, "B": 0.8},
        {"A": 0.5, "B": 0.5},
        now=T0,
    )
    d = result.to_dict()
    assert d["trigger_source"] == "drift_threshold"
    assert d["decision"] == "rebalance"
    assert "estimated_cost" in d
    assert "portfolio_drift" in d


# ── 不变量 ────────────────────────────────────────────────────────────────────


def test_invariant_stress_cost_is_higher():
    """压力市场成本 ≥ 正常市场成本。"""
    s = RebalanceScheduler()
    r_normal = s.evaluate({"A": 0.3, "B": 0.7}, {"A": 0.5, "B": 0.5}, market_state=1, now=T0)
    r_stress = s.evaluate({"A": 0.3, "B": 0.7}, {"A": 0.5, "B": 0.5}, market_state=8, now=T0)
    assert r_stress.estimated_cost >= r_normal.estimated_cost


def test_invariant_benefit_equals_drift():
    """benefit = portfolio_drift (再平衡可消除的漂移)。"""
    s = RebalanceScheduler()
    result = s.evaluate({"A": 0.3, "B": 0.7}, {"A": 0.5, "B": 0.5}, now=T0)
    assert result.estimated_benefit == pytest.approx(result.portfolio_drift)


def test_invariant_risk_alert_always_triggers():
    """风控告警无视漂移/日历, 总是触发。"""
    s = RebalanceScheduler()
    result = s.evaluate(
        {"A": 0.5, "B": 0.5},
        {"A": 0.5, "B": 0.5},
        now=T0,
        risk_alert=True,
    )
    assert result.triggered is True
    assert result.trigger_source == RebalanceTriggerSource.RISK_BREACH
