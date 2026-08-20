# [BLUEPRINT] MOD-POS-009 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""CapitalCurveManager 单元测试 (MOD-POS-007)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.position.core.capital_curve_manager import (
    CapitalCurveConfig,
    CapitalCurveManager,
    CapitalCurveUpdatedEvent,
    DrawdownLevel,
    InvalidCapitalCurveInputError,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
CAP = 1_000_000.0


# ── 初始状态 ──────────────────────────────────────────────────────────────────


def test_initial_record_is_normal_no_expansion():
    mgr = CapitalCurveManager(initial_capital=CAP)
    snap = mgr.record(CAP, now=T0)
    assert snap.drawdown == pytest.approx(0.0)
    assert snap.drawdown_level is DrawdownLevel.NORMAL
    assert snap.position_cap == pytest.approx(1.0)
    assert snap.capital_curve_discount == pytest.approx(1.0)
    assert snap.expansion_factor == pytest.approx(1.0)
    assert snap.is_new_high is False
    assert snap.defensive_only is False
    assert snap.peak == pytest.approx(CAP)


# ── 回撤分级 → 仓位上限 ───────────────────────────────────────────────────────


def test_warning_level_5pct():
    mgr = CapitalCurveManager(initial_capital=CAP)
    # 回撤 6% → WARNING, cap 0.8
    snap = mgr.record(940_000.0, now=T0)
    assert snap.drawdown == pytest.approx(-0.06)
    assert snap.drawdown_level is DrawdownLevel.WARNING
    assert snap.position_cap == pytest.approx(0.8)
    assert snap.defensive_only is False


def test_critical_level_10pct():
    mgr = CapitalCurveManager(initial_capital=CAP)
    # 回撤 11% → CRITICAL, cap 0.5
    snap = mgr.record(890_000.0, now=T0)
    assert snap.drawdown == pytest.approx(-0.11)
    assert snap.drawdown_level is DrawdownLevel.CRITICAL
    assert snap.position_cap == pytest.approx(0.5)


def test_emergency_level_15pct_defensive_only():
    mgr = CapitalCurveManager(initial_capital=CAP)
    # 回撤 16% → EMERGENCY, cap 0.3, 仅防御
    snap = mgr.record(840_000.0, now=T0)
    assert snap.drawdown == pytest.approx(-0.16)
    assert snap.drawdown_level is DrawdownLevel.EMERGENCY
    assert snap.position_cap == pytest.approx(0.3)
    assert snap.defensive_only is True


def test_boundary_exactly_5pct_is_warning_no_contraction():
    # 设计: <5%正常(>=5%为WARNING); 回撤>5%才缩减(严格大于)
    mgr = CapitalCurveManager(initial_capital=CAP)
    snap = mgr.record(950_000.0, now=T0)  # 正好 -5%
    assert snap.drawdown_level is DrawdownLevel.WARNING
    assert snap.position_cap == pytest.approx(0.8)
    # 5% 不 > 5% → 无收缩
    assert snap.capital_curve_discount == pytest.approx(1.0)


# ── 盈利扩张 ──────────────────────────────────────────────────────────────────


def test_new_high_triggers_expansion():
    mgr = CapitalCurveManager(initial_capital=CAP)
    snap = mgr.record(1_050_000.0, now=T0)
    assert snap.is_new_high is True
    assert snap.expansion_factor == pytest.approx(1.05)
    assert snap.capital_curve_discount == pytest.approx(1.05)
    assert snap.peak == pytest.approx(1_050_000.0)


def test_multiple_new_highs_compound():
    mgr = CapitalCurveManager(initial_capital=CAP)
    mgr.record(1_050_000.0, now=T0)  # expansion 1.05
    snap = mgr.record(1_102_500.0, now=T0)  # expansion 1.10
    assert snap.expansion_factor == pytest.approx(1.10)
    assert snap.capital_curve_discount == pytest.approx(1.10)


def test_expansion_capped_at_hard_limit():
    cfg = CapitalCurveConfig(profit_expansion_step=0.5, profit_expansion_hard_limit=1.5)
    mgr = CapitalCurveManager(initial_capital=CAP, config=cfg)
    snap1 = mgr.record(1_100_000.0, now=T0)  # 1.0 + 0.5 = 1.5 (capped)
    assert snap1.expansion_factor == pytest.approx(1.5)
    snap2 = mgr.record(1_200_000.0, now=T0)  # min(2.0, 1.5) = 1.5
    assert snap2.expansion_factor == pytest.approx(1.5)


def test_position_cap_not_inflated_by_expansion():
    # 不变量: position_cap 仅由分级决定, 盈利扩张不放大 cap
    mgr = CapitalCurveManager(initial_capital=CAP)
    snap = mgr.record(1_050_000.0, now=T0)  # expansion 1.05, 但 NORMAL
    assert snap.position_cap == pytest.approx(1.0)  # 非 1.05
    assert snap.capital_curve_discount == pytest.approx(1.05)


# ── 亏损收缩 ──────────────────────────────────────────────────────────────────


def test_loss_contraction_5pct():
    mgr = CapitalCurveManager(initial_capital=CAP)
    snap = mgr.record(940_000.0, now=T0)  # -6% → 收缩 0.9
    assert snap.capital_curve_discount == pytest.approx(0.9)


def test_loss_contraction_10pct():
    mgr = CapitalCurveManager(initial_capital=CAP)
    snap = mgr.record(890_000.0, now=T0)  # -11% → 收缩 0.8
    assert snap.capital_curve_discount == pytest.approx(0.8)


def test_contraction_multiplies_expansion():
    # 先扩张到 1.05, 再回撤 11% → discount = 1.05 * 0.8
    mgr = CapitalCurveManager(initial_capital=CAP)
    mgr.record(1_050_000.0, now=T0)  # expansion 1.05, peak 1.05M
    snap = mgr.record(935_000.0, now=T0)  # (0.935-1.05)/1.05 = -0.1095 → CRITICAL
    assert snap.drawdown_level is DrawdownLevel.CRITICAL
    assert snap.capital_curve_discount == pytest.approx(1.05 * 0.8)


# ── 恢复 ──────────────────────────────────────────────────────────────────────


def test_recovery_clears_contraction_preserves_expansion():
    mgr = CapitalCurveManager(initial_capital=CAP)
    mgr.record(1_050_000.0, now=T0)  # expansion 1.05, peak 1.05M
    down = mgr.record(935_000.0, now=T0)  # 回撤, contraction 0.8
    assert down.capital_curve_discount == pytest.approx(1.05 * 0.8)
    # 回到峰值 (不创新高)
    recovered = mgr.record(1_050_000.0, now=T0)
    assert recovered.drawdown == pytest.approx(0.0)
    assert recovered.drawdown_level is DrawdownLevel.NORMAL
    assert recovered.capital_curve_discount == pytest.approx(1.05)  # 扩张保留, 收缩解除
    assert recovered.is_new_high is False


def test_recovery_via_new_high_grows_expansion():
    mgr = CapitalCurveManager(initial_capital=CAP)
    mgr.record(1_050_000.0, now=T0)  # expansion 1.05, peak 1.05M
    mgr.record(935_000.0, now=T0)  # 回撤
    snap = mgr.record(1_102_500.0, now=T0)  # 新高
    assert snap.is_new_high is True
    assert snap.expansion_factor == pytest.approx(1.10)
    assert snap.capital_curve_discount == pytest.approx(1.10)


# ── peak 单调非减 ─────────────────────────────────────────────────────────────


def test_peak_monotonic_non_decreasing():
    mgr = CapitalCurveManager(initial_capital=CAP)
    mgr.record(1_100_000.0, now=T0)  # peak 1.1M
    snap = mgr.record(900_000.0, now=T0)  # 回撤, peak 不降
    assert snap.peak == pytest.approx(1_100_000.0)
    assert mgr.peak == pytest.approx(1_100_000.0)


# ── 框架硬上限 ────────────────────────────────────────────────────────────────


def test_framework_hard_cap_caps_position_cap():
    mgr = CapitalCurveManager(initial_capital=CAP, framework_hard_cap=0.6)
    snap = mgr.record(CAP, now=T0)  # NORMAL cap 1.0, 但受框架 0.6 封顶
    assert snap.position_cap == pytest.approx(0.6)


# ── 事件 ──────────────────────────────────────────────────────────────────────


def test_event_emitted_on_every_record():
    mgr = CapitalCurveManager(initial_capital=CAP)
    events: list[CapitalCurveUpdatedEvent] = []
    mgr.on_capital_curve_updated(events.append)
    mgr.record(1_050_000.0, now=T0)  # peak 1.05M
    mgr.record(990_000.0, now=T0)  # (0.99-1.05)/1.05 = -5.7% → WARNING
    assert len(events) == 2
    assert events[0].context_snapshot["is_new_high"] is True
    assert events[1].context_snapshot["drawdown_level"] == "WARNING"


def test_event_has_snapshot_and_timestamp():
    mgr = CapitalCurveManager(initial_capital=CAP)
    events: list[CapitalCurveUpdatedEvent] = []
    mgr.on_capital_curve_updated(events.append)
    mgr.record(1_050_000.0, now=T0)
    assert events[0].snapshot.expansion_factor == pytest.approx(1.05)
    assert events[0].timestamp == T0


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_initial_capital_must_be_positive():
    with pytest.raises(InvalidCapitalCurveInputError):
        CapitalCurveManager(initial_capital=0)


def test_net_value_must_be_positive():
    mgr = CapitalCurveManager(initial_capital=CAP)
    with pytest.raises(InvalidCapitalCurveInputError):
        mgr.record(-1.0)


def test_framework_hard_cap_range():
    with pytest.raises(InvalidCapitalCurveInputError):
        CapitalCurveManager(initial_capital=CAP, framework_hard_cap=1.5)


def test_config_threshold_ordering():
    with pytest.raises(InvalidCapitalCurveInputError):
        CapitalCurveConfig(warning_threshold=0.10, critical_threshold=0.05, emergency_threshold=0.15)


def test_config_hard_limit_must_exceed_one():
    with pytest.raises(InvalidCapitalCurveInputError):
        CapitalCurveConfig(profit_expansion_hard_limit=1.0)
