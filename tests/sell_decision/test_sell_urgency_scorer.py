"""SellUrgencyScorer 单元测试 (MOD-SELL-009)。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.sell_decision.core.sell_conflict_arbitrator import (
    ArbitrationResult,
    ArbitrationVerdict,
    ConflictLevel,
    Side,
)
from zephyr.sell_decision.core.sell_signal_collector import (
    SellDirection,
    SellSignal,
    SellSignalType,
)
from zephyr.sell_decision.core.sell_urgency_scorer import (
    ExecutionStrategy,
    InvalidUrgencyInputError,
    SellUrgencyScore,
    SellUrgencyScorer,
    UrgencyLevel,
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


def arb(symbol="000001.SZ", level=ConflictLevel.STRONG) -> ArbitrationResult:
    return ArbitrationResult(
        symbol=symbol,
        verdict=(
            ArbitrationVerdict.SELL_PRIORITY
            if level is ConflictLevel.STRONG
            else ArbitrationVerdict.DELAYED_OBSERVE
            if level is ConflictLevel.WEAK
            else ArbitrationVerdict.NO_CONFLICT
        ),
        conflict_level=level,
        winning_side=Side.SELL if level is not ConflictLevel.NONE else Side.NONE,
        delay_ticks=0 if level is ConflictLevel.STRONG else 1,
    )


# ── 单信号紧迫度映射 ─────────────────────────────────────────────────────────


def test_urgency_main_force_distribution():
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)], now=T0)
    assert scores[0].urgency == pytest.approx(1.0)
    assert scores[0].level is UrgencyLevel.URGENT
    assert scores[0].strategy is ExecutionStrategy.MARKET_FAST


def test_urgency_breakout_failure():
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.BREAKOUT_FAILURE)], now=T0)
    assert scores[0].urgency == pytest.approx(1.0)


def test_urgency_technical():
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.TECHNICAL)], now=T0)
    assert scores[0].urgency == pytest.approx(0.6)
    assert scores[0].level is UrgencyLevel.MODERATE
    assert scores[0].strategy is ExecutionStrategy.LIMITED_TIME


def test_urgency_opportunity_cost():
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.OPPORTUNITY_COST)], now=T0)
    assert scores[0].urgency == pytest.approx(0.3)
    assert scores[0].level is UrgencyLevel.RELAXED
    assert scores[0].strategy is ExecutionStrategy.PATIENT_LIMIT


def test_urgency_all_8_types_mapped():
    """8类 signal_type 都有映射, 无遗漏。"""
    scorer = SellUrgencyScorer()
    for stype in SellSignalType:
        scores = scorer.score([sell(stype=stype)], now=T0)
        assert len(scores) == 1
        assert 0.0 <= scores[0].urgency <= 1.0


# ── 风控信号 → 1.0 ────────────────────────────────────────────────────────────


def test_risk_source_signal_urgency_1():
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [sell(stype=SellSignalType.TECHNICAL, source="D-RISK-force")],
        now=T0,
    )
    assert scores[0].urgency == pytest.approx(1.0)
    assert scores[0].level is UrgencyLevel.URGENT


def test_risk_metadata_signal_urgency_1():
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [sell(stype=SellSignalType.TECHNICAL, metadata={"risk_force": True})],
        now=T0,
    )
    assert scores[0].urgency == pytest.approx(1.0)


# ── 多信号取最大 ─────────────────────────────────────────────────────────────


def test_multi_signal_takes_max():
    """主力(1.0) + 止盈(0.3) → 取最大 1.0。"""
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [
            sell(stype=SellSignalType.OPPORTUNITY_COST),  # 0.3
            sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION),  # 1.0
        ],
        now=T0,
    )
    assert scores[0].urgency == pytest.approx(1.0)
    assert scores[0].dominant_signal_type is SellSignalType.MAIN_FORCE_DISTRIBUTION
    assert scores[0].contributing_count == 2


def test_multi_signal_all_weak_takes_max():
    """止盈(0.3) + 技术面(0.6) → 取 0.6。"""
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [
            sell(stype=SellSignalType.OPPORTUNITY_COST),  # 0.3
            sell(stype=SellSignalType.TECHNICAL),  # 0.6
        ],
        now=T0,
    )
    assert scores[0].urgency == pytest.approx(0.6)


# ── 执行策略三档 ─────────────────────────────────────────────────────────────


def test_strategy_market_fast():
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)], now=T0)
    assert scores[0].strategy is ExecutionStrategy.MARKET_FAST


def test_strategy_limited_time():
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.TECHNICAL)], now=T0)
    assert scores[0].strategy is ExecutionStrategy.LIMITED_TIME


def test_strategy_patient_limit():
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.OPPORTUNITY_COST)], now=T0)
    assert scores[0].strategy is ExecutionStrategy.PATIENT_LIMIT


# ── 冲突增强 ─────────────────────────────────────────────────────────────────


def test_conflict_enhance_strong():
    """弱信号(0.3) + STRONG仲裁 → 增强至 0.9。"""
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [sell(stype=SellSignalType.OPPORTUNITY_COST)],  # 0.3
        arbitration_results=[arb(level=ConflictLevel.STRONG)],
        now=T0,
    )
    assert scores[0].urgency == pytest.approx(0.9)
    assert scores[0].conflict_enhanced is True
    assert scores[0].strategy is ExecutionStrategy.MARKET_FAST  # 0.9 > 0.8


def test_conflict_enhance_strong_not_lowered():
    """强信号(1.0) + STRONG仲裁 → 不降低(已超 floor)。"""
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)],  # 1.0
        arbitration_results=[arb(level=ConflictLevel.STRONG)],
        now=T0,
    )
    assert scores[0].urgency == pytest.approx(1.0)
    assert scores[0].conflict_enhanced is False  # 未被增强(已超floor)


def test_conflict_enhance_weak_not_enhanced():
    """弱信号(0.3) + WEAK仲裁 → 不增强。"""
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [sell(stype=SellSignalType.OPPORTUNITY_COST)],  # 0.3
        arbitration_results=[arb(level=ConflictLevel.WEAK)],
        now=T0,
    )
    assert scores[0].urgency == pytest.approx(0.3)
    assert scores[0].conflict_enhanced is False


def test_no_arbitration_result_normal_scoring():
    """无仲裁结果时正常评分(不增强)。"""
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.TECHNICAL)], now=T0)
    assert scores[0].urgency == pytest.approx(0.6)
    assert scores[0].conflict_enhanced is False


# ── 多标的混合 ───────────────────────────────────────────────────────────────


def test_multi_symbol_mixed():
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [
            sell(symbol="A", stype=SellSignalType.MAIN_FORCE_DISTRIBUTION),  # 1.0
            sell(symbol="B", stype=SellSignalType.OPPORTUNITY_COST),  # 0.3
            sell(symbol="C", stype=SellSignalType.TECHNICAL),  # 0.6
        ],
        now=T0,
    )
    assert len(scores) == 3
    by_sym = {s.symbol: s for s in scores}
    assert by_sym["A"].urgency == pytest.approx(1.0)
    assert by_sym["B"].urgency == pytest.approx(0.3)
    assert by_sym["C"].urgency == pytest.approx(0.6)


def test_results_sorted_by_symbol():
    scorer = SellUrgencyScorer()
    scores = scorer.score(
        [sell(symbol="C"), sell(symbol="A"), sell(symbol="B")],
        now=T0,
    )
    assert [s.symbol for s in scores] == ["A", "B", "C"]


# ── 输入校验 ─────────────────────────────────────────────────────────────────


def test_empty_signals_raises():
    scorer = SellUrgencyScorer()
    with pytest.raises(InvalidUrgencyInputError):
        scorer.score([], now=T0)


# ── 单标的异常隔离 ────────────────────────────────────────────────────────────


def test_single_symbol_exception_isolated(monkeypatch):
    """单标的评分异常不阻断其他标的。"""
    scorer = SellUrgencyScorer()
    original = scorer._signal_urgency

    def patched(sig: SellSignal) -> float:
        if sig.symbol == "BAD":
            raise RuntimeError("injected failure")
        return original(sig)

    monkeypatch.setattr(scorer, "_signal_urgency", patched)

    results = scorer.score(
        [sell(symbol="BAD"), sell(symbol="GOOD", stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)],
        now=T0,
    )
    symbols = [s.symbol for s in results]
    assert "GOOD" in symbols
    assert "BAD" not in symbols


# ── 可配置性 ─────────────────────────────────────────────────────────────────


def test_custom_urgency_map():
    """自定义 signal_type → 紧迫度映射。"""
    custom = {
        SellSignalType.TECHNICAL: 1.0,  # 提升技术面到紧急
        SellSignalType.MAIN_FORCE_DISTRIBUTION: 0.3,  # 降低主力到从容
    }
    scorer = SellUrgencyScorer(urgency_map=custom)
    scores = scorer.score([sell(stype=SellSignalType.TECHNICAL)], now=T0)
    assert scores[0].urgency == pytest.approx(1.0)
    scores2 = scorer.score([sell(stype=SellSignalType.MAIN_FORCE_DISTRIBUTION)], now=T0)
    assert scores2[0].urgency == pytest.approx(0.3)


def test_custom_conflict_enhance_floor():
    """自定义冲突增强下限。"""
    scorer = SellUrgencyScorer(conflict_enhance_floor=0.7)
    scores = scorer.score(
        [sell(stype=SellSignalType.OPPORTUNITY_COST)],  # 0.3
        arbitration_results=[arb(level=ConflictLevel.STRONG)],
        now=T0,
    )
    assert scores[0].urgency == pytest.approx(0.7)


# ── 审计字段 ─────────────────────────────────────────────────────────────────


def test_audit_fields_populated():
    scorer = SellUrgencyScorer()
    scores = scorer.score([sell(stype=SellSignalType.TECHNICAL)], now=T0)
    s = scores[0]
    assert s.dominant_signal_type is SellSignalType.TECHNICAL
    assert s.contributing_count == 1
    assert "TECHNICAL" in s.reason
    assert s.timestamp == T0


def test_unknown_signal_type_defaults_moderate():
    """未知 signal_type(不在映射里)→ 默认 0.5 中等。

    注: SellSignalType 是封闭枚举, 此测试用 monkeypatch 注入非法值验证兜底。
    """
    scorer = SellUrgencyScorer()
    sig = sell(stype=SellSignalType.TECHNICAL)
    # 替换为不在 urgency_map 的值(模拟未来新增类型)
    monkeypatch_target = SellSignalType.TECHNICAL
    # 用空映射, 使所有类型都"未知"
    empty_map_scorer = SellUrgencyScorer(urgency_map={})
    scores = empty_map_scorer.score([sig], now=T0)
    assert scores[0].urgency == pytest.approx(0.5)
