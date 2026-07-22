# [A_test] module_id: MOD-GOV_facade | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] tests.test_facade
# [INVARIANTS] test_mode=True silences all outbound; shutdown idempotent; no background threads in test mode
# [MODIFY-GUARD] facade.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError→fail; OSError→caught
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

facade = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.facade",
    reason="facade import failed",
)


class TestMetricsFacade:
    def test_instantiation(self):
        m = facade.MetricsFacade("test_mod", test_mode=True)
        assert m is not None

    def test_gauge(self):
        m = facade.MetricsFacade("test_mod", test_mode=True)
        result = m.gauge("latency_ms", 42.0)
        assert result["kind"] == "gauge"
        assert result["value"] == 42.0
        assert result["name"] == "latency_ms"

    def test_counter(self):
        m = facade.MetricsFacade("test_mod", test_mode=True)
        result = m.counter("requests", delta=3.0)
        assert result["kind"] == "counter"
        assert result["value"] == 3.0

    def test_histogram(self):
        m = facade.MetricsFacade("test_mod", test_mode=True)
        result = m.histogram("duration", 1.5)
        assert result["kind"] == "histogram"

    def test_summary(self):
        m = facade.MetricsFacade("test_mod", test_mode=True)
        result = m.summary("queue_depth", 10.0)
        assert result["kind"] == "summary"


class TestLogsFacade:
    def test_instantiation(self):
        l = facade.LogsFacade("test_mod", test_mode=True)
        assert l is not None

    def test_info(self):
        l = facade.LogsFacade("test_mod", test_mode=True)
        result = l.info("step_start", step=1)
        assert result["level"] == "INFO"
        assert result["message"] == "step_start"

    def test_warning(self):
        l = facade.LogsFacade("test_mod", test_mode=True)
        result = l.warning("slow_query", duration_ms=500)
        assert result["level"] == "WARNING"

    def test_error(self):
        l = facade.LogsFacade("test_mod", test_mode=True)
        result = l.error("connection_lost", host="db1")
        assert result["level"] == "ERROR"


class TestTracesFacade:
    def test_instantiation(self):
        t = facade.TracesFacade("test_mod", test_mode=True)
        assert t is not None

    def test_span_context_manager(self):
        t = facade.TracesFacade("test_mod", test_mode=True)
        span = t.span("pipeline:run")
        with span as s:
            s.set_attribute("key", "value")
        result = s.end()
        assert result["operation"] == "pipeline:run"
        assert "key" in result["attributes"]


class TestAIBehaviorFacade:
    def test_instantiation(self):
        a = facade.AIBehaviorFacade("test_mod", test_mode=True)
        assert a is not None

    def test_record(self):
        a = facade.AIBehaviorFacade("test_mod", test_mode=True)
        result = a.record(decision="task_assign", model="gpt-4.1", reason="best fit")
        assert result["decision"] == "task_assign"
        assert result["model"] == "gpt-4.1"


class TestArchiveFacade:
    def test_instantiation(self):
        a = facade.ArchiveFacade("test_mod", test_mode=True)
        assert a is not None

    def test_next_batch_id(self):
        a = facade.ArchiveFacade("test_mod", test_mode=True)
        batch_id = a.next_batch_id(prefix="arc")
        assert batch_id.startswith("arc-")


class TestTelemetry:
    def test_instantiation_test_mode(self):
        t = facade.Telemetry("test_mod", environment="test", test_mode=True)
        assert t.module_id == "test_mod"
        assert t.test_mode is True

    def test_has_all_subsystems(self):
        t = facade.Telemetry("test_mod", test_mode=True)
        assert hasattr(t, "metrics")
        assert hasattr(t, "logs")
        assert hasattr(t, "traces")
        assert hasattr(t, "ai_behavior")
        assert hasattr(t, "health")
        assert hasattr(t, "profiles")
        assert hasattr(t, "alerts")
        assert hasattr(t, "schema")
        assert hasattr(t, "archive")

    def test_shutdown_idempotent(self):
        t = facade.Telemetry("test_mod", test_mode=True)
        t.shutdown()
        t.shutdown()
        assert t._shutdown_called is True

    def test_metrics_gauge_through_telemetry(self):
        t = facade.Telemetry("test_mod", test_mode=True)
        result = t.metrics.gauge("latency", 10.0)
        assert result["value"] == 10.0


class TestBoundary:
    def test_metrics_empty_name(self):
        m = facade.MetricsFacade("test_mod", test_mode=True)
        result = m.gauge("", 0.0)
        assert result["name"] == ""

    def test_logs_empty_message(self):
        l = facade.LogsFacade("test_mod", test_mode=True)
        result = l.info("")
        assert result["message"] == ""

    def test_ai_behavior_no_args(self):
        a = facade.AIBehaviorFacade("test_mod", test_mode=True)
        result = a.record(decision="")
        assert result["decision"] == ""
