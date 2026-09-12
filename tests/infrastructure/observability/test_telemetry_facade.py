# [A_test] module_id: MOD-GOV_telemetry_facade | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-695 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_telemetry_facade
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""system-telemetry 单元测试 — Telemetry 门面 + 9 子系统（MOD-INF-015 v0.9.0）"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestImport:
    def test_import_telemetry(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        assert Telemetry is not None

    def test_import_contract_metrics(self):
        from zephyr.infrastructure.system_telemetry import ContractMetricsCollector

        assert ContractMetricsCollector is not None


class TestInit:
    def test_default_init(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("m1")
        assert t.module_id == "m1"
        assert t.environment == "dev"
        assert t.test_mode is False

    def test_test_mode_init(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("m2", test_mode=True)
        assert t.module_id == "m2"
        assert t.test_mode is True

    def test_all_subsystems_exist(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("sub_check", test_mode=True)
        for attr in ["metrics", "logs", "traces", "ai_behavior", "health", "profiles", "alerts", "schema", "archive"]:
            assert hasattr(t, attr), f"Missing subsystem: {attr}"

    def test_shutdown_idempotent(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("shutdown_test", test_mode=True)
        t.shutdown()
        t.shutdown()


class TestMetrics:
    def test_gauge_returns_dict(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mm", test_mode=True)
        r = t.metrics.gauge("latency_ms", 42.0, host="srv1")
        assert r["kind"] == "gauge"
        assert r["name"] == "latency_ms"
        assert r["value"] == 42.0
        assert r["tags"] == {"host": "srv1"}

    def test_counter_default_delta(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mc", test_mode=True)
        r = t.metrics.counter("requests")
        assert r["kind"] == "counter"
        assert r["value"] == 1.0

    def test_histogram(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mh", test_mode=True)
        r = t.metrics.histogram("response_time", 0.35)
        assert r["kind"] == "histogram"

    def test_summary(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("ms", test_mode=True)
        r = t.metrics.summary("total_revenue", 10000.0)
        assert r["kind"] == "summary"


class TestLogs:
    def test_info_with_labels(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("ml", test_mode=True)
        r = t.logs.info("step_start", step=1, pipeline="alpha")
        assert r["level"] == "INFO"
        assert r["message"] == "step_start"
        assert r["labels"] == {"step": 1, "pipeline": "alpha"}

    def test_warning(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("ml", test_mode=True)
        r = t.logs.warning("threshold_near")
        assert r["level"] == "WARNING"

    def test_error(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("ml", test_mode=True)
        r = t.logs.error("auth_failed", error_code=403)
        assert r["level"] == "ERROR"


class TestTraces:
    def test_span_attributes_and_end(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mt", test_mode=True)
        span = t.traces.span("pipeline:run")
        span.set_attribute("step", "init")
        span.set_attribute("batch_id", "b001")
        result = span.end()
        assert result["operation"] == "pipeline:run"
        assert result["attributes"] == {"step": "init", "batch_id": "b001"}


class TestAIBehavior:
    def test_record_decision(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("ma", test_mode=True)
        r = t.ai_behavior.record(
            decision="task_assign",
            model="gpt-4.1",
            reason="default_routing",
            priority="P1",
        )
        assert r["decision"] == "task_assign"
        assert r["model"] == "gpt-4.1"
        assert r["reason"] == "default_routing"
        assert r["extra"] == {"priority": "P1"}


class TestHealth:
    def test_register_returns_status(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mh2", test_mode=True)
        s = t.health.register()
        assert s["module_id"] == "mh2"
        assert s["status"] in ("HEALTHY", "DEGRADED", "DOWN")

    def test_set_unhealthy(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mh3", test_mode=True)
        t.health.set_unhealthy("connection_lost")
        assert "connection_lost" in t.health.status()["reason"]


class TestProfiles:
    def test_start_stop(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mp", test_mode=True)
        t.profiles.start("loop")
        r = t.profiles.stop()
        assert r["module_id"] == "mp"

    def test_snapshot(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mp2", test_mode=True)
        r = t.profiles.snapshot()
        assert "cpu_percent" in r


class TestAlerts:
    def test_fire_alert(self):
        from zephyr.infrastructure.system_telemetry import Telemetry
        from zephyr.infrastructure.system_telemetry.alerts import AlertLevel

        t = Telemetry("mal", test_mode=True)
        r = t.alerts.fire(AlertLevel.CRITICAL, "circuit_breaker_tripped", labels={"gate": "G7"})
        assert r["level"] == "CRITICAL"
        assert r["message"] == "circuit_breaker_tripped"
        assert r["fired"] is False

    def test_alert_health(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mal2", test_mode=True)
        r = t.alerts.health()
        assert r["pending_alerts"] == 0


class TestSchema:
    @staticmethod
    def _ssot_version() -> str:
        """版本号真源=config/metrics_schema.yaml（禁止测试硬编码版本号）。"""
        import yaml

        from zephyr.shared.io.paths import REPO_ROOT

        data = yaml.safe_load((REPO_ROOT / "config" / "metrics_schema.yaml").read_text(encoding="utf-8"))
        return str(data["version"])

    def test_get_version(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("msc", test_mode=True)
        v = t.schema.get_version()
        assert v == self._ssot_version()

    def test_compatibility_same(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("msc", test_mode=True)
        assert t.schema.check_compatibility(self._ssot_version()) is True

    def test_compatibility_different(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("msc", test_mode=True)
        assert t.schema.check_compatibility("0.8.0") is False


class TestArchive:
    def test_batch_id_prefix(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mar", test_mode=True)
        bid = t.archive.next_batch_id()
        assert bid.startswith("arc-")

    def test_batch_id_custom_prefix(self):
        from zephyr.infrastructure.system_telemetry import Telemetry

        t = Telemetry("mar", test_mode=True)
        bid = t.archive.next_batch_id("zarc")
        assert bid.startswith("zarc-")


class TestPhaseCheckIntegration:
    @pytest.mark.xfail(
        strict=False,
        reason=(
            "真 bug（跨域登记不代修）：phase_check_registry.check_observability_baseline "
            "锚定已迁移旧路径 src/zephyr/system-telemetry（现位于 "
            "src/zephyr/infrastructure/system_telemetry），恒返回 YELLOW。"
            "治理域修复后本测试应恢复 GREEN（AI-TD2-DATA-001 留置，统筹配号 #ARCH-113）"
        ),
    )
    def test_gate_observability_baseline_green(self):
        from zephyr.governance.ops_governance.phase_check_registry import GateResult, check_observability_baseline

        result = check_observability_baseline()
        assert result == GateResult.GREEN, f"Expected GREEN, got {result}"
