# [TESTS] tests/signal_ashare/test_resonance_pair.py
# [TTL] permanent
# 波10 G-C.3（MOD-SIG-148）共振条件对定义器单测。
# 镜像测试三纪律（C253 落地）在本套件体现：正反两面同测（入带/出带对称）、
# 缺席面显式降级（最小样本门槛的判定器版）、容差网格三态全测。

import pytest

from zephyr.signal_ashare.resonance_pair import (
    PairResonanceConfig,
    PeakRef,
    ResonanceState,
    UpperEdge,
    judge_resonance_pair,
)


def _edge(level=100.0, touches=3):
    return UpperEdge(level=level, touch_count=touches, last_touch_idx=42)


def _peaks(p1=100.2, p2=99.9):
    return (PeakRef(price=p1, anchor_idx=10), PeakRef(price=p2, anchor_idx=15))


class TestVerdict:
    def test_resonant_ready_not_fired(self):
        # 三前置齐备 → READY_NOT_FIRED（组合态成立且显式不点火）
        v = judge_resonance_pair(_edge(), _peaks())
        assert v.state == ResonanceState.READY_NOT_FIRED.value
        assert v.fired is False  # 铁律载体

    def test_never_fires_regardless_of_input(self):
        # 任何输入下 fired 恒 False（不点火铁律，正反两面同测）
        for edge, peaks in [
            (None, None),
            (_edge(), None),
            (None, _peaks()),
            (_edge(), _peaks()),
            (_edge(touches=0), _peaks()),
            (_edge(level=50.0), _peaks()),
        ]:
            v = judge_resonance_pair(edge, peaks)
            assert v.fired is False

    def test_no_upper_edge(self):
        v = judge_resonance_pair(None, _peaks())
        assert v.state == ResonanceState.NO_UPPER_EDGE.value
        assert v.reasons and "上沿" in v.reasons[0]

    def test_no_double_peak(self):
        v = judge_resonance_pair(_edge(), None)
        assert v.state == ResonanceState.NO_DOUBLE_PEAK.value
        v_bad = judge_resonance_pair(_edge(), (PeakRef(100.0, 1),))
        assert v_bad.state == ResonanceState.NO_DOUBLE_PEAK.value

    def test_not_resonant_peak_out_of_band(self):
        # 双峰一出一入（100.2 入 0.5% 带；93.0 出）→ NOT_RESONANT
        v = judge_resonance_pair(_edge(), _peaks(p2=93.0))
        assert v.state == ResonanceState.NOT_RESONANT.value
        assert any("入带不足" in r for r in v.reasons)

    def test_not_resonant_insufficient_touches(self):
        # 上沿触点不足（多触点确认不成立）
        v = judge_resonance_pair(_edge(touches=1), _peaks())
        assert v.state == ResonanceState.NOT_RESONANT.value
        assert any("触点不足" in r for r in v.reasons)

    def test_strict_double_top_mode(self):
        # peaks_must_be_eq=True：双峰各自入带但价差超并列容差 → NOT_RESONANT
        cfg = PairResonanceConfig(tolerance_pct=0.5, peaks_must_be_eq=True)
        v_eq = judge_resonance_pair(_edge(), _peaks(100.2, 99.9), cfg)  # 差 0.3%
        assert v_eq.state == ResonanceState.READY_NOT_FIRED.value
        v_ne = judge_resonance_pair(_edge(), _peaks(100.4, 99.7), cfg)  # 差 0.7%
        assert v_ne.state == ResonanceState.NOT_RESONANT.value

    def test_tolerance_grid(self):
        # 容差网格三态：带内/带边界/带外
        edge = _edge(level=100.0)
        assert judge_resonance_pair(edge, _peaks(100.2, 99.9)).state == ResonanceState.READY_NOT_FIRED.value
        tight = judge_resonance_pair(edge, _peaks(100.2, 99.9), PairResonanceConfig(tolerance_pct=0.1))
        assert tight.state == ResonanceState.NOT_RESONANT.value  # 紧带下双峰出带


class TestFailClosed:
    def test_upper_edge_validation(self):
        with pytest.raises(ValueError):
            UpperEdge(level=0.0, touch_count=2, last_touch_idx=1)
        with pytest.raises(ValueError):
            UpperEdge(level=float("nan"), touch_count=2, last_touch_idx=1)

    def test_peak_validation(self):
        with pytest.raises(ValueError):
            PeakRef(price=-1.0, anchor_idx=1)
        with pytest.raises(ValueError):
            PeakRef(price=float("inf"), anchor_idx=1)

    def test_config_validation(self):
        with pytest.raises(ValueError):
            PairResonanceConfig(tolerance_pct=0.0)
        with pytest.raises(ValueError):
            PairResonanceConfig(tolerance_pct=11.0)
        with pytest.raises(ValueError):
            PairResonanceConfig(min_touches=0)


class TestJsonSerializable:
    def test_to_dict_roundtrip(self):
        v = judge_resonance_pair(_edge(), _peaks())
        d = v.to_dict()
        assert d["fired"] is False
        assert d["state"] == "ready_not_fired"
        assert d["upper_edge"]["level"] == 100.0
        assert len(d["peaks"]) == 2
