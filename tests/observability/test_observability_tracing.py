# [A_test] module_id: MOD-GOV_observability_tracing | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_observability_tracing

# [INVARIANTS] start_span无OTEL时返回NoopSpan;traced装饰器保留__name__;_NoopSpan所有方法空操作

# [MODIFY-GUARD] tracing.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_observability_tracing.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.observability.tracing import (
    _check_otel,
    _NoopSpan,
    start_span,
    traced,
)
from zephyr.shared.utils.logging import trace_id_var


@pytest.fixture(autouse=True)
def _clear_trace():
    trace_id_var.set("")
    yield
    trace_id_var.set("")


class TestNoopSpan:
    def test_set_attribute_noop(self):
        span = _NoopSpan("test", "trace-1")
        span.set_attribute("key", "val")

    def test_set_status_noop(self):
        span = _NoopSpan("test", "trace-1")
        span.set_status("ERROR")

    def test_end_noop(self):
        span = _NoopSpan("test", "trace-1")
        span.end()

    def test_name_attribute(self):
        span = _NoopSpan("my_span", "trace-1")
        assert span.name == "my_span"


class TestStartSpan:
    def test_no_trace_id_yields_noop(self):
        trace_id_var.set("")
        with start_span("test_span") as span:
            assert isinstance(span, _NoopSpan)

    def test_with_trace_id_yields_span(self):
        trace_id_var.set("trace-abc-123")
        with start_span("test_span") as span:
            assert span is not None

    def test_with_attributes(self):
        trace_id_var.set("trace-123")
        with start_span("attr_span", attributes={"key": "val"}) as span:
            pass

    def test_exception_in_span(self):
        trace_id_var.set("trace-123")
        with pytest.raises(ValueError), start_span("fail_span") as span:
            raise ValueError("test error")


class TestTracedDecorator:
    def test_preserves_function_name(self):
        @traced("my_op")
        def my_function():
            return 42

        assert my_function.__name__ == "my_function"

    def test_function_still_works(self):
        @traced("my_op")
        def add(a, b):
            return a + b

        assert add(3, 4) == 7

    def test_default_span_name(self):
        @traced()
        def my_func():
            return 1

        assert my_func() == 1


class TestCheckOtel:
    def test_returns_bool(self):
        result = _check_otel()
        assert isinstance(result, bool)
