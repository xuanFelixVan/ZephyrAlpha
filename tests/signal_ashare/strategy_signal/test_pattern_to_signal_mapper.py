# [BLUEPRINT] MOD-SIG-115 | docs/03_modules/_domain_signal/pattern_to_signal_mapper/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-115 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_pattern_to_signal_mapper
# [TESTS] src/zephyr/signal_ashare/pattern_to_signal_mapper.py
"""MOD-SIG-115 单元测试：pattern_to_signal_mapper 形态信号转化层。

蓝图验收（B1-00849/CAND-TESTB-033，C2 97）：
PatternEvent → 方向/强度/止损映射（置信度×胜率加权 + 关键点位外扩 k%）
+ CTR-002 兼容输出（注入校验器，未注入/拒绝 Fail-Closed）。
内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.pattern_to_signal_mapper",
    reason="pattern_to_signal_mapper not importable",
)

from zephyr.signal_ashare.pattern_to_signal_mapper import (  # noqa: E402
    MappedSignal,
    PatternSignalMapError,
    PatternToSignalMapper,
    SignalDirection,
)
from zephyr.signal_ashare.unified_pattern_engine import (  # noqa: E402
    KeyPoint,
    PatternClass,
    PatternDirection,
    PatternEvent,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _mapper(**kwargs) -> PatternToSignalMapper:
    kwargs.setdefault("clock", lambda: _T0)
    kwargs.setdefault("validator", lambda s: True)
    return PatternToSignalMapper(**kwargs)


def _event(
    *,
    pattern_id: str = "p1",
    name: str = "双底",
    direction: PatternDirection = PatternDirection.UP,
    confidence: float = 0.8,
    win_rate: float | None = 0.6,
    key_points: tuple[KeyPoint, ...] = (
        KeyPoint(idx=1, price=10.0, role="谷"),
        KeyPoint(idx=5, price=10.2, role="谷"),
    ),
) -> PatternEvent:
    return PatternEvent(
        pattern_id=pattern_id,
        pattern_class=PatternClass.REVERSAL,
        name=name,
        direction=direction,
        confidence=confidence,
        key_points=key_points,
        historical_win_rate=win_rate,
        timeframe="1d",
        anchor_idx=5,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_stop_buffer_out_of_range_raises(self) -> None:
        with pytest.raises(PatternSignalMapError):
            _mapper(stop_buffer_pct=0.0)
        with pytest.raises(PatternSignalMapError):
            _mapper(stop_buffer_pct=100.0)

    def test_default_win_rate_out_of_range_raises(self) -> None:
        with pytest.raises(PatternSignalMapError):
            _mapper(default_win_rate=1.5)


# ──────────────────────────────────────────────────────────────────────────────
# 映射
# ──────────────────────────────────────────────────────────────────────────────


class TestMap:
    def test_long_mapping(self) -> None:
        m = _mapper(stop_buffer_pct=1.0)
        sig = m.map_event(_event())
        assert sig.direction is SignalDirection.LONG
        assert sig.strength == pytest.approx(0.8 * 0.6)
        # LONG 止损=最低关键点位×(1-1%)
        assert sig.stop_loss == pytest.approx(10.0 * 0.99)
        assert sig.advisory is True

    def test_short_mapping(self) -> None:
        m = _mapper(stop_buffer_pct=2.0)
        sig = m.map_event(_event(direction=PatternDirection.DOWN))
        assert sig.direction is SignalDirection.SHORT
        # SHORT 止损=最高关键点位×(1+2%)
        assert sig.stop_loss == pytest.approx(10.2 * 1.02)

    def test_neutral_no_stop(self) -> None:
        m = _mapper()
        sig = m.map_event(_event(direction=PatternDirection.NEUTRAL))
        assert sig.direction is SignalDirection.NEUTRAL
        assert sig.stop_loss is None
        assert sig.notes

    def test_win_rate_none_uses_default(self) -> None:
        m = _mapper(default_win_rate=0.5)
        sig = m.map_event(_event(win_rate=None, confidence=0.8))
        assert sig.strength == pytest.approx(0.8 * 0.5)

    def test_confidence_out_of_range_raises(self) -> None:
        m = _mapper()
        with pytest.raises(PatternSignalMapError):
            m.map_event(_event(confidence=1.5))

    def test_win_rate_out_of_range_raises(self) -> None:
        m = _mapper()
        with pytest.raises(PatternSignalMapError):
            m.map_event(_event(win_rate=-0.1))

    def test_no_key_points_raises(self) -> None:
        m = _mapper()
        with pytest.raises(PatternSignalMapError):
            m.map_event(_event(key_points=()))

    def test_batch_sorted(self) -> None:
        m = _mapper()
        out = m.map_batch([_event(pattern_id="p2"), _event(pattern_id="p1")])
        assert [s.pattern_id for s in out] == ["p1", "p2"]


# ──────────────────────────────────────────────────────────────────────────────
# CTR-002 输出
# ──────────────────────────────────────────────────────────────────────────────


class TestEmit:
    def test_emit_ok(self) -> None:
        seen: list[dict] = []
        m = _mapper(validator=lambda s: seen.append(s) or True)
        sig = m.map_event(_event())
        payload = m.emit_signal("000001", [sig], as_of=_T0)
        assert payload["contract"] == "CTR-002"
        assert payload["advisory"] is True
        assert payload["values"]["p1"] == pytest.approx(0.48)
        assert seen == [payload]

    def test_emit_short_negative_value(self) -> None:
        m = _mapper()
        sig = m.map_event(_event(direction=PatternDirection.DOWN))
        payload = m.emit_signal("000001", [sig], as_of=_T0)
        assert payload["values"]["p1"] == pytest.approx(-0.48)

    def test_emit_validator_missing_raises(self) -> None:
        m = PatternToSignalMapper(clock=lambda: _T0, validator=None)
        sig = m.map_event(_event())
        with pytest.raises(PatternSignalMapError):
            m.emit_signal("000001", [sig], as_of=_T0)

    def test_emit_validator_rejects_raises(self) -> None:
        m = _mapper(validator=lambda s: False)
        sig = m.map_event(_event())
        with pytest.raises(PatternSignalMapError):
            m.emit_signal("000001", [sig], as_of=_T0)

    def test_emit_validator_exception_raises(self) -> None:
        def _boom(s):
            raise RuntimeError("validator crash")

        m = _mapper(validator=_boom)
        sig = m.map_event(_event())
        with pytest.raises(PatternSignalMapError):
            m.emit_signal("000001", [sig], as_of=_T0)

    def test_emit_empty_signals_raises(self) -> None:
        m = _mapper()
        with pytest.raises(PatternSignalMapError):
            m.emit_signal("000001", [], as_of=_T0)

    def test_emit_blank_symbol_raises(self) -> None:
        m = _mapper()
        sig = m.map_event(_event())
        with pytest.raises(PatternSignalMapError):
            m.emit_signal("  ", [sig], as_of=_T0)

    def test_emit_future_as_of_raises(self) -> None:
        m = _mapper()
        sig = m.map_event(_event())
        future = _T0 + datetime.timedelta(days=1)
        with pytest.raises(PatternSignalMapError):
            m.emit_signal("000001", [sig], as_of=future)


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        m1 = _mapper()
        m2 = _mapper()
        e = _event()
        assert m1.map_event(e) == m2.map_event(e)
