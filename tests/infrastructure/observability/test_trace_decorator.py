# [A_test] module_id: MOD-GOV_trace_decorator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-440 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_trace_decorator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] pytest tests/test_trace_decorator.py
# [TTL] task_bound

from __future__ import annotations

import json

import pytest

from zephyr.infrastructure.observability.trace_decorator import (
    TraceCollector,
    TraceSpan,
    trace,
)


class TestTraceSpanDataclass:
    def test_default_error(self):
        span = TraceSpan(
            span_id="op-123",
            operation="op",
            start_time="2026-01-01T00:00:00+00:00",
            end_time="2026-01-01T00:00:01+00:00",
            duration_ms=1000.0,
            success=True,
        )
        assert span.error == ""

    def test_with_error(self):
        span = TraceSpan(
            span_id="op-456",
            operation="op",
            start_time="2026-01-01T00:00:00+00:00",
            end_time="2026-01-01T00:00:01+00:00",
            duration_ms=500.0,
            success=False,
            error="ValueError",
        )
        assert span.success is False
        assert span.error == "ValueError"


class TestTraceCollector:
    def setup_method(self):
        TraceCollector.reset_instance()

    def test_get_instance_creates_singleton(self):
        inst1 = TraceCollector.get_instance()
        inst2 = TraceCollector.get_instance()
        assert inst1 is inst2

    def test_add_span(self):
        collector = TraceCollector()
        span = TraceSpan(
            span_id="test-1",
            operation="test_op",
            start_time="2026-01-01T00:00:00+00:00",
            end_time="2026-01-01T00:00:01+00:00",
            duration_ms=1000.0,
            success=True,
        )
        collector.add_span(span)
        assert len(collector.spans) == 1
        assert collector.spans[0].span_id == "test-1"

    def test_add_multiple_spans(self):
        collector = TraceCollector()
        for i in range(3):
            collector.add_span(
                TraceSpan(
                    span_id=f"span-{i}",
                    operation=f"op-{i}",
                    start_time="2026-01-01T00:00:00+00:00",
                    end_time="2026-01-01T00:00:01+00:00",
                    duration_ms=100.0,
                    success=True,
                )
            )
        assert len(collector.spans) == 3

    def test_flush_writes_file(self, tmp_path, monkeypatch):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        collector.add_span(
            TraceSpan(
                span_id="flush-1",
                operation="flush_op",
                start_time="2026-01-01T00:00:00+00:00",
                end_time="2026-01-01T00:00:01+00:00",
                duration_ms=500.0,
                success=True,
            )
        )
        flushed = collector.flush()
        assert len(flushed) == 1
        assert len(collector.spans) == 0
        trace_files = list((tmp_path / "traces").glob("trace-*.jsonl"))
        assert len(trace_files) == 1
        lines = trace_files[0].read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["span_id"] == "flush-1"
        assert data["success"] is True

    def test_flush_empty(self, tmp_path):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        flushed = collector.flush()
        assert flushed == []

    def test_flush_clears_spans(self, tmp_path):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        collector.add_span(
            TraceSpan(
                span_id="clear-1",
                operation="clear_op",
                start_time="2026-01-01T00:00:00+00:00",
                end_time="2026-01-01T00:00:01+00:00",
                duration_ms=200.0,
                success=True,
            )
        )
        collector.flush()
        assert len(collector.spans) == 0


class TestTraceDecorator:
    def setup_method(self):
        TraceCollector.reset_instance()

    def test_trace_success(self, tmp_path, monkeypatch):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        TraceCollector.set_instance(collector)

        @trace(operation="custom_op")
        def my_func(x, y):
            return x + y

        result = my_func(1, 2)
        assert result == 3
        assert len(collector.spans) == 1
        assert collector.spans[0].success is True
        assert collector.spans[0].operation == "custom_op"
        assert collector.spans[0].error == ""

    def test_trace_default_operation_name(self, tmp_path, monkeypatch):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        TraceCollector.set_instance(collector)

        @trace()
        def compute():
            return 42

        compute()
        assert collector.spans[0].operation == "compute"

    def test_trace_exception_recorded(self, tmp_path, monkeypatch):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        TraceCollector.set_instance(collector)

        @trace(operation="failing_op")
        def boom():
            raise RuntimeError("kaboom")

        with pytest.raises(RuntimeError, match="kaboom"):
            boom()
        assert len(collector.spans) == 1
        assert collector.spans[0].success is False
        assert "kaboom" in collector.spans[0].error

    def test_trace_preserves_return_value(self, tmp_path, monkeypatch):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        TraceCollector.set_instance(collector)

        @trace()
        def greet(name):
            return f"hello {name}"

        assert greet("world") == "hello world"

    def test_trace_duration_positive(self, tmp_path, monkeypatch):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        TraceCollector.set_instance(collector)

        @trace()
        def slow():
            return "done"

        slow()
        assert collector.spans[0].duration_ms >= 0

    def test_trace_no_args(self, tmp_path, monkeypatch):
        collector = TraceCollector()
        collector.output_dir = tmp_path / "traces"
        TraceCollector.set_instance(collector)

        @trace("static_name")
        def no_args():
            return True

        assert no_args() is True
        assert collector.spans[0].operation == "static_name"
