# [BLUEPRINT] MOD-FE-009 | docs/03_modules/_domain_frontend/trace_waterfall_view/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-009 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_trace_waterfall_view
# [TESTS] src/zephyr/frontend/trace_waterfall_view.py
"""MOD-FE-009 单元测试：trace_waterfall_view 端到端追踪瀑布视图器。

蓝图验收（B14-04627/CAND-FE-010，A9 D-FRONTEND-15，承接 CAND-FE-005 归并）：
四视图词表闭合 + trace_id 检索（span 存储注入）+ 瀑布布局（DFS 先序父子
嵌套时间轴）+ 采样率配置（哈希确定性）+ 慢链路高亮（视图阈值映射）。
span 存储全内存替身注入，不触网/不埋点。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.frontend.trace_waterfall_view",
    reason="trace_waterfall_view not importable",
)

from zephyr.frontend.trace_waterfall_view import (  # noqa: E402
    Span,
    TraceChainView,
    TraceViewError,
    TraceWaterfallView,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _span(
    span_id: str,
    parent: str | None = None,
    *,
    trace_id: str = "t-1",
    view: TraceChainView = TraceChainView.TRADE_MAIN,
    start_offset_ms: float = 0.0,
    duration_ms: float = 100.0,
    name: str = "",
) -> Span:
    return Span(
        span_id=span_id,
        trace_id=trace_id,
        parent_span_id=parent,
        name=name or span_id,
        view=view,
        start_ts=_T0 + datetime.timedelta(milliseconds=start_offset_ms),
        duration_ms=duration_ms,
    )


def _view(
    spans: dict[str, list[Span]] | None = None,
    **kwargs,
) -> TraceWaterfallView:
    store_data = spans if spans is not None else {"t-1": [_span("root")]}
    return TraceWaterfallView(span_store=lambda tid: store_data.get(tid, []), **kwargs)


def _tree_spans() -> dict[str, list[Span]]:
    # root(0→400) ├─ childA(50→650) │  └─ grandA(100→150) └─ childB(200→100)
    return {"t-1": [
        _span("root", duration_ms=400.0),
        _span("childA", "root", start_offset_ms=50.0, duration_ms=600.0),
        _span("grandA", "childA", start_offset_ms=100.0, duration_ms=50.0),
        _span("childB", "root", start_offset_ms=200.0, duration_ms=100.0),
    ]}


# ──────────────────────────────────────────────────────────────────────────────
# 构造与配置（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_ok(self) -> None:
        view = _view()
        assert view.views() == (
            TraceChainView.TRADE_MAIN,
            TraceChainView.DATA_CHAIN,
            TraceChainView.AI_OPS,
            TraceChainView.GPU_INFER,
        )

    def test_store_missing_raises(self) -> None:
        with pytest.raises(TraceViewError):
            TraceWaterfallView(span_store=None)

    def test_invalid_sampling_rate_raises(self) -> None:
        for bad in (0, -0.5, 1.5, True):
            with pytest.raises(TraceViewError):
                _view(sampling_rate=bad)

    def test_custom_threshold_ok(self) -> None:
        view = _view(spans=_tree_spans(),
                     slow_threshold_ms={TraceChainView.TRADE_MAIN: 500.0})
        payload = view.waterfall("t-1")
        slow = {r.span_id for r in payload.rows if r.slow}
        assert slow == {"childA"}  # 600ms ≥ 500

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(TraceViewError):
            _view(slow_threshold_ms={"trade_main": 100.0})  # type: ignore[dict-item]
        with pytest.raises(TraceViewError):
            _view(slow_threshold_ms={TraceChainView.TRADE_MAIN: 0})


# ──────────────────────────────────────────────────────────────────────────────
# 采样率（哈希确定性）
# ──────────────────────────────────────────────────────────────────────────────


class TestSampling:
    def test_rate_one_always_sampled(self) -> None:
        view = _view(sampling_rate=1.0)
        assert view.should_sample("trace-alpha")
        assert view.should_sample("trace-beta")

    def test_tiny_rate_never_sampled(self) -> None:
        view = _view(sampling_rate=1e-9)
        assert not view.should_sample("trace-alpha")

    def test_deterministic_across_instances(self) -> None:
        v1 = _view(sampling_rate=0.5)
        v2 = _view(sampling_rate=0.5)
        assert v1.should_sample("trace-gamma") == v2.should_sample("trace-gamma")

    def test_blank_trace_id_raises(self) -> None:
        with pytest.raises(TraceViewError):
            _view().should_sample("")


# ──────────────────────────────────────────────────────────────────────────────
# trace 检索与瀑布布局
# ──────────────────────────────────────────────────────────────────────────────


class TestWaterfall:
    def test_unknown_or_blank_trace_raises(self) -> None:
        view = _view()
        with pytest.raises(TraceViewError):
            view.waterfall("ghost")
        with pytest.raises(TraceViewError):
            view.waterfall("")

    def test_single_root_row(self) -> None:
        payload = _view().waterfall("t-1")
        assert payload.trace_id == "t-1"
        assert len(payload.rows) == 1
        row = payload.rows[0]
        assert row.depth == 0
        assert row.start_offset_ms == 0.0
        assert payload.total_duration_ms == 100.0

    def test_dfs_preorder_nesting(self) -> None:
        payload = _view(spans=_tree_spans()).waterfall("t-1")
        order = [r.span_id for r in payload.rows]
        assert order == ["root", "childA", "grandA", "childB"]  # 父子嵌套先序
        depths = {r.span_id: r.depth for r in payload.rows}
        assert depths == {"root": 0, "childA": 1, "grandA": 2, "childB": 1}

    def test_start_offset_relative_to_trace_start(self) -> None:
        payload = _view(spans=_tree_spans()).waterfall("t-1")
        offsets = {r.span_id: r.start_offset_ms for r in payload.rows}
        assert offsets == {"root": 0.0, "childA": 50.0, "grandA": 100.0, "childB": 200.0}

    def test_total_duration_max_end(self) -> None:
        payload = _view(spans=_tree_spans()).waterfall("t-1")
        # childA 结束 650ms 最晚 → 总时长 650
        assert payload.total_duration_ms == 650.0

    def test_slow_highlight_default_threshold(self) -> None:
        payload = _view(spans=_tree_spans()).waterfall("t-1")
        slow = {r.span_id for r in payload.rows if r.slow}
        assert slow == {"childA"}  # 600ms ≥ 交易主链默认 500ms
        assert payload.slow_count == 1

    def test_slow_threshold_per_view(self) -> None:
        spans = {"t-1": [
            _span("gpu", view=TraceChainView.GPU_INFER, duration_ms=900.0),
            _span("trade", view=TraceChainView.TRADE_MAIN, duration_ms=900.0),
        ]}
        payload = _view(spans=spans).waterfall("t-1")
        slow = {r.span_id: r.slow for r in payload.rows}
        assert slow["gpu"] is True    # 900 ≥ GPU 默认 800
        assert slow["trade"] is True  # 900 ≥ 交易 500
        spans2 = {"t-1": [
            _span("gpu", view=TraceChainView.GPU_INFER, duration_ms=600.0),
        ]}
        payload2 = _view(spans=spans2).waterfall("t-1")
        assert payload2.rows[0].slow is False  # 600 < 800

    def test_siblings_ordered_by_start(self) -> None:
        spans = {"t-1": [
            _span("root", duration_ms=1000.0),
            _span("b_late", "root", start_offset_ms=300.0),
            _span("a_early", "root", start_offset_ms=100.0),
        ]}
        payload = _view(spans=spans).waterfall("t-1")
        assert [r.span_id for r in payload.rows] == ["root", "a_early", "b_late"]


# ──────────────────────────────────────────────────────────────────────────────
# span 校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestSpanValidation:
    def test_trace_id_mismatch_raises(self) -> None:
        spans = {"t-1": [_span("s1", trace_id="other")]}
        with pytest.raises(TraceViewError):
            _view(spans=spans).waterfall("t-1")

    def test_duplicate_span_id_raises(self) -> None:
        spans = {"t-1": [_span("s1"), _span("s1")]}
        with pytest.raises(TraceViewError):
            _view(spans=spans).waterfall("t-1")

    def test_unknown_parent_raises(self) -> None:
        spans = {"t-1": [_span("s1", "ghost")]}
        with pytest.raises(TraceViewError):
            _view(spans=spans).waterfall("t-1")

    def test_parent_cycle_raises(self) -> None:
        spans = {"t-1": [_span("a", "b"), _span("b", "a")]}
        with pytest.raises(TraceViewError):
            _view(spans=spans).waterfall("t-1")

    def test_self_parent_raises(self) -> None:
        spans = {"t-1": [_span("a", "a")]}
        with pytest.raises(TraceViewError):
            _view(spans=spans).waterfall("t-1")

    def test_negative_duration_raises(self) -> None:
        spans = {"t-1": [_span("s1", duration_ms=-1.0)]}
        with pytest.raises(TraceViewError):
            _view(spans=spans).waterfall("t-1")

    def test_non_span_item_raises(self) -> None:
        spans = {"t-1": ["not-a-span"]}  # type: ignore[list-item]
        with pytest.raises(TraceViewError):
            _view(spans=spans).waterfall("t-1")

    def test_deterministic(self) -> None:
        view = _view(spans=_tree_spans())
        assert view.waterfall("t-1") == view.waterfall("t-1")
