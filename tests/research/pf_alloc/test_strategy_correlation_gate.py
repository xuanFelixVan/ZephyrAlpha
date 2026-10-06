# [BLUEPRINT] MOD-PA-007 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""StrategyCorrelationGate 单元测试 (MOD-PA-004)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.pf_alloc.core.strategy_correlation_gate import (
    CorrelationGateConfig,
    CorrelationGateTriggeredEvent,
    GateVerdict,
    InvalidCorrelationInputError,
    StrategyCorrelationGate,
    StrategyPairMetrics,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


# ── 通过 ──────────────────────────────────────────────────────────────────────


def test_pass_when_all_below_thresholds():
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", correlation=0.50, factor_overlap=0.30)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.PASS
    assert result.passed is True
    assert result.violations == []
    assert result.pairs_checked == 1


def test_empty_pairs_pass():
    gate = StrategyCorrelationGate()
    result = gate.check([], now=T0)
    assert result.overall_verdict is GateVerdict.PASS


# ── 相关性 ────────────────────────────────────────────────────────────────────


def test_correlation_reject_above_085():
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", correlation=0.88)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.REJECT
    assert result.rejected is True


def test_correlation_hard_reject_above_090():
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", correlation=0.92)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.HARD_REJECT


def test_correlation_takes_absolute_value():
    # 负相关取绝对值 (同质化的反向策略也算高相关)
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", correlation=-0.88)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.REJECT


def test_correlation_boundary_085_not_triggered():
    # > 0.85 严格大于, 0.85 不触发
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", correlation=0.85)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.PASS


# ── 因子重叠 ──────────────────────────────────────────────────────────────────


def test_factor_overlap_warn_above_60():
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", factor_overlap=0.65)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.WARN
    assert result.passed is True  # WARN 可上线


def test_factor_overlap_reject_above_80():
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", factor_overlap=0.85)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.REJECT


# ── 股票池 + 行业 (联合) ──────────────────────────────────────────────────────


def test_pool_sector_joint_warn():
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", stock_pool_overlap=0.75, sector_concentration=0.55)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.WARN


def test_pool_only_without_sector_no_warn():
    # 联合条件: 仅股票池超, 行业不超 → 不触发
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", stock_pool_overlap=0.75, sector_concentration=0.40)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.PASS


# ── 尾部相关 (方向约束) ───────────────────────────────────────────────────────


def test_tail_correlation_reject_same_direction():
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", tail_correlation=0.75, same_direction=True)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.REJECT


def test_tail_correlation_no_reject_different_direction():
    # same_direction=False → 尾部相关不触发 REJECT
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", tail_correlation=0.75, same_direction=False)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.PASS


# ── 整体裁决聚合 ──────────────────────────────────────────────────────────────


def test_overall_verdict_is_worst_across_pairs():
    gate = StrategyCorrelationGate()
    pairs = [
        StrategyPairMetrics("S1", "S2", factor_overlap=0.65),  # WARN
        StrategyPairMetrics("S2", "S3", correlation=0.92),  # HARD_REJECT
        StrategyPairMetrics("S1", "S3", correlation=0.50),  # PASS
    ]
    result = gate.check(pairs, now=T0)
    assert result.overall_verdict is GateVerdict.HARD_REJECT
    assert len(result.violations) == 2  # S1-S2 WARN + S2-S3 HARD_REJECT
    assert result.pairs_checked == 3


def test_multiple_violations_in_one_pair():
    # 一个 pair 同时高相关 + 高因子重叠 → 取最严重
    gate = StrategyCorrelationGate()
    pair = StrategyPairMetrics("S1", "S2", correlation=0.92, factor_overlap=0.85)
    result = gate.check([pair], now=T0)
    assert result.overall_verdict is GateVerdict.HARD_REJECT
    assert len(result.violations) == 2


# ── 事件 ──────────────────────────────────────────────────────────────────────


def test_event_emitted_when_violation():
    gate = StrategyCorrelationGate()
    events: list[CorrelationGateTriggeredEvent] = []
    gate.on_gate_triggered(events.append)
    gate.check([StrategyPairMetrics("S1", "S2", correlation=0.88)], now=T0)
    assert len(events) == 1
    assert events[0].context_snapshot["overall_verdict"] == "REJECT"


def test_no_event_when_pass():
    gate = StrategyCorrelationGate()
    events: list[CorrelationGateTriggeredEvent] = []
    gate.on_gate_triggered(events.append)
    gate.check([StrategyPairMetrics("S1", "S2", correlation=0.50)], now=T0)
    assert events == []


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_self_correlation_raises():
    gate = StrategyCorrelationGate()
    with pytest.raises(InvalidCorrelationInputError):
        gate.check([StrategyPairMetrics("S1", "S1", correlation=0.5)])


def test_metric_out_of_range_raises():
    gate = StrategyCorrelationGate()
    with pytest.raises(InvalidCorrelationInputError):
        gate.check([StrategyPairMetrics("S1", "S2", correlation=1.5)])


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_correlation_ordering():
    with pytest.raises(InvalidCorrelationInputError):
        CorrelationGateConfig(reject_correlation=0.90, hard_reject_correlation=0.85)


def test_config_factor_overlap_ordering():
    with pytest.raises(InvalidCorrelationInputError):
        CorrelationGateConfig(warn_factor_overlap=0.80, reject_factor_overlap=0.60)


def test_config_threshold_range():
    with pytest.raises(InvalidCorrelationInputError):
        CorrelationGateConfig(reject_correlation=1.5)


# ── 可配置阈值 ────────────────────────────────────────────────────────────────


def test_custom_thresholds():
    cfg = CorrelationGateConfig(reject_correlation=0.50, hard_reject_correlation=0.70)
    gate = StrategyCorrelationGate(config=cfg)
    # 0.55 > 自定义 0.50 → REJECT (默认阈值 0.85 下会 PASS)
    result = gate.check([StrategyPairMetrics("S1", "S2", correlation=0.55)], now=T0)
    assert result.overall_verdict is GateVerdict.REJECT
