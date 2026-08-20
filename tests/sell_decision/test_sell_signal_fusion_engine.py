# [BLUEPRINT] MOD-SELL-017 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""SellSignalFusionEngine 单元测试 (MOD-SELL-007)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.sell_decision.core.sell_signal_collector import (
    SellDirection,
    SellSignal,
    SellSignalType,
    SignalTimeFrame,
)
from zephyr.sell_decision.core.sell_signal_fusion_engine import (
    ConsistencyLevel,
    FusedSellDecision,
    FusionMethod,
    InvalidFusionInputError,
    SellSignalFusedEvent,
    SellSignalFusionEngine,
    WeightedAverageFusion,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


# ── 测试数据工厂 ─────────────────────────────────────────────────────────────


def sell(
    symbol="000001.SZ",
    stype=SellSignalType.MAIN_FORCE_DISTRIBUTION,
    direction=SellDirection.CLEAR,
    confidence=0.9,
    timeframe=SignalTimeFrame.DAILY,
    **kw,
) -> SellSignal:
    return SellSignal(
        symbol=symbol,
        signal_type=stype,
        direction=direction,
        confidence=confidence,
        timeframe=timeframe,
        **kw,
    )


# ── 单信号融合 ───────────────────────────────────────────────────────────────


def test_single_signal_willingness_equals_confidence():
    """单信号: willingness=confidence, 一致性 HIGH(100%同方向)。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse([sell(confidence=0.9)], now=T0)
    d = decisions[0]
    assert d.willingness == pytest.approx(0.9)
    assert d.confidence == pytest.approx(0.9)  # HIGH × 1.0
    assert d.consistency is ConsistencyLevel.HIGH


def test_single_signal_dominant_type():
    engine = SellSignalFusionEngine()
    decisions = engine.fuse([sell(stype=SellSignalType.TECHNICAL)], now=T0)
    assert decisions[0].dominant_signal_type is SellSignalType.TECHNICAL


# ── 多信号加权平均 ───────────────────────────────────────────────────────────


def test_multi_signal_weighted_average():
    """主力(0.9,w1.5) + 止盈(0.3,w0.6) → 加权平均。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION, confidence=0.9),
            sell(stype=SellSignalType.OPPORTUNITY_COST, confidence=0.3),
        ],
        now=T0,
    )
    # (0.9×1.5 + 0.3×0.6) / (1.5+0.6) = 1.53/2.1 ≈ 0.7286
    assert decisions[0].willingness == pytest.approx(0.7286, abs=1e-3)


def test_type_weight_differentiation():
    """同 confidence 不同 type → 主导信号为高权重类型。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION, confidence=0.5),  # w1.5
            sell(stype=SellSignalType.OPPORTUNITY_COST, confidence=0.5),  # w0.6
        ],
        now=T0,
    )
    assert decisions[0].dominant_signal_type is SellSignalType.MAIN_FORCE_DISTRIBUTION


# ── 多时间框架共振 ───────────────────────────────────────────────────────────


def test_resonance_enhanced_multi_timeframe():
    """同方向多时间框架 → 权重 ×1.5, resonance_enhanced=True。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(stype=SellSignalType.TECHNICAL, confidence=0.7, timeframe=SignalTimeFrame.DAILY),
            sell(stype=SellSignalType.TECHNICAL, confidence=0.7, timeframe=SignalTimeFrame.HOUR_60),
        ],
        now=T0,
    )
    d = decisions[0]
    assert d.resonance_enhanced is True
    # 两信号同 confidence, 共振权重×1.5 → willingness 仍=0.7(归一), 但 confidence 受一致性影响
    assert d.willingness == pytest.approx(0.7)


def test_no_resonance_different_direction():
    """不同方向不触发共振。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(direction=SellDirection.CLEAR, timeframe=SignalTimeFrame.DAILY, confidence=0.7),
            sell(direction=SellDirection.REDUCE, timeframe=SignalTimeFrame.HOUR_60, confidence=0.7),
        ],
        now=T0,
    )
    assert decisions[0].resonance_enhanced is False


def test_no_resonance_unknown_timeframe():
    """UNKNOWN 时间框架不触发共振。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(timeframe=SignalTimeFrame.UNKNOWN, confidence=0.7),
            sell(timeframe=SignalTimeFrame.UNKNOWN, confidence=0.7),
        ],
        now=T0,
    )
    assert decisions[0].resonance_enhanced is False


# ── 一致性三档 ───────────────────────────────────────────────────────────────


def test_consistency_high():
    """3 个同方向 → HIGH(100%)。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(stype=SellSignalType.TECHNICAL, direction=SellDirection.CLEAR, confidence=0.6),
            sell(stype=SellSignalType.FUNDAMENTAL, direction=SellDirection.CLEAR, confidence=0.7),
            sell(stype=SellSignalType.RELATIVE_STRENGTH, direction=SellDirection.CLEAR, confidence=0.5),
        ],
        now=T0,
    )
    assert decisions[0].consistency is ConsistencyLevel.HIGH


def test_consistency_medium():
    """2 同 1 异 → 66.7% → MEDIUM。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(direction=SellDirection.CLEAR, confidence=0.6),
            sell(direction=SellDirection.CLEAR, confidence=0.7),
            sell(direction=SellDirection.REDUCE, confidence=0.5),
        ],
        now=T0,
    )
    assert decisions[0].consistency is ConsistencyLevel.MEDIUM


def test_consistency_low():
    """3 个不同方向 → 33.3% → LOW。"""
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(direction=SellDirection.CLEAR, confidence=0.6),
            sell(direction=SellDirection.REDUCE, confidence=0.7),
            sell(direction=SellDirection.REPLACE, confidence=0.5),
        ],
        now=T0,
    )
    assert decisions[0].consistency is ConsistencyLevel.LOW


# ── 融合置信度 ───────────────────────────────────────────────────────────────


def test_confidence_affected_by_consistency():
    """一致性低 → 置信度打折。"""
    engine = SellSignalFusionEngine()
    # HIGH 一致性
    d_high = engine.fuse(
        [sell(confidence=0.8), sell(confidence=0.8)],  # 同方向
        now=T0,
    )[0]
    # LOW 一致性
    d_low = engine.fuse(
        [
            sell(direction=SellDirection.CLEAR, confidence=0.8),
            sell(direction=SellDirection.REDUCE, confidence=0.8),
            sell(direction=SellDirection.REPLACE, confidence=0.8),
        ],
        now=T0,
    )[0]
    assert d_high.confidence > d_low.confidence
    assert d_low.confidence == pytest.approx(d_low.willingness * 0.5)


def test_confidence_bounded_0_1():
    engine = SellSignalFusionEngine()
    decisions = engine.fuse([sell(confidence=1.0)], now=T0)
    assert 0.0 <= decisions[0].confidence <= 1.0


# ── 多标的混合 ───────────────────────────────────────────────────────────────


def test_multi_symbol_mixed():
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [
            sell(symbol="A", confidence=0.9),
            sell(symbol="B", confidence=0.3),
        ],
        now=T0,
    )
    assert len(decisions) == 2
    by_sym = {d.symbol: d for d in decisions}
    assert by_sym["A"].willingness > by_sym["B"].willingness


def test_results_sorted_by_symbol():
    engine = SellSignalFusionEngine()
    decisions = engine.fuse(
        [sell(symbol="C"), sell(symbol="A"), sell(symbol="B")],
        now=T0,
    )
    assert [d.symbol for d in decisions] == ["A", "B", "C"]


# ── 输入校验 ─────────────────────────────────────────────────────────────────


def test_empty_signals_raises():
    engine = SellSignalFusionEngine()
    with pytest.raises(InvalidFusionInputError):
        engine.fuse([], now=T0)


# ── 单标的异常隔离 ────────────────────────────────────────────────────────────


def test_single_symbol_exception_isolated(monkeypatch):
    engine = SellSignalFusionEngine()
    original = engine._signal_weight

    def patched(sig, all_sigs):
        if sig.symbol == "BAD":
            raise RuntimeError("injected")
        return original(sig, all_sigs)

    monkeypatch.setattr(engine, "_signal_weight", patched)
    decisions = engine.fuse(
        [sell(symbol="BAD"), sell(symbol="GOOD", confidence=0.8)],
        now=T0,
    )
    symbols = [d.symbol for d in decisions]
    assert "GOOD" in symbols
    assert "BAD" not in symbols


# ── 可配置性 ─────────────────────────────────────────────────────────────────


def test_custom_type_weights():
    """自定义 signal_type 权重。"""
    custom_weights = {stype: 1.0 for stype in SellSignalType}
    custom_weights[SellSignalType.OPPORTUNITY_COST] = 2.0  # 止盈权重最高
    strategy = WeightedAverageFusion(type_weights=custom_weights)
    engine = SellSignalFusionEngine(strategy=strategy)
    decisions = engine.fuse(
        [
            sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION, confidence=0.5),
            sell(stype=SellSignalType.OPPORTUNITY_COST, confidence=0.5),
        ],
        now=T0,
    )
    assert decisions[0].dominant_signal_type is SellSignalType.OPPORTUNITY_COST


def test_custom_resonance_boost():
    """自定义共振增强因子。"""
    engine = SellSignalFusionEngine(resonance_boost=3.0)
    decisions = engine.fuse(
        [
            sell(stype=SellSignalType.TECHNICAL, confidence=0.9, timeframe=SignalTimeFrame.DAILY),
            sell(stype=SellSignalType.TECHNICAL, confidence=0.5, timeframe=SignalTimeFrame.HOUR_60),
        ],
        now=T0,
    )
    # 共振信号权重×3.0 → 高 confidence 信号主导
    d = decisions[0]
    assert d.resonance_enhanced is True


# ── 事件发布 ─────────────────────────────────────────────────────────────────


def test_fused_event_emitted():
    engine = SellSignalFusionEngine()
    events: list[SellSignalFusedEvent] = []
    engine.on_fused(events.append)
    engine.fuse([sell(confidence=0.8)], now=T0)
    assert len(events) == 1
    assert events[0].decision.symbol == "000001.SZ"
    assert events[0].context_snapshot["signal_count"] == 1


def test_event_callback_exception_isolated():
    engine = SellSignalFusionEngine()

    def bad_cb(_e: SellSignalFusedEvent) -> None:
        raise RuntimeError("boom")

    good_events: list[SellSignalFusedEvent] = []
    engine.on_fused(bad_cb)
    engine.on_fused(good_events.append)
    decisions = engine.fuse([sell(confidence=0.8)], now=T0)
    assert len(decisions) == 1
    assert len(good_events) == 1


# ── 融合方法标记 ─────────────────────────────────────────────────────────────


def test_default_fusion_method_weighted_avg():
    engine = SellSignalFusionEngine()
    decisions = engine.fuse([sell(confidence=0.8)], now=T0)
    assert decisions[0].fusion_method is FusionMethod.WEIGHTED_AVG


# ── 审计字段 ─────────────────────────────────────────────────────────────────


def test_audit_fields_populated():
    engine = SellSignalFusionEngine()
    s1 = sell(stype=SellSignalType.TECHNICAL, confidence=0.7)
    decisions = engine.fuse([s1], now=T0)
    d = decisions[0]
    assert d.contributing_signals == [s1]
    assert "willingness" in d.reason
    assert d.timestamp == T0
