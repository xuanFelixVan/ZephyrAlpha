# [A_test] module_id: MOD-SIG-116 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [BLUEPRINT] MOD-SIG-116 | docs/03_modules/_domain_signal/wyckoff_secondary_test/blueprint.md
# [MODULE] tests.signal_ashare.test_wyckoff_secondary_test
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.wyckoff_secondary_test

"""Wyckoff 二次测试模型（MOD-SIG-116，B10-01372）施工验证测试。

覆盖：KBar 合法性（价格/高低/有限数/非负量）、样本不足、配置边界、
Markup/Markdown/Range 结构判定、ST 缩量确认、深调反转、跌破前低反转、
概率表滚动统计（含 horizon 不全不计入）、score 符号、volume ratio 精度、
时钟注入确定性。全程内存合成数据，无 DB/无网络。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.wyckoff_secondary_test",
    reason="wyckoff_secondary_test not importable",
)

from zephyr.signal_ashare.wyckoff_secondary_test import (  # noqa: E402
    KBar,
    StructurePhase,
    StVerdict,
    WyckoffStConfig,
    WyckoffStError,
    WyckoffSecondaryTest,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _k(
    open: float, high: float, low: float, close: float, volume: float
) -> KBar:
    return KBar(ts=_T0, open=open, high=high, low=low, close=close, volume=volume)


def _bars(closes: list[float], vols: list[float] | None = None) -> list[KBar]:
    """high=close+0.2 / low=close-0.2 的简化构造（摆点由 close  zigzag 决定）。"""
    vols = vols or [1000.0] * len(closes)
    assert len(closes) == len(vols)
    return [_k(c, c + 0.2, c - 0.2, c, v) for c, v in zip(closes, vols)]


# ── 手工验证的摆点结构（pivot_order=2）─────────────────────────────────────
# MARKUP：摆点高 12.2@5 / 13.2@10（HH），摆点低 9.3@2 / 10.3@7（HL）
_MKUP_CLOSES = [11.0, 10.0, 9.5, 10.5, 11.5, 12.0, 11.0, 10.5, 11.5, 12.5, 13.0, 12.6, 12.4]
# MARKDOWN：摆点高 10.7@2 / 9.7@7（LH），摆点低 7.8@5 / 6.8@10（LL）
_MDN_CLOSES = [9.0, 10.0, 10.5, 9.5, 8.5, 8.0, 9.0, 9.5, 8.5, 7.5, 7.0, 7.4, 7.6]
# 混合结构：摆点高 HH 但摆点低 LL → RANGE
_MIXED_CLOSES = [11.0, 10.0, 9.5, 10.5, 11.5, 12.0, 11.0, 9.0, 11.5, 12.5, 13.0, 12.6, 12.4]


def _mkup(vols: list[float] | None = None) -> list[KBar]:
    return _bars(_MKUP_CLOSES, vols)


def _mdn(vols: list[float] | None = None) -> list[KBar]:
    return _bars(_MDN_CLOSES, vols)


def _shrink_vols(n: int = 13) -> list[float]:
    """脉冲段(idx7..10)放量 1000，回踩段(idx11+)缩量 100。"""
    vols = [1000.0] * n
    for i in range(11, n):
        vols[i] = 100.0
    return vols


class TestKBarValidation:
    def test_high_lt_low_raises(self):
        with pytest.raises(WyckoffStError):
            _k(10, 9, 10.5, 10, 100)

    def test_nonfinite_high_raises(self):
        with pytest.raises(WyckoffStError):
            _k(10, float("inf"), 9, 10, 100)

    def test_negative_volume_raises(self):
        with pytest.raises(WyckoffStError):
            _k(10, 11, 9, 10, -1)

    def test_zero_price_raises(self):
        with pytest.raises(WyckoffStError):
            _k(0, 11, 9, 10, 100)


class TestConfigValidation:
    def test_pivot_order_zero_raises(self):
        with pytest.raises(WyckoffStError):
            WyckoffStConfig(pivot_order=0)

    def test_min_bars_too_small_raises(self):
        with pytest.raises(WyckoffStError):
            WyckoffStConfig(pivot_order=2, min_bars=6)

    def test_fib_tolerance_out_of_range(self):
        with pytest.raises(WyckoffStError):
            WyckoffStConfig(fib_tolerance=0.30)

    def test_prob_horizon_zero_raises(self):
        with pytest.raises(WyckoffStError):
            WyckoffStConfig(prob_horizon=0)


class TestEmptyAndShort:
    def test_empty_bars_raises(self):
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        with pytest.raises(WyckoffStError):
            model.analyze([])

    def test_short_bars_raises(self):
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        with pytest.raises(WyckoffStError):
            model.analyze(_bars([10.0] * 11))

    def test_non_kbar_element_raises(self):
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        with pytest.raises(WyckoffStError):
            model.analyze(["not-a-kbar"] * 12)  # type: ignore[list-item]


class TestStructureDetection:
    def test_markup_detected(self):
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_mkup())
        assert r.phase is StructurePhase.MARKUP

    def test_markdown_detected(self):
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_mdn())
        assert r.phase is StructurePhase.MARKDOWN

    def test_range_when_few_pivots(self):
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_bars([10.0] * 13))
        assert r.phase is StructurePhase.RANGE
        assert r.verdict is StVerdict.NEUTRAL
        assert r.retracement_ratio is None

    def test_range_when_mixed_structure(self):
        """摆点高 HH 但摆点低 LL（混合）→ RANGE。"""
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_bars(_MIXED_CLOSES))
        assert r.phase is StructurePhase.RANGE


class TestStConfirmation:
    def test_markup_st_continuation(self):
        """Markup 缩量回踩（r≈0.276<61.8%）→ continuation，score>0。"""
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_mkup(_shrink_vols()))
        assert r.phase is StructurePhase.MARKUP
        assert r.st_confirmed is True
        assert r.verdict is StVerdict.CONTINUATION
        assert r.score > 0
        assert r.retracement_ratio == pytest.approx(0.8 / 2.9, rel=1e-6)
        assert r.volume_ratio == pytest.approx(0.1, rel=1e-6)

    def test_markup_deep_retracement_no_st_reversal(self):
        """Markup 放量深调（r≈0.759≥61.8%）→ reversal，score<0。"""
        closes = _MKUP_CLOSES[:11] + [11.2, 11.0]
        vols = [1000.0] * 11 + [2500.0, 2600.0]
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_bars(closes, vols))
        assert r.phase is StructurePhase.MARKUP
        assert r.st_confirmed is False
        assert r.verdict is StVerdict.REVERSAL
        assert r.score < 0

    def test_markup_break_low_reversal(self):
        """Markup 跌破前波段低点（r>1.0）→ reversal。"""
        closes = _MKUP_CLOSES[:11] + [10.0, 9.5]
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_bars(closes))
        assert r.phase is StructurePhase.MARKUP
        assert r.retracement_ratio is not None and r.retracement_ratio > 1.0
        assert r.verdict is StVerdict.REVERSAL

    def test_markdown_st_continuation(self):
        """Markdown 缩量反抽（r≈0.276）→ continuation，score<0。"""
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_mdn(_shrink_vols()))
        assert r.phase is StructurePhase.MARKDOWN
        assert r.st_confirmed is True
        assert r.verdict is StVerdict.CONTINUATION
        assert r.score < 0

    def test_markdown_deep_retracement_reversal(self):
        """Markdown 放量深反抽（r≈0.828≥61.8%）→ reversal，score>0。"""
        closes = _MDN_CLOSES[:11] + [8.8, 9.2]
        vols = [1000.0] * 11 + [2500.0, 2600.0]
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_bars(closes, vols))
        assert r.phase is StructurePhase.MARKDOWN
        assert r.st_confirmed is False
        assert r.verdict is StVerdict.REVERSAL
        assert r.score > 0

    def test_st_not_confirmed_when_pullback_volume_high(self):
        closes = _MKUP_CLOSES
        vols = [100.0] * 11 + [2000.0, 2000.0]  # 回踩量远大于脉冲量
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_bars(closes, vols))
        assert r.st_confirmed is False
        assert r.volume_ratio is not None and r.volume_ratio > 1.0


class TestProbabilityTable:
    def test_prob_table_zero_samples_default_horizon(self):
        """默认 horizon=10 下短序列无全可见样本。"""
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        r = model.analyze(_mkup())
        t = r.prob_table
        assert t.samples_382 == 0 and t.samples_618 == 0
        assert t.prob_382 == 0.0 and t.prob_618 == 0.0

    def test_prob_table_counts_with_short_horizon(self):
        """horizon=2 时精确命中：382 样本 1（未延续），618 样本 2（1 延续）。"""
        model = WyckoffSecondaryTest(
            config=WyckoffStConfig(prob_horizon=2), clock=lambda: _T0
        )
        r = model.analyze(_mkup())
        t = r.prob_table
        assert t.samples_382 == 1
        assert t.continuations_382 == 0
        assert t.samples_618 == 2
        assert t.continuations_618 == 1
        assert t.prob_382 == 0.0
        assert t.prob_618 == pytest.approx(0.5, rel=1e-9)


class TestDeterminism:
    def test_same_input_same_output(self):
        model = WyckoffSecondaryTest(clock=lambda: _T0)
        data = _mkup(_shrink_vols())
        r1 = model.analyze(data)
        r2 = model.analyze(data)
        assert r1 == r2

    def test_clock_injection(self):
        t = datetime.datetime(2024, 1, 1, 0, 0, 0)
        model = WyckoffSecondaryTest(clock=lambda: t)
        r = model.analyze(_mkup())
        assert r.generated_at == t
