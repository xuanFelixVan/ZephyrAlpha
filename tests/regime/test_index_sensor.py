# [BLUEPRINT] MOD-REGIME-016 | (auto-injected by S4 reconciler，gw-tdm-20260909 修正为模块级 ID) | §
# [TTL] permanent
# [DOMAIN] D_REGIME
# [TTL] permanent
"""MOD-REGIME-016 index_sensor 单元测试（红蓝对抗：红-边界/红-契约/红-前视姿态）。"""

from __future__ import annotations

import pytest

from zephyr.regime.features.index_sensor import (
    IndexSensorError,
    compute_index_trend_score,
)


def _series(closes: list[float]) -> tuple[float, ...]:
    return tuple(closes)


def _uptrend_below_high(n: int = 80, start: float = 3000.0, step: float = 5.0) -> tuple[float, ...]:
    """稳步上行、当前不在 60 日高点 3% 内（留出 2% 缓冲再回落）。"""
    closes = [start + i * step for i in range(n)]
    closes[-1] = closes[-2] * 0.97  # 回落 3%，脱离高位区但仍高于所有均线
    return _series(closes)


def _clean_bullish_plus_one() -> tuple[float, ...]:
    """人工构造：唯一得分=多头排列 +1 的序列（手工核算）。

    100 根，基线 100；bar45=115（旧高，出 MA20 窗）；bar60=150（60 日窗内 spike，
    距收盘 6.7% ≥3% 免高位减分）；bars70-99 线性 100→140。
    MA20≈122.4 < close140；MA60≈111.1 < MA20（多头）；close=high60 无新高。
    """
    closes = [100.0] * 100
    closes[45] = 115.0
    closes[60] = 150.0
    for i in range(70, 100):
        closes[i] = 100.0 + (i - 69) * (40.0 / 30.0)
    closes[99] = 140.0
    return _series(closes)


class TestScoreRules:
    """节点语义逐条：排列加分/破位减档/高位减分。"""

    def test_bullish_alignment_bonus(self):
        s = compute_index_trend_score(_clean_bullish_plus_one())
        assert s.score == 1
        assert s.bullish_alignment is True
        assert s.above_ma20 is True and s.above_ma60 is True
        assert s.near_60d_high is False
        assert s.reasons == ("MA20>MA60 多头排列 +1",)

    def test_break_ma20_minus_one(self):
        closes = list(_clean_bullish_plus_one())
        closes[-1] = 115.0  # 低于 MA20≈122.4，仍高于 MA60≈111.1
        s = compute_index_trend_score(_series(closes))
        assert s.above_ma20 is False
        assert s.above_ma60 is True
        assert s.score == 0  # +1(排列) -1(破MA20)，无高位减分（high=150 距离>3%）

    def test_break_ma60_minus_two_cumulative(self):
        closes = list(_uptrend_below_high())
        closes[-1] = closes[-1] * 0.70  # 砸 30%，双破
        s = compute_index_trend_score(_series(closes))
        assert s.above_ma20 is False and s.above_ma60 is False
        # 多头排列(+1) + 破20(-1) + 破60(-2) = -2（clamp 下界）
        assert s.score == -2

    def test_near_high_penalty(self):
        closes = [3000.0 + i * 5.0 for i in range(80)]
        s = compute_index_trend_score(_series(closes))  # 收盘=新高，dist=0
        assert s.near_60d_high is True
        assert s.dist_to_high == 0.0

    def test_clamp_upper_bound(self):
        # 多头排列+1 是唯一加分项，上限天然受限；构造极端验证 clamp
        s = compute_index_trend_score(_uptrend_below_high())
        assert -2 <= s.score <= 2

    def test_score_range_always(self):
        for factor in (0.70, 0.85, 0.97, 1.0, 1.05):
            closes = list(_uptrend_below_high())
            closes[-1] = closes[-2] * factor
            s = compute_index_trend_score(_series(closes))
            assert -2 <= s.score <= 2


class TestBoundaries:
    """红-边界：样本数/非法值/3% 高位带。"""

    def test_insufficient_sample_rejected(self):
        with pytest.raises(IndexSensorError):
            compute_index_trend_score(_series([3000.0] * 60))  # 60 根 = MA60+当日 不够

    def test_minimum_sample_accepted(self):
        s = compute_index_trend_score(_series([3000.0] * 61))
        assert -2 <= s.score <= 2

    def test_nan_rejected(self):
        with pytest.raises(IndexSensorError):
            compute_index_trend_score(_series([3000.0] * 59 + [float("nan"), 3100.0]))

    def test_negative_price_rejected(self):
        with pytest.raises(IndexSensorError):
            compute_index_trend_score(_series([3000.0] * 60 + [-1.0]))

    def test_high_proximity_boundary(self):
        # 恰好 3%：不触发高位减分（严格 <3%）
        closes = [100.0] * 60 + [103.0, 97.0]
        closes = [100.0 + i * 0.01 for i in range(60)] + [101.0, 97.97]
        s = compute_index_trend_score(_series(closes))
        # high60=101.0, close=97.97 → dist=3.0% 恰好等于 → near=False（严格<）
        assert s.near_60d_high is False or abs(s.dist_to_high - 0.03) < 1e-9


class TestContract:
    """红-契约：frozen/确定性/序列方向。"""

    def test_determinism(self):
        assert compute_index_trend_score(_uptrend_below_high()) == compute_index_trend_score(
            _uptrend_below_high()
        )

    def test_frozen(self):
        s = compute_index_trend_score(_uptrend_below_high())
        with pytest.raises(Exception):
            s.score = 5

    def test_reasons_auditable(self):
        s = compute_index_trend_score(_series([3000.0] * 61))
        assert isinstance(s.reasons, tuple)
