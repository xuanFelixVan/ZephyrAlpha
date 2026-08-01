"""PositionDriftMonitor 单元测试 (MOD-POS-003)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.position.core.position_drift_monitor import (
    DriftDetectedEvent,
    DriftScope,
    InvalidDriftInputError,
    PositionDriftMonitor,
    TriageLevel,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


# ── 无漂移 ────────────────────────────────────────────────────────────────────


def test_no_drift_when_aligned():
    monitor = PositionDriftMonitor()
    result = monitor.check(
        actual_weights={"A": 0.05, "B": 0.30},
        target_weights={"A": 0.05, "B": 0.30},
        now=T0,
    )
    assert result.has_drift is False
    assert result.portfolio_alert is None
    assert result.symbol_alerts == []


def test_small_drift_below_threshold_no_alert():
    monitor = PositionDriftMonitor()
    # 组合 drift=0.01 < 0.02, 标的 drift 都 < 0.03
    result = monitor.check(
        actual_weights={"A": 0.06, "B": 0.29},
        target_weights={"A": 0.05, "B": 0.30},
        now=T0,
    )
    assert result.has_drift is False


# ── 组合级漂移 ────────────────────────────────────────────────────────────────


def test_portfolio_drift_triggered():
    monitor = PositionDriftMonitor()
    # 组合 drift = 0.10 - 0.05 = 0.05 > 0.02
    result = monitor.check(
        actual_weights={"A": 0.10},
        target_weights={"A": 0.05},
        now=T0,
    )
    assert result.portfolio_alert is not None
    assert result.portfolio_alert.scope == DriftScope.PORTFOLIO
    assert result.portfolio_alert.drift == pytest.approx(0.05)
    assert result.portfolio_alert.is_overweight is True
    assert result.portfolio_alert.triage == TriageLevel.WATCH


def test_portfolio_drift_underweight():
    monitor = PositionDriftMonitor()
    # 组合 drift = 0.30 - 0.35 = -0.05 (低配)
    result = monitor.check(
        actual_weights={"A": 0.30},
        target_weights={"A": 0.35},
        now=T0,
    )
    assert result.portfolio_alert is not None
    assert result.portfolio_alert.is_overweight is False


# ── 标的级漂移 ────────────────────────────────────────────────────────────────


def test_symbol_drift_triggered():
    monitor = PositionDriftMonitor()
    # A drift=0.04 > 0.03, B drift=0.01 < 0.03
    result = monitor.check(
        actual_weights={"A": 0.09, "B": 0.31},
        target_weights={"A": 0.05, "B": 0.30},
        now=T0,
    )
    assert len(result.symbol_alerts) == 1
    assert result.symbol_alerts[0].symbol == "A"
    assert result.symbol_alerts[0].drift == pytest.approx(0.04)


def test_both_levels_triggered():
    monitor = PositionDriftMonitor()
    # 组合 drift=0.05>0.02, A drift=0.05>0.03
    result = monitor.check(
        actual_weights={"A": 0.10},
        target_weights={"A": 0.05},
        now=T0,
    )
    assert result.portfolio_alert is not None
    assert len(result.symbol_alerts) == 1
    assert result.has_drift is True


# ── 持仓分级 ──────────────────────────────────────────────────────────────────


def test_triage_level_applied():
    monitor = PositionDriftMonitor()
    result = monitor.check(
        actual_weights={"A": 0.10},
        target_weights={"A": 0.05},
        triage_levels={"A": TriageLevel.HOLD},
        now=T0,
    )
    assert result.symbol_alerts[0].triage == TriageLevel.HOLD


def test_triage_defaults_to_monitor():
    monitor = PositionDriftMonitor()
    result = monitor.check(
        actual_weights={"A": 0.10},
        target_weights={"A": 0.05},
        now=T0,
    )
    assert result.symbol_alerts[0].triage == TriageLevel.MONITOR


# ── 可配置阈值 ────────────────────────────────────────────────────────────────


def test_custom_thresholds():
    monitor = PositionDriftMonitor(portfolio_threshold=0.05, symbol_threshold=0.10)
    # drift 0.04 < 自定义组合阈值 0.05 → 不触发
    result = monitor.check(
        actual_weights={"A": 0.09},
        target_weights={"A": 0.05},
        now=T0,
    )
    # 组合 drift=0.04 < 0.05 不触发, 但标的 drift=0.04 < 0.10 也不触发
    assert result.has_drift is False


def test_threshold_must_be_positive():
    with pytest.raises(InvalidDriftInputError):
        PositionDriftMonitor(portfolio_threshold=0)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_weight_out_of_range_raises():
    monitor = PositionDriftMonitor()
    with pytest.raises(InvalidDriftInputError):
        monitor.check({"A": 1.5}, {"A": 0.5})


def test_missing_symbol_in_actual_raises():
    monitor = PositionDriftMonitor()
    with pytest.raises(InvalidDriftInputError):
        monitor.check({"A": 0.05}, {"A": 0.05, "B": 0.05})


# ── 事件 ──────────────────────────────────────────────────────────────────────


def test_drift_event_emitted():
    monitor = PositionDriftMonitor()
    events: list[DriftDetectedEvent] = []
    monitor.on_drift_detected(events.append)
    monitor.check({"A": 0.10}, {"A": 0.05}, now=T0)
    assert len(events) == 1
    assert events[0].context_snapshot["symbol_drift_count"] == 1


def test_no_event_when_no_drift():
    monitor = PositionDriftMonitor()
    events: list[DriftDetectedEvent] = []
    monitor.on_drift_detected(events.append)
    monitor.check({"A": 0.05}, {"A": 0.05}, now=T0)
    assert events == []
