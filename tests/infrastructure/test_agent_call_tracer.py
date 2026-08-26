# [BLUEPRINT] MOD-INF-083 | docs/03_modules/_domain_infrastructure_operations/agent_call_tracer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-083 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.test_agent_call_tracer
# [TESTS] src/zephyr/infrastructure/system_telemetry/agent_call_tracer.py
"""MOD-INF-083 单元测试：agent_call_tracer AI Agent 调用链追踪器。

蓝图验收（B14-04637/CAND-INFRATEL-003，A9运维架构）：
SpanKind 四段（意图/工具调用/LLM/决策）+ Span 树构建与闭合校验（未闭合查询
告警）+ 超预算高亮（over_budget）+ 异常标记 + 审计回调。时钟/审计全注入内存
替身，不触网。
"""

from __future__ import annotations

import datetime
import logging

import pytest

pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.agent_call_tracer",
    reason="agent_call_tracer not importable",
)

from zephyr.infrastructure.system_telemetry.agent_call_tracer import (  # noqa: E402
    AgentCallTracer,
    AgentCallTracerError,
    SpanKind,
    SpanStatus,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


class _Clock:
    """可变注入时钟（确定性推进）。"""

    def __init__(self, t: datetime.datetime) -> None:
        self._t = t

    def __call__(self) -> datetime.datetime:
        return self._t

    def advance(self, **kw) -> None:
        self._t += datetime.timedelta(**kw)


def _tracer(clock=None, **kw) -> AgentCallTracer:
    return AgentCallTracer(clock=clock or _Clock(_T0), **kw)


# ──────────────────────────────────────────────────────────────────────────────
# start_span（树构建 + 校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestStartSpan:
    def test_start_ok(self) -> None:
        span = _tracer().start_span("t-1", SpanKind.INTENT, "意图解析")
        assert span.span_id == "t-1-0001"
        assert span.parent_id is None
        assert span.status is SpanStatus.RUNNING
        assert span.end is None
        assert span.over_budget is False
        assert span.start == _T0

    def test_span_id_deterministic_seq(self) -> None:
        tracer = _tracer()
        s1 = tracer.start_span("t-1", SpanKind.INTENT, "a")
        s2 = tracer.start_span("t-1", SpanKind.LLM, "b", parent_id=s1.span_id)
        assert s2.span_id == "t-1-0002"
        assert s2.parent_id == s1.span_id

    def test_empty_trace_id_raises(self) -> None:
        with pytest.raises(AgentCallTracerError):
            _tracer().start_span("", SpanKind.INTENT, "x")

    def test_empty_name_raises(self) -> None:
        with pytest.raises(AgentCallTracerError):
            _tracer().start_span("t-1", SpanKind.INTENT, "")

    def test_invalid_kind_raises(self) -> None:
        with pytest.raises(AgentCallTracerError):
            _tracer().start_span("t-1", "intent", "x")  # 字符串非枚举

    def test_negative_budget_raises(self) -> None:
        with pytest.raises(AgentCallTracerError):
            _tracer().start_span("t-1", SpanKind.LLM, "x", budget_ms=-1)

    def test_unknown_parent_raises(self) -> None:
        with pytest.raises(AgentCallTracerError):
            _tracer().start_span("t-1", SpanKind.LLM, "x", parent_id="ghost")

    def test_cross_trace_parent_raises(self) -> None:
        tracer = _tracer()
        parent = tracer.start_span("t-1", SpanKind.INTENT, "a")
        with pytest.raises(AgentCallTracerError):
            tracer.start_span("t-2", SpanKind.LLM, "b", parent_id=parent.span_id)

    def test_closed_parent_rejected(self) -> None:
        tracer = _tracer()
        parent = tracer.start_span("t-1", SpanKind.INTENT, "a")
        tracer.end_span(parent.span_id)
        with pytest.raises(AgentCallTracerError):
            tracer.start_span("t-1", SpanKind.LLM, "b", parent_id=parent.span_id)


# ──────────────────────────────────────────────────────────────────────────────
# end_span（闭合校验 + 高亮）
# ──────────────────────────────────────────────────────────────────────────────


class TestEndSpan:
    def test_end_ok(self) -> None:
        clock = _Clock(_T0)
        tracer = _tracer(clock)
        span = tracer.start_span("t-1", SpanKind.TOOL_CALL, "取行情", budget_ms=500)
        clock.advance(milliseconds=120)
        closed = tracer.end_span(span.span_id)
        assert closed.status is SpanStatus.OK
        assert closed.end == _T0 + datetime.timedelta(milliseconds=120)
        assert closed.duration_ms == pytest.approx(120.0)
        assert closed.over_budget is False

    def test_over_budget_highlighted(self) -> None:
        clock = _Clock(_T0)
        tracer = _tracer(clock)
        span = tracer.start_span("t-1", SpanKind.LLM, "推理", budget_ms=50)
        clock.advance(milliseconds=100)
        closed = tracer.end_span(span.span_id)
        assert closed.over_budget is True
        assert tracer.get_span(span.span_id).over_budget is True

    def test_under_budget_not_highlighted(self) -> None:
        clock = _Clock(_T0)
        tracer = _tracer(clock)
        span = tracer.start_span("t-1", SpanKind.LLM, "推理", budget_ms=200)
        clock.advance(milliseconds=100)
        assert tracer.end_span(span.span_id).over_budget is False

    def test_end_error_marked(self) -> None:
        tracer = _tracer()
        span = tracer.start_span("t-1", SpanKind.DECISION, "决策输出")
        closed = tracer.end_span(span.span_id, SpanStatus.ERROR, error="LLM 超时")
        assert closed.status is SpanStatus.ERROR
        assert closed.error == "LLM 超时"

    def test_end_unknown_raises(self) -> None:
        with pytest.raises(AgentCallTracerError):
            _tracer().end_span("ghost")

    def test_double_end_raises(self) -> None:
        tracer = _tracer()
        span = tracer.start_span("t-1", SpanKind.INTENT, "a")
        tracer.end_span(span.span_id)
        with pytest.raises(AgentCallTracerError):
            tracer.end_span(span.span_id)

    def test_end_running_status_raises(self) -> None:
        tracer = _tracer()
        span = tracer.start_span("t-1", SpanKind.INTENT, "a")
        with pytest.raises(AgentCallTracerError):
            tracer.end_span(span.span_id, SpanStatus.RUNNING)


# ──────────────────────────────────────────────────────────────────────────────
# 查询（未闭合告警 / 排序 / 树）
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_unclosed_warns_and_returns(self, caplog) -> None:
        tracer = _tracer()
        tracer.start_span("t-1", SpanKind.INTENT, "a")
        with caplog.at_level(logging.WARNING):
            unclosed = tracer.unclosed_spans()
        assert [s.span_id for s in unclosed] == ["t-1-0001"]
        assert "未闭合" in caplog.text

    def test_unclosed_empty_after_end(self) -> None:
        tracer = _tracer()
        span = tracer.start_span("t-1", SpanKind.INTENT, "a")
        tracer.end_span(span.span_id)
        assert tracer.unclosed_spans() == ()

    def test_trace_spans_sorted(self) -> None:
        tracer = _tracer()
        root = tracer.start_span("t-1", SpanKind.INTENT, "root")
        child = tracer.start_span("t-1", SpanKind.LLM, "child", parent_id=root.span_id)
        spans = tracer.trace_spans("t-1")
        assert [s.span_id for s in spans] == [root.span_id, child.span_id]

    def test_trace_tree_nesting(self) -> None:
        tracer = _tracer()
        root = tracer.start_span("t-1", SpanKind.INTENT, "意图")
        tool = tracer.start_span("t-1", SpanKind.TOOL_CALL, "工具", parent_id=root.span_id)
        tracer.start_span("t-1", SpanKind.LLM, "推理", parent_id=tool.span_id)
        tree = tracer.trace_tree("t-1")
        assert len(tree) == 1
        assert tree[0]["span"].span_id == root.span_id
        assert tree[0]["children"][0]["span"].span_id == tool.span_id
        assert tree[0]["children"][0]["children"][0]["span"].kind is SpanKind.LLM


# ──────────────────────────────────────────────────────────────────────────────
# 审计回调
# ──────────────────────────────────────────────────────────────────────────────


class TestAudit:
    def test_audit_on_end(self) -> None:
        closed_spans: list = []
        tracer = _tracer(audit_sink=lambda s: closed_spans.append(s))
        span = tracer.start_span("t-1", SpanKind.DECISION, "决策")
        tracer.end_span(span.span_id)
        assert [s.span_id for s in closed_spans] == [span.span_id]
        assert closed_spans[0].status is SpanStatus.OK

    def test_audit_exception_swallowed(self) -> None:
        def _bad(span) -> None:
            raise RuntimeError("审计后端故障")

        tracer = _tracer(audit_sink=_bad)
        span = tracer.start_span("t-1", SpanKind.INTENT, "a")
        closed = tracer.end_span(span.span_id)  # 不阻断追踪
        assert closed.status is SpanStatus.OK
