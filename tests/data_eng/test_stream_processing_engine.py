# [BLUEPRINT] MOD-DATENG-004 | docs/03_modules/_domain_data_eng/stream_processing_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATENG-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_eng.test_stream_processing_engine
# [TESTS] src/zephyr/data_eng/stream_processing_engine.py
"""MOD-DATENG-004 单元测试：stream_processing_engine 单机流处理引擎。

蓝图验收（B5-07234/CAND-DATENG-007，B5）：
事件时间滚动/会话窗口聚合（注册+触发判定）+ 水位线与迟到处理
（drop/side_output）+ 背压信号（队列水位阈值回调）+ 聚合落 sink。
事件流/sink/回调全内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_eng.stream_processing_engine",
    reason="stream_processing_engine not importable",
)

from zephyr.data_eng.stream_processing_engine import (  # noqa: E402
    LatePolicy,
    StreamEngineError,
    StreamEvent,
    StreamProcessingEngine,
    WindowKind,
    WindowSpec,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)
_MIN = datetime.timedelta(minutes=1)
_SEC = datetime.timedelta(seconds=1)


def _tumbling(name: str = "t5", minutes: int = 5, late: LatePolicy = LatePolicy.DROP) -> WindowSpec:
    return WindowSpec(name=name, kind=WindowKind.TUMBLING, size=minutes * _MIN, late_policy=late)


def _session(name: str = "s5", minutes: int = 5, late: LatePolicy = LatePolicy.DROP) -> WindowSpec:
    return WindowSpec(name=name, kind=WindowKind.SESSION, gap=minutes * _MIN, late_policy=late)


def _ev(key: str, minutes: int, value: float = 1.0, seconds: int = 0) -> StreamEvent:
    return StreamEvent(key=key, event_time=_T0 + minutes * _MIN + seconds * _SEC, value=value)


# ── 注册 Fail-Closed ──────────────────────────────────────────────────────


def test_register_rejects_empty_name_and_duplicate():
    eng = StreamProcessingEngine()
    with pytest.raises(StreamEngineError, match="name 为空"):
        eng.register_window(WindowSpec(name="", kind=WindowKind.TUMBLING, size=5 * _MIN))
    eng.register_window(_tumbling())
    with pytest.raises(StreamEngineError, match="重复注册"):
        eng.register_window(_tumbling())


def test_register_rejects_bad_tumbling_params():
    eng = StreamProcessingEngine()
    with pytest.raises(StreamEngineError, match="size 非法"):
        eng.register_window(WindowSpec(name="a", kind=WindowKind.TUMBLING))
    with pytest.raises(StreamEngineError, match="不允许 gap"):
        eng.register_window(
            WindowSpec(name="b", kind=WindowKind.TUMBLING, size=5 * _MIN, gap=_MIN)
        )


def test_register_rejects_bad_session_params():
    eng = StreamProcessingEngine()
    with pytest.raises(StreamEngineError, match="gap 非法"):
        eng.register_window(WindowSpec(name="a", kind=WindowKind.SESSION))
    with pytest.raises(StreamEngineError, match="不允许 size"):
        eng.register_window(
            WindowSpec(name="b", kind=WindowKind.SESSION, gap=_MIN, size=5 * _MIN)
        )


def test_init_rejects_bad_args():
    with pytest.raises(StreamEngineError, match="allowed_lateness"):
        StreamProcessingEngine(allowed_lateness=-_SEC)
    with pytest.raises(StreamEngineError, match="max_queue"):
        StreamProcessingEngine(max_queue=0)


# ── ingest Fail-Closed ────────────────────────────────────────────────────


def test_ingest_requires_registered_window():
    eng = StreamProcessingEngine()
    with pytest.raises(StreamEngineError, match="未注册"):
        eng.ingest(_ev("k", 0))


def test_ingest_rejects_empty_key_and_bad_value():
    eng = StreamProcessingEngine()
    eng.register_window(_tumbling())
    with pytest.raises(StreamEngineError, match="key 为空"):
        eng.ingest(_ev("", 0))
    with pytest.raises(StreamEngineError, match="非有限"):
        eng.ingest(_ev("k", 0, value=float("nan")))
    with pytest.raises(StreamEngineError, match="非有限"):
        eng.ingest(_ev("k", 0, value=float("inf")))
    with pytest.raises(StreamEngineError, match="非数值"):
        eng.ingest(_ev("k", 0, value=True))


# ── 水位线与滚动窗口 ──────────────────────────────────────────────────────


def test_watermark_none_before_events_then_tracks_max_seen():
    eng = StreamProcessingEngine(allowed_lateness=10 * _SEC)
    eng.register_window(_tumbling())
    assert eng.watermark is None
    eng.ingest(_ev("k", 1))
    assert eng.watermark == _T0 + _MIN - 10 * _SEC


def test_tumbling_aggregates_and_fires_on_watermark():
    out: list = []
    eng = StreamProcessingEngine(sink=lambda a: out.append(a))
    eng.register_window(_tumbling())
    eng.ingest(_ev("k", 0, 1.0))
    eng.ingest(_ev("k", 1, 2.0))
    assert eng.poll() == ()  # 窗口 [09:30,09:35) end 未过水位线
    eng.ingest(_ev("k", 6, 3.0))  # max_seen=09:36 → wm=09:36 > 09:35
    emitted = eng.poll()
    assert len(emitted) == 1
    agg = emitted[0]
    assert (agg.spec_name, agg.key, agg.count, agg.total) == ("t5", "k", 2, 3.0)
    assert agg.window_start == _T0 and agg.window_end == _T0 + 5 * _MIN
    assert out == list(emitted)  # sink 收到同批输出


def test_tumbling_boundary_event_lands_in_next_window():
    eng = StreamProcessingEngine()
    eng.register_window(_tumbling())
    eng.ingest(_ev("k", 0, 1.0))
    eng.ingest(_ev("k", 5, 2.0))  # 恰在边界 → 下一窗口
    flushed = eng.flush()
    assert [(a.window_start, a.count, a.total) for a in flushed] == [
        (_T0, 1, 1.0),
        (_T0 + 5 * _MIN, 1, 2.0),
    ]


def test_flush_emits_all_open_windows_sorted():
    eng = StreamProcessingEngine()
    eng.register_window(_tumbling())
    eng.ingest(_ev("a", 0, 3.0))
    eng.ingest(_ev("b", 1, 2.0))
    eng.ingest(_ev("a", 7, 1.0))
    flushed = eng.flush()
    assert [(a.key, a.window_start, a.total) for a in flushed] == [
        ("a", _T0, 3.0),
        ("a", _T0 + 5 * _MIN, 1.0),
        ("b", _T0, 2.0),
    ]
    assert eng.stats()["open_tumbling"] == 0


# ── 迟到策略 ──────────────────────────────────────────────────────────────


def test_late_event_dropped_by_default():
    eng = StreamProcessingEngine()
    eng.register_window(_tumbling())
    assert eng.ingest(_ev("k", 10)) is True
    assert eng.ingest(_ev("k", 5)) is False  # wm=09:40，事件 09:35 迟到
    assert eng.stats()["dropped_late"] == 1


def test_late_event_side_output_when_policy_configured():
    side: list = []
    eng = StreamProcessingEngine(side_output_sink=lambda e: side.append(e))
    eng.register_window(_tumbling(late=LatePolicy.SIDE_OUTPUT))
    eng.ingest(_ev("k", 10))
    late_ev = _ev("k", 5)
    assert eng.ingest(late_ev) is False
    assert side == [late_ev]
    assert eng.stats()["side_outputted"] == 1
    assert eng.stats()["dropped_late"] == 0


def test_allowed_lateness_admits_slightly_late_event():
    eng = StreamProcessingEngine(allowed_lateness=6 * _MIN)
    eng.register_window(_tumbling())
    eng.ingest(_ev("k", 10, 1.0))
    assert eng.ingest(_ev("k", 5, 2.0)) is True  # wm=09:34，09:35 不迟到
    flushed = eng.flush()
    assert [(a.window_start, a.total) for a in flushed] == [
        (_T0 + 5 * _MIN, 2.0),
        (_T0 + 10 * _MIN, 1.0),
    ]


def test_event_at_watermark_exactly_is_not_late():
    eng = StreamProcessingEngine()
    eng.register_window(_tumbling())
    eng.ingest(_ev("k", 10))
    assert eng.ingest(_ev("k", 10, value=9.0)) is True  # 恰等于 wm（严格小于才迟到）
    assert eng.stats()["dropped_late"] == 0


# ── 会话窗口 ──────────────────────────────────────────────────────────────


def test_session_window_merges_within_gap_and_closes():
    out: list = []
    eng = StreamProcessingEngine(sink=lambda a: out.append(a))
    eng.register_window(_session())
    eng.ingest(_ev("k", 0, 1.0))
    eng.ingest(_ev("k", 2, 2.0))
    eng.ingest(_ev("k", 4, 3.0))
    assert eng.poll() == ()
    eng.ingest(_ev("k", 10, 9.0))  # wm=09:40 > last(09:34)+gap(5m)=09:39
    emitted = eng.poll()
    assert len(emitted) == 1
    agg = emitted[0]
    assert (agg.window_start, agg.window_end, agg.count, agg.total) == (
        _T0,
        _T0 + 9 * _MIN,
        3,
        6.0,
    )


def test_session_window_splits_beyond_gap():
    eng = StreamProcessingEngine()
    eng.register_window(_session())
    eng.ingest(_ev("k", 0, 1.0))
    eng.ingest(_ev("k", 10, 2.0))
    flushed = eng.flush()
    assert [(a.window_start, a.count, a.total) for a in flushed] == [
        (_T0, 1, 1.0),
        (_T0 + 10 * _MIN, 1, 2.0),
    ]


def test_session_out_of_order_events_merge_deterministically():
    # allowed_lateness 容纳乱序：max_seen=09:40 时 wm=09:25，0/5 分事件不迟到
    eng = StreamProcessingEngine(allowed_lateness=15 * _MIN)
    eng.register_window(_session(minutes=6))
    for m in (10, 0, 5):
        eng.ingest(_ev("k", m, 1.0))
    flushed = eng.flush()
    assert len(flushed) == 1
    assert flushed[0].window_start == _T0
    assert flushed[0].window_end == _T0 + 16 * _MIN
    assert flushed[0].count == 3


def test_sessions_are_per_key():
    eng = StreamProcessingEngine()
    eng.register_window(_session())
    eng.ingest(_ev("a", 0, 1.0))
    eng.ingest(_ev("b", 0, 2.0))
    flushed = eng.flush()
    assert [(a.key, a.total) for a in flushed] == [("a", 1.0), ("b", 2.0)]


# ── 背压 ──────────────────────────────────────────────────────────────────


def test_backpressure_signal_fires_at_queue_threshold():
    signals: list = []
    eng = StreamProcessingEngine(max_queue=3, backpressure_sink=lambda d: signals.append(d))
    eng.register_window(_tumbling())
    eng.ingest(_ev("k", 0))
    eng.ingest(_ev("k", 1))
    assert signals == []
    eng.ingest(_ev("k", 2))
    assert signals == [3]
    eng.poll()  # 排空后水位回落
    eng.ingest(_ev("k", 3))
    assert signals == [3]


# ── sink 健壮性 / 多窗口 / 统计 / 确定性 ──────────────────────────────────


def test_sink_exception_does_not_break_poll():
    eng = StreamProcessingEngine(sink=lambda a: (_ for _ in ()).throw(RuntimeError("x")))
    eng.register_window(_tumbling())
    eng.ingest(_ev("k", 0))
    eng.ingest(_ev("k", 6))
    assert len(eng.poll()) == 1  # 输出仍返回，sink 异常仅日志


def test_event_feeds_all_registered_windows():
    eng = StreamProcessingEngine()
    eng.register_window(_tumbling())
    eng.register_window(_session())
    eng.ingest(_ev("k", 0, 2.0))
    flushed = eng.flush()
    assert {(a.spec_name, a.count, a.total) for a in flushed} == {
        ("t5", 1, 2.0),
        ("s5", 1, 2.0),
    }


def test_stats_snapshot():
    eng = StreamProcessingEngine()
    eng.register_window(_tumbling())
    eng.ingest(_ev("k", 0))
    eng.ingest(_ev("k", 10))
    eng.ingest(_ev("k", 5))  # 迟到丢弃
    s = eng.stats()
    assert s == {
        "pending": 2,
        "open_tumbling": 0,
        "open_sessions": 0,
        "dropped_late": 1,
        "side_outputted": 0,
    }


def test_same_input_same_output():
    def _run():
        eng = StreamProcessingEngine()
        eng.register_window(_tumbling())
        eng.register_window(_session())
        for key, m, v in (("a", 0, 1.0), ("b", 1, 2.0), ("a", 2, 3.0), ("a", 12, 4.0)):
            eng.ingest(_ev(key, m, v))
        return eng.poll() + eng.flush()

    assert _run() == _run()
