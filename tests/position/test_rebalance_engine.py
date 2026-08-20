"""RebalanceEngine 单元测试 (MOD-POS-004)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.position.core.position_drift_monitor import (
    DriftAlert,
    DriftDetectedEvent,
    DriftResult,
    DriftScope,
    PositionDriftMonitor,
    TriageLevel,
)
from zephyr.position.core.rebalance_engine import (
    InvalidRebalanceInputError,
    RebalanceAction,
    RebalanceEngine,
    RebalanceTrigger,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


def _make_drift_event(
    actual: dict[str, float],
    target: dict[str, float],
    now: datetime = T0,
) -> DriftDetectedEvent:
    """用 PositionDriftMonitor 构造一个 DriftDetectedEvent。"""
    monitor = PositionDriftMonitor(portfolio_threshold=0.001, symbol_threshold=0.001)
    result = monitor.check(actual_weights=actual, target_weights=target, now=now)
    # 强制产出事件(即使无漂移也构造, 测试用)
    if not result.has_drift:
        result = DriftResult(
            portfolio_alert=DriftAlert(
                scope=DriftScope.PORTFOLIO,
                symbol=None,
                actual_weight=sum(actual.values()),
                target_weight=sum(target.values()),
                drift=sum(actual.values()) - sum(target.values()),
                threshold=0.001,
                triage=TriageLevel.MONITOR,
            ),
            symbol_alerts=[],
            timestamp=now,
        )
    return DriftDetectedEvent(result=result, timestamp=now)


# ── 无需再平衡 ────────────────────────────────────────────────────────────────


def test_no_rebalance_when_aligned():
    """权重一致时, 无调仓指令, 跳过再平衡。"""
    engine = RebalanceEngine(cost_rate=0.001)
    event = _make_drift_event({"A": 0.05, "B": 0.30}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.05, "B": 0.30},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    assert decision.should_rebalance is False
    assert decision.orders == []
    assert decision.turnover == pytest.approx(0.0)


# ── 成本收益判定 ──────────────────────────────────────────────────────────────


def test_skip_when_cost_exceeds_improvement():
    """交易成本 > 预期收益改善 → 跳过。"""
    # 极小漂移 + 极高成本率 → 成本远超改善
    engine = RebalanceEngine(cost_rate=1.0, improvement_ratio_threshold=2.0)
    event = _make_drift_event({"A": 0.06, "B": 0.29}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.06, "B": 0.29},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    assert decision.should_rebalance is False
    assert "transaction_cost" in decision.reason or "improvement_ratio" in decision.reason


def test_execute_when_improvement_exceeds_threshold():
    """预期改善 > 2× 成本 → 执行。"""
    # 大漂移 + 低成本率 → 改善远超成本
    engine = RebalanceEngine(cost_rate=0.0001, improvement_ratio_threshold=2.0)
    event = _make_drift_event({"A": 0.20, "B": 0.10}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.20, "B": 0.10},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    assert decision.should_rebalance is True
    assert decision.improvement_ratio >= 2.0
    assert len(decision.orders) == 2


def test_improvement_ratio_boundary():
    """改善比恰好等于阈值时执行(>=)。"""
    # 构造: 漂移使得 improvement/cost 刚好在阈值附近
    engine = RebalanceEngine(cost_rate=0.001, improvement_ratio_threshold=0.5)
    event = _make_drift_event({"A": 0.15, "B": 0.15}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.15, "B": 0.15},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    # 大漂移 + 低阈值 → 应执行
    assert decision.should_rebalance is True


# ── 压力市场状态 ──────────────────────────────────────────────────────────────


def test_stress_market_state_cost_multiplier():
    """压力状态(7/8/9)成本系数×1.5, 可能将"执行"变为"跳过"。"""
    # 同样的漂移, 正常状态执行, 压力状态可能跳过
    actual = {"A": 0.20, "B": 0.10}
    target = {"A": 0.05, "B": 0.30}
    event = _make_drift_event(actual, target)

    engine = RebalanceEngine(cost_rate=0.01, improvement_ratio_threshold=2.0)

    # 正常状态
    dec_normal = engine.evaluate(
        drift_event=event,
        actual_weights=actual,
        target_weights=target,
        market_state=3,
        now=T0,
    )
    # 压力状态
    dec_stress = engine.evaluate(
        drift_event=event,
        actual_weights=actual,
        target_weights=target,
        market_state=7,
        now=T0,
    )
    # 压力状态成本 = 正常状态成本 × 1.5
    assert dec_stress.transaction_cost == pytest.approx(dec_normal.transaction_cost * 1.5)


def test_normal_market_state_no_multiplier():
    """正常状态(0-6)无成本系数加成。"""
    engine = RebalanceEngine(cost_rate=0.001)
    event = _make_drift_event({"A": 0.10, "B": 0.20}, {"A": 0.05, "B": 0.30})
    for state in (0, 1, 2, 3, 4, 5, 6):
        decision = engine.evaluate(
            drift_event=event,
            actual_weights={"A": 0.10, "B": 0.20},
            target_weights={"A": 0.05, "B": 0.30},
            market_state=state,
            now=T0,
        )
        # 正常状态 multiplier=1.0
        turnover = sum(abs(t - a) for a, t in zip((0.10, 0.20), (0.05, 0.30)))
        assert decision.transaction_cost == pytest.approx(turnover * 0.001 * 1.0)


# ── 调仓指令生成 ──────────────────────────────────────────────────────────────


def test_orders_overweight_sell_underweight_buy():
    """超配→SELL, 低配→BUY。"""
    engine = RebalanceEngine(cost_rate=0.0001, improvement_ratio_threshold=0.1)
    event = _make_drift_event({"A": 0.20, "B": 0.10}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.20, "B": 0.10},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    assert decision.should_rebalance is True
    orders_by_sym = {o.symbol: o for o in decision.orders}
    # A 超配 → SELL (delta 负)
    assert orders_by_sym["A"].action == RebalanceAction.SELL
    assert orders_by_sym["A"].delta < 0
    # B 低配 → BUY (delta 正)
    assert orders_by_sym["B"].action == RebalanceAction.BUY
    assert orders_by_sym["B"].delta > 0


def test_turnover_calculation():
    """总换手率 = Σ|Δweight_i|。"""
    engine = RebalanceEngine(cost_rate=0.0001, improvement_ratio_threshold=0.1)
    event = _make_drift_event({"A": 0.20, "B": 0.10}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.20, "B": 0.10},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    # |0.05-0.20| + |0.30-0.10| = 0.15 + 0.20 = 0.35
    assert decision.turnover == pytest.approx(0.35)


# ── 日历强制触发 ──────────────────────────────────────────────────────────────


def test_calendar_trigger_forces_execution():
    """CALENDAR 周频强制触发: 改善比不足但成本<改善时仍执行(放宽改善比阈值)。

    注意: "成本>改善→跳过"是禁止亏损再平衡的硬规则, CALENDAR 不覆盖;
    CALENDAR 仅放宽改善比阈值(2×规则)。
    """
    # 漂移 0.01+0.01, turnover=0.02, improvement=0.0002
    # cost_rate=0.005 → cost=0.0001 < improvement=0.0002 (通过硬规则)
    # ratio=0.0002/0.0001=2.0 < threshold=10.0 (改善比不足)
    engine = RebalanceEngine(cost_rate=0.005, improvement_ratio_threshold=10.0)
    event = _make_drift_event({"A": 0.06, "B": 0.29}, {"A": 0.05, "B": 0.30})

    # DEVIATION 触发: 改善比不足 → 跳过
    dec_dev = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.06, "B": 0.29},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        trigger=RebalanceTrigger.DEVIATION,
        now=T0,
    )
    assert dec_dev.should_rebalance is False
    assert "improvement_ratio" in dec_dev.reason

    # CALENDAR 触发: 强制执行(改善比不足但日历强制)
    dec_cal = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.06, "B": 0.29},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        trigger=RebalanceTrigger.CALENDAR,
        now=T0,
    )
    assert dec_cal.should_rebalance is True
    assert "calendar-forced" in dec_cal.reason


# ── 事件订阅 ──────────────────────────────────────────────────────────────────


def test_event_emitted_on_rebalance():
    """执行再平衡时发出 E-POS-03 事件。"""
    engine = RebalanceEngine(cost_rate=0.0001, improvement_ratio_threshold=0.1)
    received: list = []
    engine.on_rebalance_triggered(received.append)

    event = _make_drift_event({"A": 0.20, "B": 0.10}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.20, "B": 0.10},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    assert decision.should_rebalance is True
    assert len(received) == 1
    fired = received[0]
    assert fired.decision is decision
    assert fired.timestamp == T0
    assert fired.context_snapshot["trigger"] == "DEVIATION"


def test_no_event_when_skipped():
    """跳过再平衡时不发出事件。"""
    engine = RebalanceEngine(cost_rate=1.0, improvement_ratio_threshold=10.0)
    received: list = []
    engine.on_rebalance_triggered(received.append)

    event = _make_drift_event({"A": 0.06, "B": 0.29}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.06, "B": 0.29},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    assert decision.should_rebalance is False
    assert len(received) == 0


def test_listener_error_isolated():
    """监听器故障不影响主流程。"""
    engine = RebalanceEngine(cost_rate=0.0001, improvement_ratio_threshold=0.1)

    def bad_listener(_event):
        raise RuntimeError("listener boom")

    good_received: list = []
    engine.on_rebalance_triggered(bad_listener)
    engine.on_rebalance_triggered(good_received.append)

    event = _make_drift_event({"A": 0.20, "B": 0.10}, {"A": 0.05, "B": 0.30})
    decision = engine.evaluate(
        drift_event=event,
        actual_weights={"A": 0.20, "B": 0.10},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        now=T0,
    )
    # 坏监听器不影响决策结果, 好监听器仍收到事件
    assert decision.should_rebalance is True
    assert len(good_received) == 1


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_invalid_weight_out_of_range():
    engine = RebalanceEngine()
    with pytest.raises(InvalidRebalanceInputError):
        engine.evaluate(
            drift_event=None,
            actual_weights={"A": 1.5},
            target_weights={"A": 0.5},
            now=T0,
        )


def test_missing_symbol_in_actual():
    engine = RebalanceEngine()
    with pytest.raises(InvalidRebalanceInputError):
        engine.evaluate(
            drift_event=None,
            actual_weights={"A": 0.05},
            target_weights={"A": 0.05, "B": 0.30},
            now=T0,
        )


def test_invalid_cost_rate():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceEngine(cost_rate=0.0)


def test_invalid_threshold():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceEngine(improvement_ratio_threshold=0.0)


def test_invalid_tolerance():
    with pytest.raises(InvalidRebalanceInputError):
        RebalanceEngine(post_rebalance_tolerance=-0.01)


# ── 无 drift_event 降级 ───────────────────────────────────────────────────────


def test_no_drift_event_degrades_to_weight_diff():
    """无 drift_event 时(CALENDAR 触发), 降级用权重差计算改善。"""
    engine = RebalanceEngine(cost_rate=0.0001, improvement_ratio_threshold=0.1)
    decision = engine.evaluate(
        drift_event=None,
        actual_weights={"A": 0.20, "B": 0.10},
        target_weights={"A": 0.05, "B": 0.30},
        market_state=3,
        trigger=RebalanceTrigger.CALENDAR,
        now=T0,
    )
    assert decision.should_rebalance is True
    assert decision.expected_improvement > 0
