# [A_test] module_id: MOD-GOV_otel_instrumentation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_otel_instrumentation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_otel_instrumentation.py -q
# [TTL] task_bound
import time

from zephyr.infrastructure.system_telemetry.otel_instrumentation import OTelInstrumentation, PipelineTraceSpan


class TestPipelineTraceSpan:
    def test_default_values(self):
        span = PipelineTraceSpan(name="test", start_time=1.0)
        assert span.end_time == 0.0
        assert span.attributes == {}
        assert span.status == "OK"

    def test_custom_attributes(self):
        attrs = {"key": "value", "count": 42}
        span = PipelineTraceSpan(name="custom", start_time=1.0, attributes=attrs)
        assert span.attributes["key"] == "value"
        assert span.attributes["count"] == 42

    def test_explicit_end_time(self):
        span = PipelineTraceSpan(name="t", start_time=1.0, end_time=2.0)
        assert span.end_time == 2.0

    def test_explicit_status(self):
        span = PipelineTraceSpan(name="t", start_time=1.0, status="ERROR")
        assert span.status == "ERROR"


class TestOTelInstrumentationInstantiation:
    def test_create_instance(self):
        otel = OTelInstrumentation()
        assert otel is not None

    def test_initial_spans_empty(self):
        otel = OTelInstrumentation()
        assert otel._spans == []


class TestOTelInstrumentationStartSpan:
    def test_start_span_returns_span(self):
        otel = OTelInstrumentation()
        span = otel.start_span("operation")
        assert isinstance(span, PipelineTraceSpan)
        assert span.name == "operation"

    def test_start_span_records_start_time(self):
        otel = OTelInstrumentation()
        before = time.time()
        span = otel.start_span("op")
        after = time.time()
        assert before <= span.start_time <= after

    def test_start_span_default_end_time_zero(self):
        otel = OTelInstrumentation()
        span = otel.start_span("op")
        assert span.end_time == 0.0

    def test_start_span_with_attributes(self):
        otel = OTelInstrumentation()
        attrs = {"component": "ce", "version": 2}
        span = otel.start_span("op", attrs=attrs)
        assert span.attributes["component"] == "ce"
        assert span.attributes["version"] == 2

    def test_start_span_none_attrs_yields_empty_dict(self):
        otel = OTelInstrumentation()
        span = otel.start_span("op", attrs=None)
        assert span.attributes == {}

    def test_start_span_appends_to_internal_list(self):
        otel = OTelInstrumentation()
        otel.start_span("a")
        otel.start_span("b")
        assert len(otel._spans) == 2
        assert otel._spans[0].name == "a"
        assert otel._spans[1].name == "b"


class TestOTelInstrumentationEndSpan:
    def test_end_span_sets_end_time(self):
        otel = OTelInstrumentation()
        span = otel.start_span("op")
        assert span.end_time == 0.0
        time.sleep(0.01)
        otel.end_span(span)
        assert span.end_time > 0.0

    def test_end_time_after_start_time(self):
        otel = OTelInstrumentation()
        span = otel.start_span("op")
        time.sleep(0.01)
        otel.end_span(span)
        assert span.end_time >= span.start_time

    def test_end_span_preserves_status(self):
        otel = OTelInstrumentation()
        span = otel.start_span("op")
        otel.end_span(span)
        assert span.status == "OK"

    def test_multiple_spans_independent(self):
        otel = OTelInstrumentation()
        span_a = otel.start_span("a")
        span_b = otel.start_span("b")
        otel.end_span(span_a)
        assert span_a.end_time > 0.0
        assert span_b.end_time == 0.0
