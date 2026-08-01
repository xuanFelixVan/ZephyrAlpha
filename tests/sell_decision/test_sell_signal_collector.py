"""SellSignalCollector 单元测试 (MOD-SELL-001)。

覆盖: 信号数据校验 / provider注册(callable+Protocol) / 收集聚合 / 去重 / 故障隔离 / 排序。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from zephyr.sell_decision.core.sell_signal_collector import (
    DuplicateProviderError,
    InvalidSellSignalError,
    SellDirection,
    SellSignal,
    SellSignalCollector,
    SellSignalType,
    SignalTimeFrame,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


def _sig(
    symbol: str = "000001.SZ",
    stype: SellSignalType = SellSignalType.TECHNICAL,
    direction: SellDirection = SellDirection.REDUCE,
    confidence: float = 0.5,
    **kw: Any,
) -> SellSignal:
    return SellSignal(symbol=symbol, signal_type=stype, direction=direction, confidence=confidence, **kw)


# ── SellSignal 数据校验 ───────────────────────────────────────────────────────


def test_sell_signal_creation():
    sig = _sig(confidence=0.8, source="tech_provider", reason="死叉")
    assert sig.symbol == "000001.SZ"
    assert sig.signal_type == SellSignalType.TECHNICAL
    assert sig.confidence == 0.8
    assert sig.dedup_key == ("000001.SZ", "TECHNICAL", "REDUCE")


def test_sell_signal_confidence_out_of_range_raises():
    with pytest.raises(InvalidSellSignalError):
        _sig(confidence=1.5)
    with pytest.raises(InvalidSellSignalError):
        _sig(confidence=-0.1)


def test_sell_signal_empty_symbol_raises():
    with pytest.raises(InvalidSellSignalError):
        SellSignal(symbol="", signal_type=SellSignalType.TECHNICAL, direction=SellDirection.CLEAR, confidence=0.5)


def test_sell_signal_boundary_confidence_ok():
    _sig(confidence=0.0)
    _sig(confidence=1.0)


def test_eight_signal_types_complete():
    assert len(SellSignalType) == 8


# ── Provider 注册 ─────────────────────────────────────────────────────────────


def test_register_callable_provider():
    collector = SellSignalCollector()

    def tech_provider(symbol, now, context):
        return [_sig(symbol=symbol, stype=SellSignalType.TECHNICAL, confidence=0.7)]

    collector.register(SellSignalType.TECHNICAL, tech_provider)
    assert SellSignalType.TECHNICAL in collector.registered_types


def test_register_protocol_object_provider():
    collector = SellSignalCollector()

    class MainForceProvider:
        signal_type = SellSignalType.MAIN_FORCE_DISTRIBUTION

        def provide(self, symbol, now, context):
            return [_sig(symbol=symbol, stype=SellSignalType.MAIN_FORCE_DISTRIBUTION, confidence=0.9)]

    collector.register(SellSignalType.MAIN_FORCE_DISTRIBUTION, MainForceProvider())
    assert SellSignalType.MAIN_FORCE_DISTRIBUTION in collector.registered_types


def test_duplicate_register_raises():
    collector = SellSignalCollector()
    collector.register(SellSignalType.TECHNICAL, lambda s, n, c: [])
    with pytest.raises(DuplicateProviderError):
        collector.register(SellSignalType.TECHNICAL, lambda s, n, c: [])


def test_unregister():
    collector = SellSignalCollector()
    collector.register(SellSignalType.TECHNICAL, lambda s, n, c: [])
    collector.unregister(SellSignalType.TECHNICAL)
    assert SellSignalType.TECHNICAL not in collector.registered_types


# ── 收集与去重 ────────────────────────────────────────────────────────────────


def test_collect_aggregates_multiple_types():
    collector = SellSignalCollector()
    collector.register(
        SellSignalType.TECHNICAL,
        lambda s, n, c: [_sig(symbol=s, stype=SellSignalType.TECHNICAL, confidence=0.6)],
    )
    collector.register(
        SellSignalType.MAIN_FORCE_DISTRIBUTION,
        lambda s, n, c: [_sig(symbol=s, stype=SellSignalType.MAIN_FORCE_DISTRIBUTION, confidence=0.9)],
    )
    signals = collector.collect("000001.SZ", now=T0)
    assert len(signals) == 2
    # 按 confidence 降序
    assert signals[0].confidence == 0.9
    assert signals[1].confidence == 0.6


def test_collect_dedup_keeps_highest_confidence():
    collector = SellSignalCollector()
    # 同 symbol+type+direction 两个信号, confidence 不同
    collector.register(
        SellSignalType.TECHNICAL,
        lambda s, n, c: [
            _sig(symbol=s, stype=SellSignalType.TECHNICAL, direction=SellDirection.REDUCE, confidence=0.5),
            _sig(symbol=s, stype=SellSignalType.TECHNICAL, direction=SellDirection.REDUCE, confidence=0.8),
        ],
    )
    signals = collector.collect("000001.SZ", now=T0)
    assert len(signals) == 1
    assert signals[0].confidence == 0.8


def test_collect_dedup_different_direction_kept():
    collector = SellSignalCollector()
    collector.register(
        SellSignalType.TECHNICAL,
        lambda s, n, c: [
            _sig(symbol=s, stype=SellSignalType.TECHNICAL, direction=SellDirection.REDUCE, confidence=0.5),
            _sig(symbol=s, stype=SellSignalType.TECHNICAL, direction=SellDirection.CLEAR, confidence=0.7),
        ],
    )
    signals = collector.collect("000001.SZ", now=T0)
    assert len(signals) == 2


def test_collect_sorted_by_confidence_desc():
    collector = SellSignalCollector()
    collector.register(
        SellSignalType.TECHNICAL,
        lambda s, n, c: [_sig(symbol=s, stype=SellSignalType.TECHNICAL, confidence=0.3)],
    )
    collector.register(
        SellSignalType.FUNDAMENTAL,
        lambda s, n, c: [_sig(symbol=s, stype=SellSignalType.FUNDAMENTAL, confidence=0.9)],
    )
    collector.register(
        SellSignalType.VOLUME_PRICE_DIVERGENCE,
        lambda s, n, c: [_sig(symbol=s, stype=SellSignalType.VOLUME_PRICE_DIVERGENCE, confidence=0.6)],
    )
    signals = collector.collect("000001.SZ", now=T0)
    confs = [s.confidence for s in signals]
    assert confs == [0.9, 0.6, 0.3]


def test_collect_empty_when_no_providers():
    collector = SellSignalCollector()
    assert collector.collect("000001.SZ", now=T0) == []


def test_collect_empty_when_provider_returns_empty():
    collector = SellSignalCollector()
    collector.register(SellSignalType.TECHNICAL, lambda s, n, c: [])
    assert collector.collect("000001.SZ", now=T0) == []


# ── 故障隔离 ──────────────────────────────────────────────────────────────────


def test_collect_isolates_provider_failure():
    collector = SellSignalCollector()

    def bad_provider(s, n, c):
        raise RuntimeError("boom")

    collector.register(SellSignalType.TECHNICAL, bad_provider)
    collector.register(
        SellSignalType.FUNDAMENTAL,
        lambda s, n, c: [_sig(symbol=s, stype=SellSignalType.FUNDAMENTAL, confidence=0.8)],
    )
    signals = collector.collect("000001.SZ", now=T0)
    # 故障 provider 被跳过, 正常 provider 仍产出
    assert len(signals) == 1
    assert signals[0].signal_type == SellSignalType.FUNDAMENTAL


# ── context 传递 ──────────────────────────────────────────────────────────────


def test_collect_passes_context_to_provider():
    collector = SellSignalCollector()
    received: dict[str, Any] = {}

    def provider(s, n, c):
        received.update(c)
        return []

    collector.register(SellSignalType.TECHNICAL, provider)
    collector.collect("000001.SZ", now=T0, context={"position_state": "OBSERVING", "nav": 1_000_000})
    assert received["position_state"] == "OBSERVING"
    assert received["nav"] == 1_000_000


# ── timeframe ─────────────────────────────────────────────────────────────────


def test_signal_with_timeframe():
    sig = _sig(timeframe=SignalTimeFrame.DAILY)
    assert sig.timeframe == SignalTimeFrame.DAILY
