# [BLUEPRINT] MOD-POS-019 | docs/03_modules/MOD-POS-019/
# [MODULE] zephyr.position.core.position_behavior_classifier
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/position/test_position_behavior_classifier.py
# [TTL] permanent
"""position_behavior_classifier（持仓行为分类器）单元测试。

覆盖：
- 规则分类五类：LOSS_HOLDING（套牢）/WINNER_CUTTING（过早止盈）/TREND_RIDING（趋势持有）/STALE（呆滞）/NEUTRAL
- 分类优先级（套牢 > 过早止盈 > 趋势 > 呆滞 > 中性）
- 汇总计数 + 行为风险预警（处置效应/踩踏止盈）
- 非法特征输入 → InvalidPositionFeatureError
"""

from __future__ import annotations

import pytest

from zephyr.position.core.position_behavior_classifier import (
    BehaviorClass,
    InvalidPositionFeatureError,
    PositionFeatures,
    classify_positions,
)


def _feat(pnl: float, days: int, dd: float = 0.0) -> PositionFeatures:
    return PositionFeatures(pnl_pct=pnl, days_held=days, drawdown_from_peak=dd)


class TestClassification:
    def test_loss_holding(self) -> None:
        """深亏+长期持有 → LOSS_HOLDING（处置效应）。"""
        r = classify_positions({"A": _feat(pnl=-0.20, days=60)})
        assert r.labels["A"] is BehaviorClass.LOSS_HOLDING

    def test_winner_cutting(self) -> None:
        """盈利+短持 → WINNER_CUTTING（过早止盈倾向）。"""
        r = classify_positions({"A": _feat(pnl=0.10, days=3)})
        assert r.labels["A"] is BehaviorClass.WINNER_CUTTING

    def test_trend_riding(self) -> None:
        """盈利+长持+回撤小 → TREND_RIDING（让利润奔跑）。"""
        r = classify_positions({"A": _feat(pnl=0.25, days=40, dd=0.05)})
        assert r.labels["A"] is BehaviorClass.TREND_RIDING

    def test_stale(self) -> None:
        """盈亏平淡+长持 → STALE（呆滞占用资金）。"""
        r = classify_positions({"A": _feat(pnl=0.01, days=90)})
        assert r.labels["A"] is BehaviorClass.STALE

    def test_neutral(self) -> None:
        """不满足任何规则 → NEUTRAL。"""
        r = classify_positions({"A": _feat(pnl=0.03, days=10)})
        assert r.labels["A"] is BehaviorClass.NEUTRAL

    def test_loss_holding_priority_over_stale(self) -> None:
        """深亏长持同时命中 LOSS_HOLDING 与 STALE → 取 LOSS_HOLDING（优先）。"""
        r = classify_positions({"A": _feat(pnl=-0.30, days=120)})
        assert r.labels["A"] is BehaviorClass.LOSS_HOLDING

    def test_mild_loss_not_loss_holding(self) -> None:
        """浅亏（>-15%）→ 不算套牢。"""
        r = classify_positions({"A": _feat(pnl=-0.05, days=100)})
        assert r.labels["A"] is not BehaviorClass.LOSS_HOLDING


class TestSummary:
    def test_counts(self) -> None:
        r = classify_positions(
            {
                "L": _feat(pnl=-0.20, days=60),
                "W": _feat(pnl=0.10, days=3),
                "T": _feat(pnl=0.25, days=40, dd=0.05),
                "S": _feat(pnl=0.01, days=90),
                "N": _feat(pnl=0.03, days=10),
            }
        )
        assert r.counts[BehaviorClass.LOSS_HOLDING] == 1
        assert r.counts[BehaviorClass.WINNER_CUTTING] == 1
        assert r.counts[BehaviorClass.TREND_RIDING] == 1
        assert r.counts[BehaviorClass.STALE] == 1
        assert r.counts[BehaviorClass.NEUTRAL] == 1

    def test_disposition_effect_warning(self) -> None:
        """存在套牢持仓 → 处置效应预警。"""
        r = classify_positions({"A": _feat(pnl=-0.25, days=80)})
        assert any("处置效应" in w for w in r.warnings)

    def test_empty_positions(self) -> None:
        r = classify_positions({})
        assert r.labels == {}
        assert all(v == 0 for v in r.counts.values())


class TestInvalidInput:
    def test_non_finite_pnl(self) -> None:
        with pytest.raises(InvalidPositionFeatureError):
            classify_positions({"A": _feat(pnl=float("nan"), days=5)})

    def test_negative_days_held(self) -> None:
        with pytest.raises(InvalidPositionFeatureError):
            classify_positions({"A": _feat(pnl=0.0, days=-1)})

    def test_drawdown_out_of_range(self) -> None:
        """回撤须 ∈[0,1]。"""
        with pytest.raises(InvalidPositionFeatureError):
            classify_positions({"A": _feat(pnl=0.1, days=5, dd=1.5)})
        with pytest.raises(InvalidPositionFeatureError):
            classify_positions({"A": _feat(pnl=0.1, days=5, dd=-0.1)})
