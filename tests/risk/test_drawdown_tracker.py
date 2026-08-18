# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""DrawdownTracker 单元测试 (MOD-RK-011)。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from zephyr.risk.core.drawdown_tracker import (
    DrawdownAlertedEvent,
    DrawdownAlertLevel,
    DrawdownTracker,
    DrawdownTrackerConfig,
    InvalidDrawdownInputError,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
NAV = 1_000_000.0


def t(offset_seconds: float = 0.0) -> datetime:
    return T0 + timedelta(seconds=offset_seconds)


# ── 初始状态 ──────────────────────────────────────────────────────────────────


def test_initial_state_is_none():
    tracker = DrawdownTracker(initial_net_value=NAV)
    snap = tracker.update(NAV, now=T0)
    assert snap.level is DrawdownAlertLevel.NONE
    assert snap.drawdown == pytest.approx(0.0)
    assert snap.peak == pytest.approx(NAV)
    assert snap.trough == pytest.approx(NAV)
    assert snap.is_emergency is False


# ── 峰值谷值跟踪 ──────────────────────────────────────────────────────────────


def test_new_high_updates_peak_and_resets_trough():
    tracker = DrawdownTracker(initial_net_value=NAV)
    tracker.update(950_000.0, now=t(0))   # 谷值 950K
    assert tracker.trough == pytest.approx(950_000.0)
    tracker.update(1_050_000.0, now=t(60))  # 新高
    assert tracker.peak == pytest.approx(1_050_000.0)
    assert tracker.trough == pytest.approx(1_050_000.0)  # 重置


def test_peak_monotonic_non_decreasing():
    tracker = DrawdownTracker(initial_net_value=NAV)
    tracker.update(1_100_000.0, now=t(0))  # peak 1.1M
    tracker.update(900_000.0, now=t(60))   # 回撤, peak 不降
    assert tracker.peak == pytest.approx(1_100_000.0)


def test_trough_tracks_lowest_since_peak():
    tracker = DrawdownTracker(initial_net_value=NAV)
    tracker.update(1_100_000.0, now=t(0))   # peak 1.1M
    tracker.update(980_000.0, now=t(60))    # trough 980K
    tracker.update(1_000_000.0, now=t(120))  # 回升但 trough 保留
    assert tracker.trough == pytest.approx(980_000.0)


# ── 三级阈值 ──────────────────────────────────────────────────────────────────


def test_warning_level():
    tracker = DrawdownTracker(initial_net_value=NAV)
    snap = tracker.update(940_000.0, now=T0)  # -6%
    assert snap.drawdown == pytest.approx(-0.06)
    assert snap.level is DrawdownAlertLevel.WARNING


def test_critical_level():
    tracker = DrawdownTracker(initial_net_value=NAV)
    snap = tracker.update(890_000.0, now=T0)  # -11%
    assert snap.level is DrawdownAlertLevel.CRITICAL


def test_emergency_level_triggers_kill_switch_flag():
    tracker = DrawdownTracker(initial_net_value=NAV)
    snap = tracker.update(840_000.0, now=T0)  # -16%
    assert snap.level is DrawdownAlertLevel.EMERGENCY
    assert snap.is_emergency is True


def test_boundary_exactly_5pct_is_warning():
    tracker = DrawdownTracker(initial_net_value=NAV)
    snap = tracker.update(950_000.0, now=T0)  # 正好 -5%
    assert snap.level is DrawdownAlertLevel.WARNING


def test_boundary_exactly_15pct_is_emergency():
    tracker = DrawdownTracker(initial_net_value=NAV)
    snap = tracker.update(850_000.0, now=T0)  # 正好 -15%
    assert snap.level is DrawdownAlertLevel.EMERGENCY


# ── 事件去抖 ──────────────────────────────────────────────────────────────────


def test_event_emitted_on_level_change():
    tracker = DrawdownTracker(initial_net_value=NAV)
    events: list[DrawdownAlertedEvent] = []
    tracker.on_drawdown_alerted(events.append)
    tracker.update(940_000.0, now=t(0))  # NONE → WARNING
    assert len(events) == 1
    assert events[0].level is DrawdownAlertLevel.WARNING
    assert events[0].is_escalation is True


def test_event_not_repeated_for_same_level():
    tracker = DrawdownTracker(initial_net_value=NAV)
    events: list[DrawdownAlertedEvent] = []
    tracker.on_drawdown_alerted(events.append)
    tracker.update(940_000.0, now=t(0))   # -6% WARNING
    tracker.update(935_000.0, now=t(60))  # -6.5% 仍 WARNING
    tracker.update(930_000.0, now=t(120))  # -7% 仍 WARNING
    assert len(events) == 1  # 去抖


def test_escalation_event_emitted():
    tracker = DrawdownTracker(initial_net_value=NAV)
    events: list[DrawdownAlertedEvent] = []
    tracker.on_drawdown_alerted(events.append)
    tracker.update(940_000.0, now=t(0))   # WARNING
    tracker.update(890_000.0, now=t(60))  # CRITICAL (升级)
    assert len(events) == 2
    assert events[1].level is DrawdownAlertLevel.CRITICAL
    assert events[1].is_escalation is True


# ── 恢复检测 ──────────────────────────────────────────────────────────────────


def test_recovery_event_on_level_drop():
    tracker = DrawdownTracker(initial_net_value=NAV)
    events: list[DrawdownAlertedEvent] = []
    tracker.on_drawdown_alerted(events.append)
    tracker.update(890_000.0, now=t(0))    # CRITICAL
    tracker.update(990_000.0, now=t(60))   # -1% → NONE (恢复)
    assert len(events) == 2
    assert events[1].level is DrawdownAlertLevel.NONE
    assert events[1].is_recovery is True


def test_in_recovery_flag_when_rebounding_but_not_new_high():
    tracker = DrawdownTracker(initial_net_value=NAV)
    tracker.update(1_100_000.0, now=t(0))   # peak 1.1M
    tracker.update(950_000.0, now=t(60))    # trough 950K, -13.6% CRITICAL
    snap = tracker.update(1_000_000.0, now=t(120))  # 回升, -9.09% WARNING, 未创新高
    assert snap.in_recovery is True
    assert snap.drawdown < 0  # 仍低于峰值


def test_recovery_completes_on_new_high():
    tracker = DrawdownTracker(initial_net_value=NAV)
    tracker.update(1_100_000.0, now=t(0))   # peak 1.1M
    tracker.update(950_000.0, now=t(60))    # 回撤
    snap = tracker.update(1_150_000.0, now=t(120))  # 新高
    assert snap.in_recovery is False
    assert snap.drawdown == pytest.approx(0.0)
    assert snap.peak == pytest.approx(1_150_000.0)


# ── 事件上下文 ────────────────────────────────────────────────────────────────


def test_event_context_snapshot():
    tracker = DrawdownTracker(initial_net_value=NAV)
    events: list[DrawdownAlertedEvent] = []
    tracker.on_drawdown_alerted(events.append)
    tracker.update(840_000.0, now=T0)  # EMERGENCY
    ctx = events[0].context_snapshot
    assert ctx["level"] == "EMERGENCY"
    assert ctx["previous_level"] == "NONE"
    assert ctx["is_recovery"] is False
    assert ctx["peak"] == pytest.approx(NAV)
    assert ctx["trough"] == pytest.approx(840_000.0)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_initial_net_value_must_be_positive():
    with pytest.raises(InvalidDrawdownInputError):
        DrawdownTracker(initial_net_value=0)


def test_net_value_must_be_positive():
    tracker = DrawdownTracker(initial_net_value=NAV)
    with pytest.raises(InvalidDrawdownInputError):
        tracker.update(-1.0)


def test_net_value_must_be_finite():
    """非有限值门禁（AI-R2 红队 ATK-1）：NaN/+Inf/-Inf 一律拒绝。

    实证：NaN 所有比较恒 False → 静默失明轮；+Inf 使 peak=inf 永久中毒，
    后续真实 -20% 回撤 drawdown=NaN → EMERGENCY 永不触发（回撤链静默死亡）。
    """
    tracker = DrawdownTracker(initial_net_value=NAV)
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(InvalidDrawdownInputError):
            tracker.update(bad)
    # 拒绝后链路完好：真实 -20% 回撤正常触发 EMERGENCY（默认阈值 15%）
    snap = tracker.update(NAV * 0.80)
    assert snap.level is DrawdownAlertLevel.EMERGENCY


def test_config_threshold_ordering():
    with pytest.raises(InvalidDrawdownInputError):
        DrawdownTrackerConfig(warning_threshold=0.10, critical_threshold=0.05, emergency_threshold=0.15)


# ── 可配置阈值 ────────────────────────────────────────────────────────────────


def test_custom_thresholds():
    cfg = DrawdownTrackerConfig(warning_threshold=0.03, critical_threshold=0.06, emergency_threshold=0.10)
    tracker = DrawdownTracker(initial_net_value=NAV, config=cfg)
    # -4% > 自定义 3% → WARNING (默认 5% 下会 NONE)
    snap = tracker.update(960_000.0, now=T0)
    assert snap.level is DrawdownAlertLevel.WARNING
