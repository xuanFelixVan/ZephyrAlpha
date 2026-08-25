# [A_test] module_id: MOD-SIG-108 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-108 | docs/03_modules/_domain_signal/multi_factor_timing_overlay/blueprint.md
# [MODULE] tests.signal_ashare.test_multi_factor_timing_overlay
# [TTL] permanent
# [DEPENDENCIES] zephyr.signal_ashare.multi_factor_timing_overlay

"""多因子叠加择时（MOD-SIG-108，B10-01482）施工验证测试。

覆盖：6 源封闭集、IC/BMA/等权权重优先级与归一、负权重 clip、合成分与方向阈、
≥3 同向共振高置信（含反向混杂）、缺源降级、非法输入 fail-closed、frozen/JSON 契约。
全程内存合成数据，无 DB。
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.multi_factor_timing_overlay import (
    TIMING_SOURCES,
    MultiFactorTimingOverlay,
    TimingOverlayConfig,
    TimingSignal,
)


def _ov(cfg=None) -> MultiFactorTimingOverlay:
    return MultiFactorTimingOverlay(cfg or TimingOverlayConfig())


def _sig(source, direction, strength=1.0):
    return TimingSignal(source=source, direction=direction, strength=strength)


class TestSourcesRegistry:
    def test_six_sources(self):
        assert len(TIMING_SOURCES) == 6

    def test_expected_sources(self):
        expected = {"sentiment_reversal", "regime_shift", "volatility_breakout",
                    "calendar", "volume", "northbound"}
        assert set(TIMING_SOURCES) == expected


class TestWeights:
    def test_ic_weights_normalized(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1), _sig("regime_shift", 1)]
        ic = {"sentiment_reversal": 0.6, "regime_shift": 0.4}
        r = ov.overlay(sigs, ic_weights=ic)
        assert r.weights_used["sentiment_reversal"] == pytest.approx(0.6, abs=1e-6)
        assert r.weights_used["regime_shift"] == pytest.approx(0.4, abs=1e-6)

    def test_negative_weight_clipped(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1), _sig("regime_shift", 1)]
        ic = {"sentiment_reversal": -0.2, "regime_shift": 0.8}
        r = ov.overlay(sigs, ic_weights=ic)
        assert r.weights_used["sentiment_reversal"] == 0.0
        assert r.weights_used["regime_shift"] == pytest.approx(1.0, abs=1e-6)

    def test_all_zero_ic_fallback_equal(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1), _sig("regime_shift", -1)]
        ic = {"sentiment_reversal": 0.0, "regime_shift": 0.0}
        r = ov.overlay(sigs, ic_weights=ic)
        assert r.weights_used["sentiment_reversal"] == pytest.approx(0.5, abs=1e-6)
        assert r.weights_used["regime_shift"] == pytest.approx(0.5, abs=1e-6)
        assert "fallback" in r.notes.lower() or "equal" in r.notes.lower()

    def test_bma_overrides_ic(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1), _sig("regime_shift", -1)]
        ic = {"sentiment_reversal": 0.9, "regime_shift": 0.1}
        bma = {"sentiment_reversal": 0.3, "regime_shift": 0.7}
        r = ov.overlay(sigs, ic_weights=ic, bma_weights=bma)
        assert r.weights_used["sentiment_reversal"] == pytest.approx(0.3, abs=1e-6)
        assert r.weights_used["regime_shift"] == pytest.approx(0.7, abs=1e-6)

    def test_partial_missing_source_zero_weight(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1), _sig("regime_shift", 1)]
        ic = {"sentiment_reversal": 1.0}  # regime_shift 缺失
        r = ov.overlay(sigs, ic_weights=ic)
        assert r.weights_used["regime_shift"] == 0.0


class TestCompositeAndDirection:
    def test_bullish(self):
        ov = _ov()
        sigs = [_sig(s, 1, 1.0) for s in TIMING_SOURCES]
        r = ov.overlay(sigs)
        assert r.composite_score > 0.10
        assert r.direction == "bullish"

    def test_bearish(self):
        ov = _ov()
        sigs = [_sig(s, -1, 1.0) for s in TIMING_SOURCES]
        r = ov.overlay(sigs)
        assert r.composite_score < -0.10
        assert r.direction == "bearish"

    def test_neutral(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1, 0.5), _sig("regime_shift", -1, 0.5)]
        r = ov.overlay(sigs)
        assert -0.10 <= r.composite_score <= 0.10
        assert r.direction == "neutral"


class TestResonance:
    def test_three_same_direction_high_confidence(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1), _sig("regime_shift", 1),
                _sig("volume", 1), _sig("northbound", -1)]
        r = ov.overlay(sigs)
        assert r.resonance_count == 3
        assert r.high_confidence is True

    def test_mixed_no_high_confidence(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1), _sig("regime_shift", -1),
                _sig("volume", 1), _sig("northbound", -1)]
        r = ov.overlay(sigs)
        assert r.high_confidence is False

    def test_custom_resonance_threshold(self):
        ov = _ov(TimingOverlayConfig(resonance_threshold=4))
        sigs = [_sig("sentiment_reversal", 1), _sig("regime_shift", 1),
                _sig("volume", 1)]
        r = ov.overlay(sigs)
        assert r.high_confidence is False


class TestDegraded:
    def test_missing_sources_not_raise(self):
        ov = _ov()
        sigs = [_sig("sentiment_reversal", 1)]
        r = ov.overlay(sigs)
        assert "missing" in r.notes.lower() or "partial" in r.notes.lower()

    def test_empty_signals_raises(self):
        ov = _ov()
        with pytest.raises(ValueError):
            ov.overlay([])


class TestFailClosed:
    def test_unknown_source(self):
        with pytest.raises(ValueError):
            _sig("no_such_source", 1)

    def test_invalid_direction(self):
        with pytest.raises(ValueError):
            _sig("sentiment_reversal", 2)

    def test_strength_out_of_range(self):
        with pytest.raises(ValueError):
            _sig("sentiment_reversal", 1, 1.5)


class TestFrozenAndJson:
    def test_frozen(self):
        s = _sig("sentiment_reversal", 1)
        with pytest.raises(dataclasses.FrozenInstanceError):
            s.direction = -1

    def test_json(self):
        s = _sig("sentiment_reversal", 1)
        assert json.dumps(dataclasses.asdict(s))
