"""RRG 相对旋转图 单元测试（22 号 spec §3.1④，JdK DualEma 10/26）"""

import pytest

from zephyr.signal_ashare.sector_rrg import (
    RRGQuadrant,
    classify_quadrant,
    compute_rrg_series,
    confirm_quadrant_series,
    ema_series,
    quadrant_strength_adjust,
    rrg_zscore,
    zscore_signal_adjust,
)

L = RRGQuadrant.LEADING
W = RRGQuadrant.WEAKENING
G = RRGQuadrant.LAGGING
I = RRGQuadrant.IMPROVING


def _trend_series(start: float, daily_pct: float, n: int) -> list[float]:
    """生成等比涨/跌合成收盘价序列"""
    out = [start]
    for _ in range(n - 1):
        out.append(out[-1] * (1.0 + daily_pct))
    return out


class TestEmaSeries:
    def test_empty(self):
        assert ema_series([], 10) == []

    def test_single_value_seed(self):
        assert ema_series([5.0], 10) == [5.0]

    def test_recursion_matches_tdx_formula(self):
        """EMA_t = alpha×x_t + (1-alpha)×EMA_{t-1}，alpha=2/(span+1)"""
        values = [10.0, 12.0, 11.0]
        out = ema_series(values, 10)
        alpha = 2.0 / 11.0
        assert out[0] == 10.0
        assert out[1] == pytest.approx(alpha * 12.0 + (1 - alpha) * 10.0)
        assert out[2] == pytest.approx(alpha * 11.0 + (1 - alpha) * out[1])

    def test_constant_series_stays_constant(self):
        assert ema_series([7.0] * 30, 10) == pytest.approx([7.0] * 30)


class TestComputeRrgSeries:
    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="长度必须一致"):
            compute_rrg_series([1.0] * 70, [1.0] * 69)

    def test_min_data_requirement_raises(self):
        """最小数据量 long×2+short=62 日"""
        with pytest.raises(ValueError, match="最小数据量"):
            compute_rrg_series([1.0] * 61, [1.0] * 61)

    def test_non_positive_benchmark_raises(self):
        with pytest.raises(ValueError, match="基准收盘价必须为正"):
            compute_rrg_series([1.0] * 70, [0.0] * 70)

    def test_sector_outperforming_lands_leading(self):
        """板块日涨 1%、基准横盘 → RS 持续上升 → RS-Ratio>100 且动量>100 → 领先"""
        p_sector = _trend_series(100.0, 0.01, 70)
        p_bench = [100.0] * 70
        points = compute_rrg_series(p_sector, p_bench)
        assert len(points) == 70
        last = points[-1]
        assert last.rs_ratio > 100.0
        assert last.rs_momentum > 100.0
        assert last.quadrant == L

    def test_sector_underperforming_lands_lagging(self):
        """板块日跌 1%、基准横盘 → RS 持续下降 → 滞后"""
        p_sector = _trend_series(100.0, -0.01, 70)
        p_bench = [100.0] * 70
        last = compute_rrg_series(p_sector, p_bench)[-1]
        assert last.rs_ratio < 100.0
        assert last.rs_momentum < 100.0
        assert last.quadrant == G

    def test_sector_matching_benchmark_stays_neutral(self):
        """板块与基准完全同步 → RS 恒定 → RS-Ratio=100、RS-Momentum=100（中性分界）"""
        p_sector = _trend_series(100.0, 0.005, 70)
        p_bench = _trend_series(5000.0, 0.005, 70)
        last = compute_rrg_series(p_sector, p_bench)[-1]
        assert last.rs_ratio == pytest.approx(100.0)
        assert last.rs_momentum == pytest.approx(100.0)


class TestClassifyQuadrant:
    @pytest.mark.parametrize(
        ("ratio", "momentum", "expected"),
        [
            (101.0, 101.0, L),
            (101.0, 99.0, W),
            (99.0, 99.0, G),
            (99.0, 101.0, I),
            (100.0, 101.0, I),  # 边界：=100 不算 >100 → 左半区
            (101.0, 100.0, W),
        ],
    )
    def test_quadrants(self, ratio, momentum, expected):
        assert classify_quadrant(ratio, momentum) == expected


class TestConfirmQuadrantSeries:
    def test_empty(self):
        assert confirm_quadrant_series([]) == []

    def test_single_day_flip_not_confirmed(self):
        """单日跳变 = whipsaw 假信号，不采信"""
        assert confirm_quadrant_series([L, L, W, L, L]) == [L, L, L, L, L]

    def test_two_consecutive_days_confirm(self):
        """连续 2 日保持新象限 → 确认切换"""
        assert confirm_quadrant_series([L, L, W, W, W]) == [L, L, L, W, W]

    def test_new_candidate_resets_streak(self):
        """候选象限被第三个象限打断 → 重新计数"""
        assert confirm_quadrant_series([L, W, G, G]) == [L, L, L, G]

    def test_half_circle_rotation_allowed(self):
        """强趋势半圆例外：领先→疲软→领先 容许（State Street 2026-03）"""
        out = confirm_quadrant_series([L, L, W, W, L, L])
        assert out == [L, L, L, W, W, L]

    def test_full_clockwise_rotation(self):
        """顺时针完整轮动 领先→疲软→滞后→改善→领先"""
        seq = [L, L, W, W, G, G, I, I, L, L]
        assert confirm_quadrant_series(seq) == [L, L, L, W, W, G, G, I, I, L]

    def test_confirm_days_3(self):
        """连续 3 日确认模式：2 日不足以切换"""
        assert confirm_quadrant_series([L, W, W, W], confirm_days=3) == [L, L, L, W]


class TestRrgZscore:
    def test_insufficient_samples_returns_zero(self):
        assert rrg_zscore([101.0]) == 0.0

    def test_zero_std_returns_zero(self):
        assert rrg_zscore([100.0] * 70) == 0.0

    def test_stretch_detection(self):
        """63 日平稳在 100 附近，最新拉到 106 → Z 显著为正"""
        hist = [99.5, 100.0, 100.5] * 21 + [106.0]
        z = rrg_zscore(hist)
        assert z > 2.0

    def test_window_truncates_history(self):
        """滚动窗口只取最近 63 日"""
        hist = [50.0] * 100 + [101.0, 100.0, 99.0] * 21 + [100.0]
        z = rrg_zscore(hist, window=63)
        assert abs(z) < 2.0  # 远古极端值不进入窗口


class TestZscoreSignalAdjust:
    def test_leading_overstretched_downgrades_to_hold(self):
        """领先象限 Z>+2 = 透支，买入降级持有"""
        assert zscore_signal_adjust(L, 2.5) == "HOLD_REDUCE"

    def test_leading_normal_z_keeps_buy(self):
        assert zscore_signal_adjust(L, 1.0) == "BUY_CANDIDATE"

    def test_improving_abnormal_compression_upgrades(self):
        """改善象限 Z<−2 = 异常压缩，升级提前布局"""
        assert zscore_signal_adjust(I, -2.5) == "EARLY_LAYOUT"

    def test_improving_normal_z_keeps_watch(self):
        assert zscore_signal_adjust(I, -1.0) == "WATCH_EARLY"

    def test_other_quadrants_unaffected(self):
        assert zscore_signal_adjust(W, 3.0) == "HOLD_REDUCE"
        assert zscore_signal_adjust(G, -3.0) == "AVOID"


class TestQuadrantStrengthAdjust:
    @pytest.mark.parametrize(
        ("quadrant", "expected"),
        [(L, 0.05), (I, 0.02), (W, -0.03), (G, -0.08)],
    )
    def test_adjust_mapping(self, quadrant, expected):
        assert quadrant_strength_adjust(quadrant) == expected
