# -*- coding: utf-8 -*-
"""MOD-SIG-147 pattern_signal_runtime 链路单测（tmp 隔离，不触库）。"""

from __future__ import annotations

import datetime

import pytest

from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
    Ctr002PayloadValidator,
    PatternSignalRuntime,
)
from zephyr.signal_ashare.strategy_signal.pattern_to_signal_mapper import (
    PatternSignalMapError,
)
from zephyr.signal_ashare.strategy_signal.unified_pattern_engine import (
    KeyPoint,
    PatternClass,
    PatternDirection,
    PatternEvent,
)

_FROZEN_NOW = datetime.datetime(2026, 9, 14, 15, 0, 5)


def _clock() -> datetime.datetime:
    return _FROZEN_NOW


def _make_runtime(**kw) -> PatternSignalRuntime:
    base = dict(clock=_clock, win_rate_query=lambda pid: 0.62)
    base.update(kw)
    return PatternSignalRuntime(**base)


def _head_shoulder_event() -> PatternEvent:
    return PatternEvent(
        pattern_id="PAT-CHART-002",
        pattern_class=PatternClass.REVERSAL,
        name="头肩顶",
        direction=PatternDirection.DOWN,
        confidence=0.8,
        key_points=(
            KeyPoint(idx=5, price=10.0, role="顶1"),
            KeyPoint(idx=9, price=10.5, role="顶2"),
        ),
        historical_win_rate=0.6,
        timeframe="day",
        anchor_idx=9,
    )


# ── 装配 ──────────────────────────────────────────────────────────────────────


def test_assembly_ambiguity_rejected() -> None:
    """provider 与 win_rate_query 同时给=装配歧义，必须拒绝。"""
    with pytest.raises(ValueError, match="二选一"):
        PatternSignalRuntime(
            provider=PatternSignalRuntime(win_rate_query=lambda p: None)._provider,
            win_rate_query=lambda p: None,
            clock=_clock,
        )


def test_build_engine_injects_win_rate_fn() -> None:
    """引擎工厂：注入契约生效（recognize 出的事件带胜率）。"""
    rt = _make_runtime()
    engine = rt.build_engine()
    highs = [10.0, 10.8, 9.9, 10.9, 9.8, 10.85, 9.85, 10.1]
    lows = [9.6, 10.2, 9.5, 10.3, 9.4, 10.25, 9.45, 9.7]
    closes = [9.9, 10.5, 9.7, 10.6, 9.6, 10.55, 9.65, 9.95]
    result = engine.recognize("000001", highs, lows, closes, timeframe="day")
    assert result.events, "合成序列应至少触发一个形态"
    for ev in result.events:
        assert ev.historical_win_rate == pytest.approx(0.62)


# ── on_events 全链路 ─────────────────────────────────────────────────────────


def test_on_events_full_chain() -> None:
    """事件→映射→CTR-002 载荷（方向/强度/止损/校验全通）。"""
    rt = _make_runtime()
    payload = rt.on_events("000001", [_head_shoulder_event()], as_of=_FROZEN_NOW)
    assert payload["contract"] == "CTR-002"
    assert payload["symbol"] == "000001"
    assert payload["values"]["PAT-CHART-002"] == pytest.approx(-0.48)  # -0.8×0.6
    md = payload["metadata"]
    assert md["directions"]["PAT-CHART-002"] == "short"


def test_on_events_empty_events_no_signal() -> None:
    """空事件序列=不出载荷（无形态不发信号）。"""
    rt = _make_runtime()
    assert rt.on_events("000001", [], as_of=_FROZEN_NOW) == {}


def test_on_events_future_asof_rejected() -> None:
    """未来 as_of=映射出口直接拒绝（mapper 既有 PIT 契约透传）。"""
    rt = _make_runtime()
    with pytest.raises(PatternSignalMapError, match="未来信号"):
        rt.on_events(
            "000001",
            [_head_shoulder_event()],
            as_of=_FROZEN_NOW + datetime.timedelta(days=1),
        )


def test_on_events_neutral_no_stop() -> None:
    """中性方向：无关键点位也合法，止损=None，强度带 0 值。"""
    ev = PatternEvent(
        pattern_id="PAT-TREND-013",
        pattern_class=PatternClass.TREND,
        name="均线排列",
        direction=PatternDirection.NEUTRAL,
        confidence=0.5,
        key_points=(),
        historical_win_rate=None,
        timeframe="day",
        anchor_idx=0,
    )
    rt = _make_runtime(win_rate_query=lambda p: None)
    payload = rt.on_events("000001", [ev], as_of=_FROZEN_NOW)
    assert payload["values"]["PAT-TREND-013"] == 0.0


# ── Ctr002PayloadValidator（Fail-Closed 四态） ───────────────────────────────


def _valid_payload() -> dict:
    return {
        "contract": "CTR-002",
        "factor_id": "pattern_signal",
        "source_domain": "ashare_signal",
        "symbol": "000001",
        "values": {"PAT-CHART-002": -0.48},
        "as_of": _FROZEN_NOW.isoformat(),
        "advisory": True,
        "metadata": {},
    }


def test_validator_accepts_valid_payload() -> None:
    v = Ctr002PayloadValidator(clock=_clock)
    assert v(_valid_payload()) is True


def test_validator_rejects_future_asof() -> None:
    p = _valid_payload()
    p["as_of"] = (_FROZEN_NOW + datetime.timedelta(days=1)).isoformat()
    assert Ctr002PayloadValidator(clock=_clock)(p) is False


def test_validator_rejects_empty_values() -> None:
    p = _valid_payload()
    p["values"] = {}
    assert Ctr002PayloadValidator(clock=_clock)(p) is False


def test_validator_fail_closed_on_garbage() -> None:
    """非 Mapping/坏 as_of/None=异常路径，一律 False（Fail-Closed）。"""
    v = Ctr002PayloadValidator(clock=_clock)
    assert v("not-a-mapping") is False
    p = _valid_payload()
    p["as_of"] = "not-a-timestamp"
    assert v(p) is False
    assert v(None) is False
