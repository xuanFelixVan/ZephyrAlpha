# [A_test] module_id: MOD-GOV_span_stub | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] tests.test_span_stub
# [INVARIANTS] Span命名遵循gen_ai.component.operation风格;W3C TraceContext传播;采样决策由TraceSampler控制
# [MODIFY-GUARD] traces/span_stub.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 采样决策由TraceSampler控制;span结束自动flush到logs
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

ss = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.traces.span_stub",
    reason="span_stub import failed",
)


@pytest.fixture(autouse=True)
def _clear_registry():
    with ss._SPAN_REGISTRY_LOCK:
        ss._SPAN_REGISTRY.clear()
    yield
    with ss._SPAN_REGISTRY_LOCK:
        ss._SPAN_REGISTRY.clear()


class TestTraceContext:
    def test_new_root(self):
        ctx = ss.TraceContext.new_root()
        assert len(ctx.trace_id) == 32
        assert len(ctx.span_id) == 16
        assert ctx.parent_span_id is None

    def test_new_child(self):
        parent = ss.TraceContext.new_root()
        child = ss.TraceContext.new_child(parent)
        assert child.trace_id == parent.trace_id
        assert child.span_id != parent.span_id
        assert child.parent_span_id == parent.span_id

    def test_to_w3c_header(self):
        ctx = ss.TraceContext.new_root()
        header = ctx.to_w3c_header()
        assert header.startswith("00-")
        parts = header.split("-")
        assert len(parts) == 4

    def test_to_log_context(self):
        ctx = ss.TraceContext.new_root()
        log_ctx = ctx.to_log_context()
        assert "trace_id" in log_ctx
        assert "span_id" in log_ctx


class TestSpan:
    def test_creation(self):
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="test_op", context=ctx)
        assert span.name == "test_op"
        assert span.status == "UNSET"

    def test_set_attribute(self):
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="test_op", context=ctx)
        span.set_attribute("key", "value")
        assert span.attributes["key"] == "value"

    def test_add_event(self):
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="test_op", context=ctx)
        span.add_event("event_name", attrs={"detail": "info"})
        assert len(span.events) == 1
        assert span.events[0].name == "event_name"

    def test_finish(self):
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="test_op", context=ctx)
        span.finish("OK")
        assert span.status == "OK"
        assert span.end_time_ns is not None
        assert span.duration_ms is not None

    def test_duration_ms_unfinished(self):
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="test_op", context=ctx)
        assert span.duration_ms is None

    def test_snapshot(self):
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="test_op", context=ctx)
        span.set_attribute("k", "v")
        snap = span.snapshot()
        assert snap["name"] == "test_op"
        assert "trace_id" in snap
        assert snap["attributes"]["k"] == "v"


class TestTraceSampler:
    def test_default_rate(self):
        sampler = ss.TraceSampler()
        assert sampler.base_rate == 0.1

    def test_error_always_sampled(self):
        sampler = ss.TraceSampler()
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="test", context=ctx)
        span.finish("ERROR")
        assert sampler.should_sample(span) is True

    def test_long_duration_sampled(self):
        sampler = ss.TraceSampler(min_duration_ms_for_keep=0.0)
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="test", context=ctx)
        span.finish("OK")
        assert sampler.should_sample(span) is True


class TestNoopSpan:
    def test_context_manager(self):
        with ss.noop_span("test:operation") as span:
            span.set_attribute("key", "value")
        assert span.status == "OK"

    def test_error_finish(self):
        with pytest.raises(ValueError), ss.noop_span("test:error") as span:
            raise ValueError("test error")
        assert span.status == "ERROR"

    def test_with_attributes(self):
        with ss.noop_span("test:attrs", attributes={"preset": "val"}) as span:
            assert span.attributes["preset"] == "val"


class TestListActiveSpans:
    def test_empty(self):
        result = ss.list_active_spans()
        assert result == []

    def test_with_active_span(self):
        with ss.noop_span("active:test") as span:
            active = ss.list_active_spans()
            assert len(active) >= 1
            found = any(s["name"] == "active:test" for s in active)
            assert found


class TestGetTraceTree:
    def test_empty(self):
        result = ss.get_trace_tree("nonexistent_trace")
        assert result == []

    def test_with_spans(self):
        with ss.noop_span("tree:root") as root_span:
            trace_id = root_span.context.trace_id
            tree = ss.get_trace_tree(trace_id)
            assert len(tree) >= 1


class TestBoundary:
    def test_span_empty_name(self):
        ctx = ss.TraceContext.new_root()
        span = ss.Span(name="", context=ctx)
        assert span.name == ""

    def test_noop_span_empty_name(self):
        with ss.noop_span("") as span:
            assert span.name == ""

    def test_trace_context_with_tracestate(self):
        ctx = ss.TraceContext(
            trace_id="a" * 32,
            span_id="b" * 16,
            tracestate="vendor=value",
        )
        assert ctx.tracestate == "vendor=value"

    def test_span_event_creation(self):
        event = ss.SpanEvent(name="test_event", timestamp_ns=1000)
        assert event.name == "test_event"
        assert event.attributes == {}
