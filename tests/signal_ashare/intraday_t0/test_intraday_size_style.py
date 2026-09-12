# [BLUEPRINT] MOD-SIG-120 | docs/03_modules/_domain_signal/intraday_size_style/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-120 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_intraday_size_style
# [TESTS] src/zephyr/signal_ashare/intraday_size_style.py
"""MOD-SIG-120 单元测试：intraday_size_style 分时微结构与大小盘风格。

蓝图验收（B10-01385/CAND-TESTB-040，A1 模块45）：
Size 因子（大盘-小盘收益差序列）+ 风格持续性（同向 >5 天判定）+
Gao 2018 日内动量（首/次半小时滚动相关 + 信号）+ VWAP 偏差 + 分时 ADX。
时钟全注入内存替身，纯内存不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.intraday_size_style",
    reason="intraday_size_style not importable",
)

from zephyr.signal_ashare.intraday_size_style import (  # noqa: E402
    IntradaySizeStyle,
    IntradaySizeStyleError,
)

_T0 = datetime.datetime(2026, 8, 26, 10, 0, 0)


def _model() -> IntradaySizeStyle:
    return IntradaySizeStyle(clock=lambda: _T0)


# ──────────────────────────────────────────────────────────────────────────────
# Size 因子
# ──────────────────────────────────────────────────────────────────────────────


class TestSizeFactorSeries:
    def test_basic_diff(self) -> None:
        diffs = _model().size_factor_series([0.02, 0.01, 0.03], [0.01, 0.03, 0.01])
        assert diffs == pytest.approx((0.01, -0.02, 0.02))

    def test_length_mismatch_raises(self) -> None:
        with pytest.raises(IntradaySizeStyleError):
            _model().size_factor_series([0.01, 0.02], [0.01])

    def test_empty_raises(self) -> None:
        with pytest.raises(IntradaySizeStyleError):
            _model().size_factor_series([], [])

    def test_non_finite_raises(self) -> None:
        with pytest.raises(IntradaySizeStyleError):
            _model().size_factor_series([0.01, float("nan")], [0.01, 0.02])
        with pytest.raises(IntradaySizeStyleError):
            _model().size_factor_series([0.01], [float("inf")])


# ──────────────────────────────────────────────────────────────────────────────
# 风格持续性
# ──────────────────────────────────────────────────────────────────────────────


class TestStylePersistence:
    def test_positive_streak(self) -> None:
        p = _model().style_persistence([-0.1, 0.2, 0.3, 0.4])
        assert p.direction == 1
        assert p.streak_days == 3
        assert p.is_persistent is False

    def test_negative_streak(self) -> None:
        p = _model().style_persistence([0.1, -0.2, -0.3])
        assert p.direction == -1
        assert p.streak_days == 2

    def test_over_five_days_persistent(self) -> None:
        p = _model().style_persistence([0.01] * 6)
        assert p.streak_days == 6
        assert p.is_persistent is True

    def test_exactly_five_not_persistent(self) -> None:
        """严格大于 5 天方判定持续（边界）。"""
        p = _model().style_persistence([0.01] * 5)
        assert p.streak_days == 5
        assert p.is_persistent is False

    def test_zero_breaks_streak(self) -> None:
        p = _model().style_persistence([0.1, 0.0, 0.2, 0.3])
        assert p.direction == 1
        assert p.streak_days == 2
        trailing_zero = _model().style_persistence([0.1, 0.0])
        assert trailing_zero.direction == 0  # 尾端为 0 无方向
        assert trailing_zero.streak_days == 0
        assert trailing_zero.is_persistent is False

    def test_empty_and_bad_min_days_raises(self) -> None:
        with pytest.raises(IntradaySizeStyleError):
            _model().style_persistence([])
        with pytest.raises(IntradaySizeStyleError):
            _model().style_persistence([0.1], min_days=0)


# ──────────────────────────────────────────────────────────────────────────────
# 日内动量（Gao 2018）
# ──────────────────────────────────────────────────────────────────────────────


class TestIntradayMomentum:
    def test_perfect_positive_correlation(self) -> None:
        seq = [0.01, -0.02, 0.03, -0.01, 0.02, -0.03]
        sig = _model().intraday_momentum_signal(seq, list(seq), window=6)
        assert sig.window_ready is True
        assert sig.correlation == pytest.approx(1.0)

    def test_signal_follows_latest_first_half_up(self) -> None:
        seq = [-0.01, 0.02, -0.03, 0.01, -0.02, 0.03]
        sig = _model().intraday_momentum_signal(seq, list(seq), window=6)
        assert sig.signal == 1

    def test_signal_follows_latest_first_half_down(self) -> None:
        seq = [0.01, -0.02, 0.03, -0.01, 0.02, -0.03]
        sig = _model().intraday_momentum_signal(seq, list(seq), window=6)
        assert sig.signal == -1

    def test_below_threshold_signal_zero(self) -> None:
        first = [0.01, -0.01, 0.01, -0.01, 0.01, -0.01]
        second = [0.005] * 6  # 零方差 → 相关降级 0.0
        sig = _model().intraday_momentum_signal(first, second, window=6, corr_threshold=0.5)
        assert sig.correlation == 0.0
        assert sig.signal == 0

    def test_insufficient_window_degrades(self) -> None:
        sig = _model().intraday_momentum_signal([0.01, 0.02], [0.01, 0.02], window=6)
        assert sig.window_ready is False
        assert sig.correlation == 0.0
        assert sig.signal == 0

    def test_invalid_params_raises(self) -> None:
        with pytest.raises(IntradaySizeStyleError):
            _model().intraday_momentum_signal([0.01, 0.02], [0.01, 0.02], window=1)
        with pytest.raises(IntradaySizeStyleError):
            _model().intraday_momentum_signal([0.01, 0.02], [0.01, 0.02], window=2, corr_threshold=0.0)
        with pytest.raises(IntradaySizeStyleError):
            _model().intraday_momentum_signal([0.01, 0.02], [0.01], window=2)


# ──────────────────────────────────────────────────────────────────────────────
# VWAP 偏差
# ──────────────────────────────────────────────────────────────────────────────


class TestVwapDeviation:
    def test_basic(self) -> None:
        dev = _model().vwap_deviation([10.0, 12.0], [1.0, 1.0])
        assert dev == pytest.approx((12.0 - 11.0) / 11.0)

    def test_volume_weighted(self) -> None:
        # vwap = (10*3 + 20*1)/4 = 12.5；最新价 20 → dev 0.6
        dev = _model().vwap_deviation([10.0, 20.0], [3.0, 1.0])
        assert dev == pytest.approx(0.6)

    def test_zero_total_volume_raises(self) -> None:
        with pytest.raises(IntradaySizeStyleError):
            _model().vwap_deviation([10.0, 12.0], [0.0, 0.0])

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(IntradaySizeStyleError):
            _model().vwap_deviation([10.0], [1.0, 2.0])  # 长度不齐
        with pytest.raises(IntradaySizeStyleError):
            _model().vwap_deviation([10.0], [-1.0])  # 负成交量
        with pytest.raises(IntradaySizeStyleError):
            _model().vwap_deviation([0.0], [1.0])  # 非正价格


# ──────────────────────────────────────────────────────────────────────────────
# 分时 ADX
# ──────────────────────────────────────────────────────────────────────────────


class TestIntradayAdx:
    def test_uptrend_adx_100(self) -> None:
        """单边上行：+DM 独占 → DX 全 100。"""
        closes = [10.0 + i for i in range(8)]
        highs = [c + 0.5 for c in closes]
        lows = [c - 0.5 for c in closes]
        adx = _model().intraday_adx(highs, lows, closes, period=4)
        assert adx == pytest.approx(100.0)

    def test_choppy_lower_than_uptrend(self) -> None:
        """震荡：±DM 交替 → ADX 显著低于单边。"""
        up_closes = [10.0 + i for i in range(8)]
        up_adx = _model().intraday_adx([c + 0.5 for c in up_closes], [c - 0.5 for c in up_closes], up_closes, period=4)
        chop_closes = [10.0, 11.0, 10.0, 11.0, 10.0, 11.0, 10.0, 11.0]
        chop_adx = _model().intraday_adx(
            [c + 0.3 for c in chop_closes],
            [c - 0.3 for c in chop_closes],
            chop_closes,
            period=4,
        )
        assert 0.0 <= chop_adx < up_adx

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(IntradaySizeStyleError):
            _model().intraday_adx([1.0, 2.0], [0.5, 1.5], [1.0, 2.0], period=4)  # 样本不足
        with pytest.raises(IntradaySizeStyleError):
            _model().intraday_adx([1.0, 2.0, 3.0], [0.5, 9.9, 2.5], [1.0, 2.0, 3.0], period=2)  # high<low
        with pytest.raises(IntradaySizeStyleError):
            _model().intraday_adx([1.0, 2.0, 3.0], [0.5, 1.5], [1.0, 2.0, 3.0], period=2)  # 长度不齐
        with pytest.raises(IntradaySizeStyleError):
            _model().intraday_adx([1.0, 2.0, 3.0], [0.5, 1.5, 2.5], [1.0, 2.0, 3.0], period=1)


# ──────────────────────────────────────────────────────────────────────────────
# 综合评估（聚合 + 时钟注入 + 确定性）
# ──────────────────────────────────────────────────────────────────────────────


def _assess_kwargs() -> dict:
    return {
        "large_returns": [0.02, 0.01, 0.03, 0.02, 0.01, 0.02],
        "small_returns": [0.01, 0.03, 0.01, 0.02, 0.03, 0.01],
        "first_half_returns": [0.01, -0.02, 0.03, -0.01, 0.02, 0.03],
        "second_half_returns": [0.01, -0.02, 0.03, -0.01, 0.02, 0.03],
        "prices": [10.0, 10.5, 11.0],
        "volumes": [2.0, 1.0, 1.0],
        "highs": [10.2, 10.7, 11.2],
        "lows": [9.8, 10.3, 10.8],
        "closes": [10.0, 10.5, 11.0],
        "momentum_window": 6,
        "adx_period": 2,
    }


class TestAssess:
    def test_assess_aggregates_and_clock(self) -> None:
        out = _model().assess(**_assess_kwargs())
        assert out.size_diff_latest == pytest.approx(0.01)
        assert out.persistence.direction == 1
        assert out.momentum.window_ready is True
        assert out.momentum.signal == 1
        assert out.vwap_deviation == pytest.approx((11.0 - 10.375) / 10.375)
        assert 0.0 <= out.adx <= 100.0
        assert out.assessed_at == _T0  # 时钟注入生效

    def test_determinism(self) -> None:
        a = _model().assess(**_assess_kwargs())
        b = _model().assess(**_assess_kwargs())
        assert a == b  # 同输入必同输出
