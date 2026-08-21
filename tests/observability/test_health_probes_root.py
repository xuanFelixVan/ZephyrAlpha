# [A_test] module_id: MOD-GOV_health_probes_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] tests.test_health_probes
# [INVARIANTS] 11-system triple-state probes (knowledge_base 已随 KB 系统退役移除); ProbeStatus enum stability
# [MODIFY-GUARD] health_probes.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError→fail; RuntimeError→fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

hp = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.health_probes",
    reason="health_probes import failed",
)


class TestProbeStatus:
    def test_enum_values(self):
        assert hp.ProbeStatus.HEALTHY.value == "healthy"
        assert hp.ProbeStatus.DEGRADED.value == "degraded"
        assert hp.ProbeStatus.UNHEALTHY.value == "unhealthy"

    def test_string_enum(self):
        assert hp.ProbeStatus("healthy") == hp.ProbeStatus.HEALTHY


class TestLivenessProbe:
    def test_defaults(self):
        p = hp.LivenessProbe()
        assert p.status == "alive"
        assert p.pid == 0
        assert p.uptime_s == 0.0


class TestReadinessProbe:
    def test_defaults(self):
        p = hp.ReadinessProbe()
        assert p.status == "ready"
        assert isinstance(p.dependencies, dict)


class TestHealthzProbe:
    def test_defaults(self):
        p = hp.HealthzProbe()
        assert p.status == hp.ProbeStatus.HEALTHY
        assert p.degraded_details == ""


class TestHealthProbeManager:
    def test_instantiation(self):
        mgr = hp.HealthProbeManager()
        assert mgr is not None

    def test_liveness(self):
        mgr = hp.HealthProbeManager()
        result = mgr.liveness("orchestrator")
        assert result["status"] == "alive"
        assert result["system"] == "orchestrator"
        assert "uptime_s" in result

    def test_readiness_ok(self):
        mgr = hp.HealthProbeManager()
        result = mgr.readiness("database", deps_ok=True)
        assert result["status"] == "ready"

    def test_readiness_not_ok(self):
        mgr = hp.HealthProbeManager()
        result = mgr.readiness("database", deps_ok=False)
        assert result["status"] == "not_ready"

    def test_healthz_healthy(self):
        mgr = hp.HealthProbeManager()
        result = mgr.healthz("system-telemetry")
        assert result["status"] == "healthy"

    def test_healthz_degraded_orchestrator(self):
        mgr = hp.HealthProbeManager()
        result = mgr.healthz("orchestrator", metrics={"pending_queue": 200})
        assert result["status"] == "degraded"
        assert "pending_queue" in result["degraded_details"]

    def test_healthz_no_degraded_llm_security(self):
        mgr = hp.HealthProbeManager()
        result = mgr.healthz("llm-security", metrics={"some_metric": 999})
        assert result["status"] == "healthy"

    def test_list_systems(self):
        mgr = hp.HealthProbeManager()
        systems = mgr.list_systems()
        assert isinstance(systems, list)
        assert len(systems) == 11
        assert "orchestrator" in systems


class TestSystemsConstant:
    def test_systems_tuple(self):
        assert isinstance(hp.SYSTEMS, tuple)
        assert len(hp.SYSTEMS) == 11

    def test_special_rules(self):
        assert "orchestrator" in hp.SPECIAL_RULES
        assert "llm-security" in hp.SPECIAL_RULES
        assert hp.SPECIAL_RULES["llm-security"]["no_degraded"] is True


class TestBoundary:
    def test_liveness_unknown_system(self):
        mgr = hp.HealthProbeManager()
        result = mgr.liveness("nonexistent")
        assert result["status"] == "alive"

    def test_healthz_none_metrics(self):
        mgr = hp.HealthProbeManager()
        result = mgr.healthz("orchestrator", metrics=None)
        assert result["status"] == "healthy"

    def test_healthz_empty_metrics(self):
        mgr = hp.HealthProbeManager()
        result = mgr.healthz("orchestrator", metrics={})
        assert result["status"] == "healthy"

    def test_readiness_default_deps(self):
        mgr = hp.HealthProbeManager()
        result = mgr.readiness("database")
        assert result["status"] == "ready"
