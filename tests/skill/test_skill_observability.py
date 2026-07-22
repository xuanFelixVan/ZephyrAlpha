# [A_test] module_id: MOD-GOV_skill_observability | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_observability
# [INVARIANTS] Trace/Span/Metric data stored in class-level dicts; clear_all resets state
# [MODIFY-GUARD] changes require review of skill_observability.py API
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns error dict for unknown trace_id; never raises
# [TESTS] pytest tests/test_skill_observability.py -q
# [TTL] task_bound


import pytest

from zephyr.autonomy_core.skills.skill_observability import SkillObservability, Span, Trace


@pytest.fixture(autouse=True)
def clean_state():
    SkillObservability.clear_all()
    yield
    SkillObservability.clear_all()


class TestSpanInstantiation:
    def test_default_values(self):
        span = Span(name="test-span")
        assert span.name == "test-span"
        assert span.start_ms == 0
        assert span.end_ms == 0
        assert span.metadata == {}

    def test_custom_values(self):
        span = Span(name="s", start_ms=100, end_ms=200, metadata={"k": "v"})
        assert span.start_ms == 100
        assert span.end_ms == 200
        assert span.metadata["k"] == "v"

    def test_to_dict(self):
        span = Span(name="s", start_ms=100, end_ms=250, metadata={"x": 1})
        d = span.to_dict()
        assert d["name"] == "s"
        assert d["duration_ms"] == 150
        assert d["metadata"] == {"x": 1}

    def test_to_dict_no_end(self):
        span = Span(name="s", start_ms=100)
        d = span.to_dict()
        assert d["duration_ms"] == 0


class TestTraceInstantiation:
    def test_default_values(self):
        trace = Trace(trace_id="t1", skill_id="SKILL-DOM-TS-001")
        assert trace.trace_id == "t1"
        assert trace.skill_id == "SKILL-DOM-TS-001"
        assert trace.spans == []
        assert trace.status == "running"
        assert trace.end_ms == 0

    def test_custom_values(self):
        trace = Trace(trace_id="t2", skill_id="SKILL-DOM-TS-002", start_ms=1000, status="completed")
        assert trace.start_ms == 1000
        assert trace.status == "completed"

    def test_to_dict(self):
        trace = Trace(trace_id="t3", skill_id="SKILL-DOM-TS-003", start_ms=100, end_ms=500)
        d = trace.to_dict()
        assert d["trace_id"] == "t3"
        assert d["duration_ms"] == 400
        assert d["status"] == "running"

    def test_to_dict_with_spans(self):
        span = Span(name="sp1", start_ms=100, end_ms=200)
        trace = Trace(trace_id="t4", skill_id="SKILL-DOM-TS-004", spans=[span])
        d = trace.to_dict()
        assert len(d["spans"]) == 1
        assert d["spans"][0]["name"] == "sp1"


class TestSkillObservabilityStartTrace:
    def test_start_trace_returns_dict(self):
        result = SkillObservability.start_trace("SKILL-DOM-TS-001")
        assert "trace_id" in result
        assert result["skill_id"] == "SKILL-DOM-TS-001"
        assert result["status"] == "started"

    def test_start_trace_stores_trace(self):
        result = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = result["trace_id"]
        stored = SkillObservability.get_trace(trace_id)
        assert stored is not None
        assert stored["skill_id"] == "SKILL-DOM-TS-001"

    def test_start_trace_unique_ids_for_different_skills(self):
        r1 = SkillObservability.start_trace("SKILL-DOM-TS-001")
        r2 = SkillObservability.start_trace("SKILL-DOM-TS-002")
        assert r1["trace_id"] != r2["trace_id"]


class TestSkillObservabilityAddSpan:
    def test_add_span_success(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        result = SkillObservability.add_span(trace_id, "load_l1")
        assert result["status"] == "span_added"
        assert result["span_name"] == "load_l1"

    def test_add_span_with_metadata(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        result = SkillObservability.add_span(trace_id, "load_l2", metadata={"tokens": 50})
        assert result["status"] == "span_added"

    def test_add_span_unknown_trace(self):
        result = SkillObservability.add_span("nonexistent-trace", "span1")
        assert "error" in result

    def test_add_span_none_metadata(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        result = SkillObservability.add_span(trace_id, "span1", metadata=None)
        assert result["status"] == "span_added"


class TestSkillObservabilityEndSpan:
    def test_end_span_success(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        SkillObservability.add_span(trace_id, "load_l1")
        result = SkillObservability.end_span(trace_id, "load_l1")
        assert result["status"] == "span_ended"

    def test_end_span_unknown_trace(self):
        result = SkillObservability.end_span("nonexistent", "span1")
        assert "error" in result

    def test_end_span_not_running(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        SkillObservability.add_span(trace_id, "sp1")
        SkillObservability.end_span(trace_id, "sp1")
        result = SkillObservability.end_span(trace_id, "sp1")
        assert "error" in result


class TestSkillObservabilityEndTrace:
    def test_end_trace_completed(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        result = SkillObservability.end_trace(trace_id, status="completed")
        assert result["status"] == "completed"
        assert result["duration_ms"] >= 0

    def test_end_trace_failed(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        result = SkillObservability.end_trace(trace_id, status="failed")
        assert result["status"] == "failed"

    def test_end_trace_closes_open_spans(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        SkillObservability.add_span(trace_id, "open_span")
        result = SkillObservability.end_trace(trace_id)
        trace_data = SkillObservability.get_trace(trace_id)
        for span_dict in trace_data["spans"]:
            assert span_dict["duration_ms"] >= 0

    def test_end_trace_unknown(self):
        result = SkillObservability.end_trace("nonexistent")
        assert "error" in result

    def test_end_trace_returns_dict_with_status(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        result = SkillObservability.end_trace(trace_id)
        assert "status" in result
        assert "duration_ms" in result
        assert result["duration_ms"] >= 0


class TestSkillObservabilityGetTrace:
    def test_existing_trace(self):
        r = SkillObservability.start_trace("SKILL-DOM-TS-001")
        trace_id = r["trace_id"]
        result = SkillObservability.get_trace(trace_id)
        assert result is not None
        assert result["trace_id"] == trace_id

    def test_nonexistent_trace(self):
        result = SkillObservability.get_trace("nonexistent")
        assert result is None


class TestSkillObservabilityRecordMetric:
    def test_record_metric_returns_entry(self):
        result = SkillObservability.record_metric("SKILL-DOM-TS-001", "latency_ms", 42.5)
        assert result["skill_id"] == "SKILL-DOM-TS-001"
        assert result["metric"] == "latency_ms"
        assert result["value"] == 42.5

    def test_record_metric_with_tags(self):
        result = SkillObservability.record_metric("SKILL-DOM-TS-001", "tokens", 100, tags={"tier": "L1"})
        assert result["tags"]["tier"] == "L1"

    def test_record_metric_none_tags(self):
        result = SkillObservability.record_metric("SKILL-DOM-TS-001", "tokens", 100, tags=None)
        assert result["tags"] == {}

    def test_record_metric_max_events(self):
        for i in range(510):
            SkillObservability.record_metric("SKILL-DOM-TS-001", "m", float(i))
        metrics = SkillObservability.get_metrics("SKILL-DOM-TS-001")
        assert len(metrics) <= 500


class TestSkillObservabilityGetMetrics:
    def test_get_metrics_by_skill(self):
        SkillObservability.record_metric("SKILL-A", "latency", 10.0)
        SkillObservability.record_metric("SKILL-B", "latency", 20.0)
        result = SkillObservability.get_metrics("SKILL-A")
        assert all(m["skill_id"] == "SKILL-A" for m in result)

    def test_get_metrics_all_skills(self):
        SkillObservability.record_metric("SKILL-A", "latency", 10.0)
        SkillObservability.record_metric("SKILL-B", "latency", 20.0)
        result = SkillObservability.get_metrics()
        assert len(result) == 2

    def test_get_metrics_filter_by_name(self):
        SkillObservability.record_metric("SKILL-A", "latency", 10.0)
        SkillObservability.record_metric("SKILL-A", "tokens", 50.0)
        result = SkillObservability.get_metrics("SKILL-A", metric_name="latency")
        assert all(m["metric"] == "latency" for m in result)

    def test_get_metrics_limit(self):
        for i in range(10):
            SkillObservability.record_metric("SKILL-A", "m", float(i))
        result = SkillObservability.get_metrics("SKILL-A", limit=5)
        assert len(result) == 5

    def test_get_metrics_nonexistent_skill(self):
        result = SkillObservability.get_metrics("NONEXISTENT")
        assert result == []


class TestSkillObservabilityLogEvent:
    def test_log_event_returns_dict(self):
        result = SkillObservability.log_event("SKILL-DOM-TS-001", "activated")
        assert result["skill_id"] == "SKILL-DOM-TS-001"
        assert result["event_type"] == "activated"
        assert "timestamp" in result

    def test_log_event_with_detail(self):
        result = SkillObservability.log_event("SKILL-DOM-TS-001", "error", detail={"msg": "timeout"})
        assert result["detail"]["msg"] == "timeout"

    def test_log_event_none_detail(self):
        result = SkillObservability.log_event("SKILL-DOM-TS-001", "activated", detail=None)
        assert result["detail"] == {}


class TestSkillObservabilityHealthSummary:
    def test_empty_summary(self):
        summary = SkillObservability.health_summary()
        assert summary["active_traces"] == 0
        assert summary["skills_with_metrics"] == 0
        assert summary["total_metric_entries"] == 0

    def test_summary_with_data(self):
        SkillObservability.start_trace("SKILL-A")
        SkillObservability.record_metric("SKILL-A", "latency", 10.0)
        SkillObservability.record_metric("SKILL-B", "latency", 20.0)
        summary = SkillObservability.health_summary()
        assert summary["active_traces"] == 1
        assert summary["skills_with_metrics"] == 2
        assert summary["total_metric_entries"] == 2


class TestSkillObservabilityClearAll:
    def test_clear_all_resets_traces(self):
        SkillObservability.start_trace("SKILL-A")
        SkillObservability.clear_all()
        assert SkillObservability.health_summary()["active_traces"] == 0

    def test_clear_all_resets_metrics(self):
        SkillObservability.record_metric("SKILL-A", "latency", 10.0)
        SkillObservability.clear_all()
        assert SkillObservability.health_summary()["total_metric_entries"] == 0
