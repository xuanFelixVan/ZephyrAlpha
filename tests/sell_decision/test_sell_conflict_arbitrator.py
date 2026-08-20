"""SellConflictArbitrator 单元测试 (MOD-SELL-008)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.sell_decision.core.sell_conflict_arbitrator import (
    ArbitrationResult,
    ArbitrationVerdict,
    BuySignal,
    ConflictLevel,
    InvalidArbitrationInputError,
    SellArbitratedEvent,
    SellConflictArbitrator,
    Side,
)
from zephyr.sell_decision.core.sell_signal_collector import (
    SellDirection,
    SellSignal,
    SellSignalType,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


# ── 测试数据工厂 ─────────────────────────────────────────────────────────────


def sell(
    symbol="000001.SZ", stype=SellSignalType.MAIN_FORCE_DISTRIBUTION, confidence=0.9, source="", **kw
) -> SellSignal:
    return SellSignal(
        symbol=symbol,
        signal_type=stype,
        direction=SellDirection.CLEAR,
        confidence=confidence,
        source=source,
        **kw,
    )


def buy(symbol="000001.SZ", confidence=0.7) -> BuySignal:
    return BuySignal(symbol=symbol, confidence=confidence)


# ── 无冲突 ────────────────────────────────────────────────────────────────────


def test_no_conflict_when_no_buy_opponent():
    """卖出信号无买入对手 → NO_CONFLICT 直通。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate([sell()], [], now=T0)
    assert len(results) == 1
    r = results[0]
    assert r.verdict is ArbitrationVerdict.NO_CONFLICT
    assert r.conflict_level is ConflictLevel.NONE
    assert r.winning_side is Side.NONE
    assert r.delay_ticks == 0


def test_empty_sell_signals_returns_empty():
    """无卖出信号 → 空结果(SELL-08 只处理有卖出信号的标的)。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate([], [buy()], now=T0)
    assert results == []


# ── 强冲突 → SELL_PRIORITY ────────────────────────────────────────────────────


def test_strong_conflict_main_force_distribution():
    """主力出货 → 强冲突 → SELL_PRIORITY 立即执行(0延迟)。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)],
        [buy()],
        now=T0,
    )
    r = results[0]
    assert r.verdict is ArbitrationVerdict.SELL_PRIORITY
    assert r.conflict_level is ConflictLevel.STRONG
    assert r.winning_side is Side.SELL
    assert r.delay_ticks == 0


def test_strong_conflict_breakout_failure():
    """突破失败 → 强冲突 → SELL_PRIORITY。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [sell(stype=SellSignalType.BREAKOUT_FAILURE)],
        [buy()],
        now=T0,
    )
    assert results[0].verdict is ArbitrationVerdict.SELL_PRIORITY
    assert results[0].conflict_level is ConflictLevel.STRONG


def test_strong_conflict_risk_source():
    """source 含 RISK → 风控强制 → 强冲突。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [sell(stype=SellSignalType.TECHNICAL, source="D-RISK-force")],
        [buy()],
        now=T0,
    )
    r = results[0]
    assert r.conflict_level is ConflictLevel.STRONG
    assert r.verdict is ArbitrationVerdict.SELL_PRIORITY


def test_strong_conflict_risk_metadata():
    """metadata.risk_force=True → 风控强制 → 强冲突。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [sell(stype=SellSignalType.TECHNICAL, metadata={"risk_force": True})],
        [buy()],
        now=T0,
    )
    assert results[0].conflict_level is ConflictLevel.STRONG


# ── 弱冲突 → DELAYED_OBSERVE ──────────────────────────────────────────────────


def test_weak_conflict_opportunity_cost():
    """止盈/置换(OPPORTUNITY_COST) → 弱冲突 → DELAYED_OBSERVE 延迟1 Tick。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [sell(stype=SellSignalType.OPPORTUNITY_COST)],
        [buy()],
        now=T0,
    )
    r = results[0]
    assert r.verdict is ArbitrationVerdict.DELAYED_OBSERVE
    assert r.conflict_level is ConflictLevel.WEAK
    assert r.winning_side is Side.SELL
    assert r.delay_ticks == 1


def test_weak_conflict_technical():
    """技术面卖出 → 弱冲突 → DELAYED_OBSERVE。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [sell(stype=SellSignalType.TECHNICAL)],
        [buy()],
        now=T0,
    )
    assert results[0].verdict is ArbitrationVerdict.DELAYED_OBSERVE
    assert results[0].delay_ticks == 1


def test_weak_conflict_mixed_strong_wins():
    """强弱混合 → 取最强(STRONG) → SELL_PRIORITY。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [
            sell(stype=SellSignalType.TECHNICAL),  # 弱
            sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION),  # 强
        ],
        [buy()],
        now=T0,
    )
    assert results[0].conflict_level is ConflictLevel.STRONG
    assert results[0].verdict is ArbitrationVerdict.SELL_PRIORITY


# ── 卖出优先铁律 ─────────────────────────────────────────────────────────────


def test_sell_priority_iron_law_always_sell_wins():
    """冲突时永远卖出方胜出(即使弱冲突)。"""
    arb = SellConflictArbitrator()
    for stype in SellSignalType:
        results = arb.arbitrate(
            [sell(stype=stype, confidence=0.1)],
            [buy(confidence=0.99)],  # 买入置信度远高于卖出
            now=T0,
        )
        r = results[0]
        if r.conflict_level is ConflictLevel.NONE:
            continue
        assert r.winning_side is Side.SELL, f"sell priority violated for {stype}"


# ── 多标的混合 ────────────────────────────────────────────────────────────────


def test_multi_symbol_mixed():
    """多标的混合: A强冲突 / B弱冲突 / C无冲突。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [
            sell(symbol="A", stype=SellSignalType.MAIN_FORCE_DISTRIBUTION),
            sell(symbol="B", stype=SellSignalType.TECHNICAL),
            sell(symbol="C", stype=SellSignalType.OPPORTUNITY_COST),
        ],
        [buy(symbol="A"), buy(symbol="B")],  # C 无买入对手
        now=T0,
    )
    assert len(results) == 3
    by_sym = {r.symbol: r for r in results}
    assert by_sym["A"].verdict is ArbitrationVerdict.SELL_PRIORITY
    assert by_sym["B"].verdict is ArbitrationVerdict.DELAYED_OBSERVE
    assert by_sym["C"].verdict is ArbitrationVerdict.NO_CONFLICT


def test_results_sorted_by_symbol():
    """结果按 symbol 排序。"""
    arb = SellConflictArbitrator()
    results = arb.arbitrate(
        [sell(symbol="C"), sell(symbol="A"), sell(symbol="B")],
        [],
        now=T0,
    )
    assert [r.symbol for r in results] == ["A", "B", "C"]


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_buy_signal_empty_symbol_raises():
    with pytest.raises(InvalidArbitrationInputError):
        BuySignal(symbol="", confidence=0.5)


def test_buy_signal_confidence_out_of_range_raises():
    with pytest.raises(InvalidArbitrationInputError):
        BuySignal(symbol="X", confidence=1.5)


def test_empty_strong_types_raises():
    with pytest.raises(InvalidArbitrationInputError):
        SellConflictArbitrator(strong_conflict_types=frozenset())


def test_negative_delay_raises():
    with pytest.raises(InvalidArbitrationInputError):
        SellConflictArbitrator(weak_delay_ticks=-1)


# ── 单标的异常隔离 ────────────────────────────────────────────────────────────


def test_single_symbol_exception_isolated(monkeypatch):
    """单标的异常不阻断其他标的。

    用 monkeypatch 向 _classify_conflict 注入异常, 模拟 BAD 标的仲裁失败,
    验证 GOOD 标的不受影响。
    """
    arb = SellConflictArbitrator()
    original_classify = arb._classify_conflict

    def patched_classify(sell_sigs: list[SellSignal]) -> ConflictLevel:
        for s in sell_sigs:
            if s.symbol == "BAD":
                raise RuntimeError("injected failure for BAD")
        return original_classify(sell_sigs)

    monkeypatch.setattr(arb, "_classify_conflict", patched_classify)

    bad_signal = sell(symbol="BAD", stype=SellSignalType.TECHNICAL)
    good_signal = sell(symbol="GOOD", stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)
    # BAD 必须有买入对手才会进入 _classify_conflict(否则走 NO_CONFLICT 直通)
    results = arb.arbitrate([bad_signal, good_signal], [buy("BAD"), buy("GOOD")], now=T0)
    # BAD 被隔离跳过, GOOD 正常仲裁
    symbols = [r.symbol for r in results]
    assert "GOOD" in symbols
    assert "BAD" not in symbols


# ── 事件发布 ──────────────────────────────────────────────────────────────────


def test_arbitrated_event_emitted_on_conflict():
    """冲突时发布 E-SELL-02 事件。"""
    arb = SellConflictArbitrator()
    events: list[SellArbitratedEvent] = []
    arb.on_arbitrated(events.append)
    arb.arbitrate([sell()], [buy()], now=T0)
    assert len(events) == 1
    assert events[0].result.symbol == "000001.SZ"
    assert events[0].context_snapshot["sell_count"] == 1
    assert events[0].context_snapshot["buy_count"] == 1


def test_no_event_when_no_conflict():
    """无冲突时不发布事件。"""
    arb = SellConflictArbitrator()
    events: list[SellArbitratedEvent] = []
    arb.on_arbitrated(events.append)
    arb.arbitrate([sell()], [], now=T0)  # 无买入对手
    assert events == []


def test_event_callback_exception_isolated():
    """回调异常不阻断主流程。"""
    arb = SellConflictArbitrator()

    def bad_cb(_e: SellArbitratedEvent) -> None:
        raise RuntimeError("callback boom")

    good_events: list[SellArbitratedEvent] = []
    arb.on_arbitrated(bad_cb)
    arb.on_arbitrated(good_events.append)
    results = arb.arbitrate([sell()], [buy()], now=T0)
    assert len(results) == 1  # 主流程未阻断
    assert len(good_events) == 1  # 后续回调仍执行


# ── 可配置性 ──────────────────────────────────────────────────────────────────


def test_custom_strong_types():
    """自定义强冲突类型集合。"""
    arb = SellConflictArbitrator(
        strong_conflict_types=frozenset({SellSignalType.FUNDAMENTAL}),
    )
    # FUNDAMENTAL 现在是强冲突
    results = arb.arbitrate(
        [sell(stype=SellSignalType.FUNDAMENTAL)],
        [buy()],
        now=T0,
    )
    assert results[0].conflict_level is ConflictLevel.STRONG
    # MAIN_FORCE_DISTRIBUTION 不再是强冲突(被自定义覆盖)
    results2 = arb.arbitrate(
        [sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)],
        [buy()],
        now=T0,
    )
    assert results2[0].conflict_level is ConflictLevel.WEAK


def test_custom_risk_marker():
    """自定义风控来源标识。"""
    arb = SellConflictArbitrator(risk_source_marker="wind-control")
    results = arb.arbitrate(
        [sell(stype=SellSignalType.TECHNICAL, source="d-wind-control-gw")],
        [buy()],
        now=T0,
    )
    assert results[0].conflict_level is ConflictLevel.STRONG


def test_custom_weak_delay_ticks():
    """自定义弱冲突延迟tick数。"""
    arb = SellConflictArbitrator(weak_delay_ticks=3)
    results = arb.arbitrate(
        [sell(stype=SellSignalType.TECHNICAL)],
        [buy()],
        now=T0,
    )
    assert results[0].delay_ticks == 3


# ── 审计字段 ──────────────────────────────────────────────────────────────────


def test_audit_fields_populated():
    """仲裁结果含审计字段(sell_signals/buy_signals/reason/timestamp)。"""
    arb = SellConflictArbitrator()
    s = sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)
    b = buy()
    results = arb.arbitrate([s], [b], now=T0)
    r = results[0]
    assert r.sell_signals == [s]
    assert r.buy_signals == [b]
    assert "000001.SZ" in r.reason
    assert r.timestamp == T0


def test_verdict_matches_ctr_sell_001_contract():
    """verdict 值匹配 CTR-SELL-001 conflict_arbitration 字段定义。"""
    assert ArbitrationVerdict.SELL_PRIORITY.value == "sell_priority"
    assert ArbitrationVerdict.DELAYED_OBSERVE.value == "delayed_observe"
    assert ArbitrationVerdict.NO_CONFLICT.value == "no_conflict"
