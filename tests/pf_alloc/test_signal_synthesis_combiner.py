"""SignalSynthesisCombiner 单元测试 (MOD-PA-002)。

覆盖: 信号校验 / 多策略投票 / 共振级别 / 冲突裁决 / 决策去重 / 仓位合并+截断 / calibrator。
"""

from __future__ import annotations

from typing import Any

import pytest

from zephyr.pf_alloc.core.signal_synthesis_combiner import (
    ConfidenceCalibrator,
    InvalidStrategySignalError,
    ResonanceLevel,
    SignalDirection,
    SignalSynthesisCombiner,
    StrategySignal,
)

# ── StrategySignal 校验 ───────────────────────────────────────────────────────


def test_strategy_signal_validation():
    with pytest.raises(InvalidStrategySignalError):
        StrategySignal("", "000001.SZ", SignalDirection.LONG, 0.5)
    with pytest.raises(InvalidStrategySignalError):
        StrategySignal("s1", "000001.SZ", SignalDirection.LONG, 1.5)
    with pytest.raises(InvalidStrategySignalError):
        StrategySignal("s1", "000001.SZ", SignalDirection.LONG, 0.5, weight=2.0)


def test_direction_sign():
    assert SignalDirection.LONG.sign == 1.0
    assert SignalDirection.SHORT.sign == -1.0
    assert SignalDirection.NEUTRAL.sign == 0.0


# ── 多策略投票 ────────────────────────────────────────────────────────────────


def test_weighted_voting_long():
    """两个LONG策略, 综合得分=Σ(weight×sign×conf×sensitivity)。"""
    sigs = [
        StrategySignal("a", "000001.SZ", SignalDirection.LONG, 0.8, weight=0.5),
        StrategySignal("b", "000001.SZ", SignalDirection.LONG, 0.6, weight=0.5),
    ]
    result = SignalSynthesisCombiner().combine(sigs)
    assert len(result) == 1
    r = result[0]
    # composite = 0.5×1×0.8×1 + 0.5×1×0.6×1 = 0.7
    assert r.composite_score == pytest.approx(0.7)
    assert r.direction == SignalDirection.LONG
    # confidence = |0.7| / (0.5+0.5) = 0.7
    assert r.confidence == pytest.approx(0.7)
    assert r.resonance == ResonanceLevel.STRONG
    assert set(r.contributing_strategies) == {"a", "b"}
    assert r.conflict is False


def test_multiple_symbols_grouped():
    sigs = [
        StrategySignal("a", "000001.SZ", SignalDirection.LONG, 0.8, weight=1.0),
        StrategySignal("a", "600000.SH", SignalDirection.SHORT, 0.7, weight=1.0),
    ]
    result = SignalSynthesisCombiner().combine(sigs)
    assert len(result) == 2
    symbols = {r.symbol for r in result}
    assert symbols == {"000001.SZ", "600000.SH"}


# ── 共振级别 ──────────────────────────────────────────────────────────────────


def test_resonance_strong_all_same_direction():
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.5, weight=0.34),
        StrategySignal("b", "X", SignalDirection.LONG, 0.5, weight=0.33),
        StrategySignal("c", "X", SignalDirection.LONG, 0.5, weight=0.33),
    ]
    r = SignalSynthesisCombiner().combine(sigs)[0]
    assert r.resonance == ResonanceLevel.STRONG


def test_resonance_moderate_two_thirds():
    # 2 LONG + 1 SHORT → 同向 2/3 → MODERATE
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.5, weight=0.34),
        StrategySignal("b", "X", SignalDirection.LONG, 0.5, weight=0.33),
        StrategySignal("c", "X", SignalDirection.SHORT, 0.5, weight=0.33),
    ]
    r = SignalSynthesisCombiner().combine(sigs)[0]
    assert r.resonance == ResonanceLevel.MODERATE


def test_resonance_weak_diverged():
    # 1 LONG + 1 SHORT → 1/2 < 2/3 → WEAK
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.5, weight=0.5),
        StrategySignal("b", "X", SignalDirection.SHORT, 0.5, weight=0.5),
    ]
    r = SignalSynthesisCombiner().combine(sigs)[0]
    assert r.resonance == ResonanceLevel.WEAK


# ── 冲突检测 + 裁决 ───────────────────────────────────────────────────────────


def test_conflict_detected_and_resolved_by_priority():
    # LONG 优先级 1 vs SHORT 优先级 3 → SHORT 胜
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.9, weight=0.5, priority=1),
        StrategySignal("b", "X", SignalDirection.SHORT, 0.5, weight=0.5, priority=3),
    ]
    r = SignalSynthesisCombiner().combine(sigs)[0]
    assert r.conflict is True
    assert "priority->SHORT" in r.conflict_resolution


def test_conflict_priority_tie_resolved_by_majority():
    # 2 LONG(优先级1) + 1 SHORT(优先级1) → 平局, 多数 LONG 胜
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.5, weight=0.34, priority=1),
        StrategySignal("b", "X", SignalDirection.LONG, 0.5, weight=0.33, priority=1),
        StrategySignal("c", "X", SignalDirection.SHORT, 0.5, weight=0.33, priority=1),
    ]
    r = SignalSynthesisCombiner().combine(sigs)[0]
    assert r.conflict is True
    assert "priority->LONG" in r.conflict_resolution


# ── 仓位合并 + 截断 ───────────────────────────────────────────────────────────


def test_position_merge_sum_within_cap():
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.5, weight=1.0, target_weight=0.3),
        StrategySignal("b", "X", SignalDirection.LONG, 0.5, weight=1.0, target_weight=0.2),
    ]
    r = SignalSynthesisCombiner(position_cap=1.0).combine(sigs)[0]
    assert r.merged_position_weight == pytest.approx(0.5)


def test_position_merge_truncated_at_cap():
    # cap=0.5, 两个0.3 → 0.3+0.3=0.6 截断到 0.5
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.5, weight=1.0, target_weight=0.3, priority=2),
        StrategySignal("b", "X", SignalDirection.LONG, 0.5, weight=1.0, target_weight=0.3, priority=1),
    ]
    r = SignalSynthesisCombiner(position_cap=0.5).combine(sigs)[0]
    assert r.merged_position_weight == pytest.approx(0.5)


def test_position_cap_validation():
    with pytest.raises(InvalidStrategySignalError):
        SignalSynthesisCombiner(position_cap=0.0)
    with pytest.raises(InvalidStrategySignalError):
        SignalSynthesisCombiner(position_cap=1.5)


def test_position_merge_conflict_only_winning_direction():
    # 冲突: LONG 胜(优先级高), 只合并 LONG 的仓位
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.9, weight=0.5, priority=3, target_weight=0.3),
        StrategySignal("b", "X", SignalDirection.SHORT, 0.5, weight=0.5, priority=1, target_weight=0.4),
    ]
    r = SignalSynthesisCombiner(position_cap=1.0).combine(sigs)[0]
    # 合成方向 LONG(优先级高), 只合并 LONG 的 0.3
    assert r.direction == SignalDirection.LONG
    assert r.merged_position_weight == pytest.approx(0.3)


# ── calibrator 注入 ───────────────────────────────────────────────────────────


def test_calibrator_applied():
    class DoubleCalibrator:
        def calibrate(self, confidence: float, strategy_id: str, context: dict[str, Any] | None = None) -> float:
            # 简单校准: 压缩到一半
            return confidence * 0.5

    sigs = [StrategySignal("a", "X", SignalDirection.LONG, 0.8, weight=1.0)]
    r = SignalSynthesisCombiner(calibrator=DoubleCalibrator()).combine(sigs)[0]
    # composite = 1.0 × 1 × (0.8×0.5) × 1 = 0.4
    assert r.composite_score == pytest.approx(0.4)


# ── NEUTRAL ───────────────────────────────────────────────────────────────────


def test_neutral_direction_zero_score():
    sigs = [StrategySignal("a", "X", SignalDirection.NEUTRAL, 0.5, weight=1.0)]
    r = SignalSynthesisCombiner().combine(sigs)[0]
    assert r.direction == SignalDirection.NEUTRAL
    assert r.composite_score == 0.0
    assert r.confidence == 0.0


# ── 决策去重 ──────────────────────────────────────────────────────────────────


def test_dedup_same_symbol_combined_into_one():
    # 同标的3个策略信号 → 合成1条
    sigs = [
        StrategySignal("a", "X", SignalDirection.LONG, 0.5, weight=0.34),
        StrategySignal("b", "X", SignalDirection.LONG, 0.6, weight=0.33),
        StrategySignal("c", "X", SignalDirection.LONG, 0.7, weight=0.33),
    ]
    result = SignalSynthesisCombiner().combine(sigs)
    assert len(result) == 1
    assert len(result[0].contributing_strategies) == 3
