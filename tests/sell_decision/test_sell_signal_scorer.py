# [BLUEPRINT] MOD-SELL-002 | docs/03_modules/MOD-SELL-002/
# [MODULE] zephyr.sell_decision.core.sell_signal_scorer
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/sell_decision/test_sell_signal_scorer.py
# [TTL] permanent
"""sell_signal_scorer（卖出信号评分器）单元测试。

覆盖：
- 评分=置信度×强度×历史准确率调整×共振加成，值域[0,1]
- 贝叶斯准确率收缩（小样本→0.5 先验）
- 跨周期共振加成（同标的同方向不同 timeframe）
- 排序确定性（score 降序→symbol 字典序）
- 非法输入 → InvalidScoreInputError
"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.sell_signal_collector import (
    SellDirection,
    SellSignal,
    SellSignalType,
    SignalTimeFrame,
)
from zephyr.sell_decision.core.sell_signal_scorer import (
    AccuracyStat,
    InvalidScoreInputError,
    score_signals,
)


def _sig(
    symbol: str = "A",
    stype: SellSignalType = SellSignalType.TECHNICAL,
    conf: float = 0.8,
    strength: float = 0.5,
    tf: SignalTimeFrame = SignalTimeFrame.DAILY,
) -> SellSignal:
    return SellSignal(
        symbol=symbol,
        signal_type=stype,
        direction=SellDirection.REDUCE,
        confidence=conf,
        timeframe=tf,
        strength=strength,
    )


class TestScoring:
    def test_base_score_without_stats(self) -> None:
        """无准确率统计 → 评分=置信度×强度（中性准确率 0.5 调整）。"""
        scored = score_signals([_sig(conf=0.8, strength=0.6)])
        assert len(scored) == 1
        # 0.8 conf × 0.6 strength × 0.5 中性调整 = 0.24
        assert scored[0].score == pytest.approx(0.8 * 0.6 * 0.5)
        assert 0.0 <= scored[0].score <= 1.0

    def test_accuracy_stats_boost_high_hit_rate(self) -> None:
        """高命中率信号类型 → 评分高于中性。"""
        stats = {SellSignalType.TECHNICAL: AccuracyStat(hits=18, total=20)}
        boosted = score_signals([_sig()], accuracy_stats=stats)[0].score
        neutral = score_signals([_sig()])[0].score
        assert boosted > neutral

    def test_small_sample_shrinks_to_prior(self) -> None:
        """小样本（2/2 命中）准确率收缩后应低于大样本（18/20）。"""
        small = score_signals(
            [_sig()], accuracy_stats={SellSignalType.TECHNICAL: AccuracyStat(hits=2, total=2)}
        )[0].score
        large = score_signals(
            [_sig()], accuracy_stats={SellSignalType.TECHNICAL: AccuracyStat(hits=18, total=20)}
        )[0].score
        assert small < large

    def test_resonance_bonus_cross_timeframe(self) -> None:
        """同标的同方向跨周期共振 → 评分乘 (1+bonus)，封顶 1.0。"""
        single = score_signals([_sig(conf=0.9, strength=0.9)])[0].score
        resonant = score_signals(
            [
                _sig(conf=0.9, strength=0.9, tf=SignalTimeFrame.DAILY),
                _sig(conf=0.9, strength=0.9, tf=SignalTimeFrame.HOUR_60),
            ]
        )
        # 共振组两个信号都应获得加成
        for s in resonant:
            assert s.resonance is True
            assert s.score > single or s.score == pytest.approx(1.0)

    def test_no_resonance_same_timeframe(self) -> None:
        """同 timeframe 不算共振（去重后单信号）。"""
        scored = score_signals([_sig(tf=SignalTimeFrame.DAILY)])
        assert scored[0].resonance is False

    def test_score_capped_at_one(self) -> None:
        """满分输入 → score ≤ 1.0。"""
        stats = {SellSignalType.TECHNICAL: AccuracyStat(hits=100, total=100)}
        scored = score_signals(
            [
                _sig(conf=1.0, strength=1.0, tf=SignalTimeFrame.DAILY),
                _sig(conf=1.0, strength=1.0, tf=SignalTimeFrame.MIN_15),
            ],
            accuracy_stats=stats,
        )
        assert all(s.score <= 1.0 for s in scored)

    def test_strength_clipped_to_unit(self) -> None:
        """strength>1（异常上游）→ 截断至 1.0（Fail-Closed 不放大）。"""
        scored = score_signals([_sig(conf=1.0, strength=3.0)])
        assert scored[0].score <= 1.0

    def test_sorted_by_score_desc_then_symbol(self) -> None:
        """输出按 score 降序、同分按 symbol 字典序。"""
        scored = score_signals(
            [
                _sig(symbol="B", conf=0.5, strength=0.5),
                _sig(symbol="A", conf=0.9, strength=0.9),
                _sig(symbol="C", conf=0.5, strength=0.5),
            ]
        )
        assert scored[0].signal.symbol == "A"
        assert [s.signal.symbol for s in scored[1:]] == ["B", "C"]

    def test_components_recorded(self) -> None:
        """评分明细（置信度/强度/准确率/共振加成）留痕。"""
        scored = score_signals([_sig()])
        s = scored[0]
        assert s.confidence_component == pytest.approx(0.8)
        assert s.strength_component == pytest.approx(0.5)
        assert s.accuracy_component == pytest.approx(0.5)
        assert s.resonance_multiplier == pytest.approx(1.0)

    def test_empty_signals(self) -> None:
        assert score_signals([]) == []


class TestInvalidInput:
    def test_accuracy_stat_hits_above_total(self) -> None:
        with pytest.raises(InvalidScoreInputError):
            score_signals(
                [_sig()],
                accuracy_stats={SellSignalType.TECHNICAL: AccuracyStat(hits=5, total=3)},
            )

    def test_accuracy_stat_negative(self) -> None:
        with pytest.raises(InvalidScoreInputError):
            score_signals(
                [_sig()],
                accuracy_stats={SellSignalType.TECHNICAL: AccuracyStat(hits=-1, total=3)},
            )

    def test_invalid_resonance_bonus(self) -> None:
        with pytest.raises(InvalidScoreInputError):
            score_signals([_sig()], resonance_bonus=-0.1)
        with pytest.raises(InvalidScoreInputError):
            score_signals([_sig()], resonance_bonus=1.5)
