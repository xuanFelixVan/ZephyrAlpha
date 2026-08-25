# [A_test] module_id: MOD-SIG-100 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-100 | docs/03_modules/_domain_signal/false_breakout_trap_detector/blueprint.md
# [MODULE] tests.signal_ashare.test_false_breakout_trap_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""假突破与诱多检测模型（MOD-SIG-100，B10-01370）施工验证测试。

覆盖：
- 突破确认：收盘过压力位+放量 ≥1.5× 确认；未过位不判定；
- 假突破判定：N=3 日回落逐根检查、失败速度（次日回落=极弱）、未决 pending；
- 诱多三特征：缩量 40/CVD 背离 35/尾盘 25、缺数据腿降级、suspected 阈值；
- 假突破率滚动统计：窗口截断、基线 40-50% 比较、elevated/below、小样本降级；
- fail-closed：非法压力位/越界索引/负价负量/空序列/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.false_breakout_trap_detector import (
    Bar,
    BreakoutEvent,
    FalseBreakoutConfig,
    FalseBreakoutTrapDetector,
)

RES = 10.0


def _engine() -> FalseBreakoutTrapDetector:
    return FalseBreakoutTrapDetector(FalseBreakoutConfig())


def _bar(close: float, vol: float = 1000.0) -> Bar:
    return Bar(open=close, high=close + 0.1, low=close - 0.1, close=close, volume=vol)


def _base_bars(n: int = 26) -> list[Bar]:
    """压力位下方横盘序列（均量 1000）。"""
    return [_bar(9.5, 1000.0) for _ in range(n)]


def _events(falses: int, trues: int) -> list[BreakoutEvent]:
    return [BreakoutEvent(false_breakout=True) for _ in range(falses)] + [
        BreakoutEvent(false_breakout=False) for _ in range(trues)
    ]


class TestConfigValidation:
    def test_default_config_ok(self) -> None:
        FalseBreakoutConfig()

    @pytest.mark.parametrize(
        "field,value",
        [
            ("confirm_volume_ratio", 1.0),
            ("false_check_days", 0),
            ("vol_avg_window", 4),
            ("cvd_lookback", 1),
            ("tail_breakout_minute", -1.0),
            ("trap_threshold", 0.0),
            ("trap_threshold", 100.1),
            ("stats_window", 4),
            ("stats_min_events", 0),
            ("baseline_low", 0.6),
            ("baseline_high", 0.3),
        ],
    )
    def test_invalid_config_raises(self, field: str, value: float) -> None:
        with pytest.raises(ValueError):
            FalseBreakoutConfig(**{field: value})


class TestEvaluate:
    def test_true_breakout_after_3_days(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0), _bar(10.6), _bar(10.7), _bar(10.8)]
        ev = _engine().evaluate(bars, RES, 26)
        assert ev.breakout is True
        assert ev.confirmed is True  # 2000 ≥ 1.5×1000
        assert ev.false_breakout is False
        assert ev.fail_speed_days is None
        assert ev.pending is False

    def test_false_breakout_speed2(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0), _bar(10.6), _bar(9.8), _bar(10.9)]
        ev = _engine().evaluate(bars, RES, 26)
        assert ev.false_breakout is True
        assert ev.fail_speed_days == 2
        assert ev.pending is False

    def test_extreme_weak_speed1(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0), _bar(9.7), _bar(10.9), _bar(11.0)]
        ev = _engine().evaluate(bars, RES, 26)
        assert ev.false_breakout is True
        assert ev.fail_speed_days == 1  # 次日即回落=极弱

    def test_pending_at_last_bar(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0)]
        ev = _engine().evaluate(bars, RES, 26)
        assert ev.pending is True
        assert ev.false_breakout is None

    def test_pending_partial_follow(self) -> None:
        # 仅 1 根后续且未回落 → 未决
        bars = _base_bars() + [_bar(10.5, 2000.0), _bar(10.6)]
        ev = _engine().evaluate(bars, RES, 26)
        assert ev.pending is True
        assert ev.false_breakout is None

    def test_not_breakout(self) -> None:
        bars = _base_bars() + [_bar(9.9, 2000.0)]
        ev = _engine().evaluate(bars, RES, 26)
        assert ev.breakout is False
        assert ev.false_breakout is None
        assert ev.pending is False

    def test_volume_not_confirmed(self) -> None:
        bars = _base_bars() + [_bar(10.5, 1200.0), _bar(10.6), _bar(10.7), _bar(10.8)]
        ev = _engine().evaluate(bars, RES, 26)
        assert ev.confirmed is False  # 1200 < 1.5×1000


class TestTrapFeatures:
    def test_shrink_breakout_40(self) -> None:
        bars = _base_bars() + [_bar(10.5, 800.0), _bar(10.6), _bar(10.7), _bar(10.8)]
        ev = _engine().evaluate(bars, RES, 26)
        assert ev.trap.shrink_points == 40.0
        assert ev.trap.cvd_points == 0.0  # 未注入 CVD → 降级
        assert any("CVD" in n for n in ev.notes)

    def test_cvd_divergence_35(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0), _bar(10.6), _bar(10.7), _bar(10.8)]
        # 前高（横盘 9.5 区，参考根=前 20 根内收盘最高根）CVD=5000，突破根 CVD=3000 → 背离
        cvd = [5000.0] * 26 + [3000.0, 3100.0, 3200.0, 3300.0]
        ev = _engine().evaluate(bars, RES, 26, cvd=cvd)
        assert ev.trap.cvd_points == 35.0

    def test_cvd_no_divergence(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0), _bar(10.6), _bar(10.7), _bar(10.8)]
        cvd = [3000.0] * 26 + [5000.0, 5100.0, 5200.0, 5300.0]
        ev = _engine().evaluate(bars, RES, 26, cvd=cvd)
        assert ev.trap.cvd_points == 0.0

    def test_tail_breakout_25(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0), _bar(10.6), _bar(10.7), _bar(10.8)]
        ev = _engine().evaluate(bars, RES, 26, breakout_minute=280.0)
        assert ev.trap.tail_points == 25.0

    def test_full_trap_suspected(self) -> None:
        bars = _base_bars() + [_bar(10.5, 800.0), _bar(10.6), _bar(10.7), _bar(10.8)]
        cvd = [5000.0] * 26 + [3000.0, 3100.0, 3200.0, 3300.0]
        ev = _engine().evaluate(bars, RES, 26, cvd=cvd, breakout_minute=285.0)
        assert ev.trap.score == pytest.approx(100.0)
        assert ev.trap.suspected is True

    def test_cvd_length_mismatch_raises(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0)]
        with pytest.raises(ValueError):
            _engine().evaluate(bars, RES, 26, cvd=[1.0] * 10)


class TestRollingStats:
    def test_half_false_not_elevated(self) -> None:
        st = _engine().rolling_stats(_events(5, 5))
        assert st.false_rate == pytest.approx(0.5)
        assert st.elevated is False  # 严格 >
        assert st.below_baseline is False
        assert st.sufficient is True

    def test_elevated_above_baseline(self) -> None:
        st = _engine().rolling_stats(_events(6, 4))
        assert st.false_rate == pytest.approx(0.6)
        assert st.elevated is True

    def test_below_baseline(self) -> None:
        st = _engine().rolling_stats(_events(3, 7))
        assert st.false_rate == pytest.approx(0.3)
        assert st.below_baseline is True

    def test_window_truncates(self) -> None:
        # 25 个事件（前 5 全真），窗口 20 → 只计后 20 个（全假）
        events = _events(0, 5) + _events(20, 0)
        st = _engine().rolling_stats(events)
        assert st.total == 20
        assert st.false_rate == pytest.approx(1.0)

    def test_insufficient_events_degraded(self) -> None:
        st = _engine().rolling_stats(_events(2, 1))
        assert st.total == 3
        assert st.sufficient is False
        assert st.degraded is True

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().rolling_stats([])


class TestValidation:
    def test_invalid_resistance(self) -> None:
        with pytest.raises(ValueError):
            _engine().evaluate(_base_bars(), 0.0, 10)

    def test_index_out_of_range(self) -> None:
        with pytest.raises(ValueError):
            _engine().evaluate(_base_bars(), RES, 99)

    def test_empty_bars(self) -> None:
        with pytest.raises(ValueError):
            _engine().evaluate([], RES, 0)

    def test_negative_price(self) -> None:
        bars = _base_bars()
        bars[3] = Bar(open=9.0, high=9.1, low=-0.5, close=9.0, volume=1000.0)
        with pytest.raises(ValueError):
            _engine().evaluate(bars, RES, 25)


class TestContract:
    def test_frozen_and_json_serializable(self) -> None:
        bars = _base_bars() + [_bar(10.5, 2000.0), _bar(10.6), _bar(10.7), _bar(10.8)]
        ev = _engine().evaluate(bars, RES, 26)
        with pytest.raises(dataclasses.FrozenInstanceError):
            ev.breakout = False  # type: ignore[misc]
        json.dumps(ev.to_dict())
        st = _engine().rolling_stats(_events(5, 5))
        json.dumps(st.to_dict())
