# [A_test] module_id: SRC-TST-0787 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_e2e_integration_health
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.e2e_integration_health
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_e2e_integration_health.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.e2e_integration_health import (
    E2EIntegrationHealth,
    IntegrationHealth,
)


class TestIntegrationHealthEnum:
    def test_healthy_value(self):
        assert IntegrationHealth.HEALTHY.value == "HEALTHY"

    def test_degraded_value(self):
        assert IntegrationHealth.DEGRADED.value == "DEGRADED"

    def test_broken_value(self):
        assert IntegrationHealth.BROKEN.value == "BROKEN"

    def test_unknown_value(self):
        assert IntegrationHealth.UNKNOWN.value == "UNKNOWN"

    def test_all_values_count(self):
        assert len(IntegrationHealth) == 4


class TestE2EIntegrationHealthInstantiation:
    def test_default_params(self):
        mon = E2EIntegrationHealth()
        assert mon.max_integration_latency_ms == 10000.0
        assert mon.max_integration_error_rate == 0.05
        assert mon.min_sample_count == 10
        assert mon.integrations == {}
        assert mon.health_history == []

    def test_custom_params(self):
        mon = E2EIntegrationHealth(
            max_integration_latency_ms=5000.0,
            max_integration_error_rate=0.01,
            min_sample_count=5,
        )
        assert mon.max_integration_latency_ms == 5000.0
        assert mon.min_sample_count == 5


class TestRegisterIntegration:
    def test_register_creates_entry(self):
        mon = E2EIntegrationHealth()
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        assert "svc-a-to-b" in mon.integrations

    def test_register_sets_sla_values(self):
        mon = E2EIntegrationHealth()
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        integ = mon.integrations["svc-a-to-b"]
        assert integ["sla_latency_ms"] == 500.0
        assert integ["sla_error_rate"] == 0.01
        assert integ["source"] == "svc-a"
        assert integ["target"] == "svc-b"

    def test_register_initializes_counters(self):
        mon = E2EIntegrationHealth()
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        integ = mon.integrations["svc-a-to-b"]
        assert integ["success_count"] == 0
        assert integ["failure_count"] == 0
        assert integ["total_samples"] == 0
        assert integ["latency_samples"] == []


class TestRecordCall:
    def test_record_success(self):
        mon = E2EIntegrationHealth()
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        mon.record_call("svc-a-to-b", 100.0, success=True)
        assert mon.integrations["svc-a-to-b"]["success_count"] == 1
        assert mon.integrations["svc-a-to-b"]["total_samples"] == 1

    def test_record_failure(self):
        mon = E2EIntegrationHealth()
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        mon.record_call("svc-a-to-b", 100.0, success=False)
        assert mon.integrations["svc-a-to-b"]["failure_count"] == 1
        assert mon.integrations["svc-a-to-b"]["total_samples"] == 1

    def test_record_unregistered_integration_ignored(self):
        mon = E2EIntegrationHealth()
        mon.record_call("nonexistent", 100.0, success=True)
        assert len(mon.integrations) == 0

    def test_latency_samples_capped_at_200(self):
        mon = E2EIntegrationHealth()
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        for i in range(250):
            mon.record_call("svc-a-to-b", float(i), success=True)
        assert len(mon.integrations["svc-a-to-b"]["latency_samples"]) == 200


class TestCheckIntegrationHealth:
    def test_unregistered_returns_unknown(self):
        mon = E2EIntegrationHealth()
        result = mon.check_integration_health("nonexistent")
        assert result["health"] == IntegrationHealth.UNKNOWN.value
        assert result["reason"] == "not_registered"

    def test_insufficient_samples_returns_unknown(self):
        mon = E2EIntegrationHealth(min_sample_count=10)
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        for _ in range(5):
            mon.record_call("svc-a-to-b", 100.0, success=True)
        result = mon.check_integration_health("svc-a-to-b")
        assert result["health"] == IntegrationHealth.UNKNOWN.value

    def test_healthy_integration(self):
        mon = E2EIntegrationHealth(min_sample_count=5)
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        for _ in range(10):
            mon.record_call("svc-a-to-b", 100.0, success=True)
        result = mon.check_integration_health("svc-a-to-b")
        assert result["health"] == IntegrationHealth.HEALTHY.value

    def test_degraded_integration_latency(self):
        mon = E2EIntegrationHealth(min_sample_count=5)
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 200.0, 0.5)
        for _ in range(10):
            mon.record_call("svc-a-to-b", 500.0, success=True)
        result = mon.check_integration_health("svc-a-to-b")
        assert result["health"] in (IntegrationHealth.DEGRADED.value, IntegrationHealth.BROKEN.value)


class TestCheckAllIntegrations:
    def test_empty_integrations(self):
        mon = E2EIntegrationHealth()
        result = mon.check_all_integrations()
        assert result["overall_health"] == IntegrationHealth.HEALTHY.value
        assert result["broken_integrations"] == 0

    def test_records_health_history(self):
        mon = E2EIntegrationHealth(min_sample_count=2)
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 500.0, 0.01)
        for _ in range(5):
            mon.record_call("svc-a-to-b", 100.0, success=True)
        mon.check_all_integrations()
        assert len(mon.health_history) == 1


class TestOverallIntegrationScore:
    def test_empty_returns_one(self):
        mon = E2EIntegrationHealth()
        assert mon.overall_integration_score() == 1.0

    def test_all_healthy(self):
        mon = E2EIntegrationHealth(min_sample_count=2)
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 5000.0, 0.5)
        for _ in range(5):
            mon.record_call("svc-a-to-b", 100.0, success=True)
        assert mon.overall_integration_score() == 1.0

    def test_score_between_zero_and_one(self):
        mon = E2EIntegrationHealth(min_sample_count=2)
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 5000.0, 0.5)
        for _ in range(5):
            mon.record_call("svc-a-to-b", 100.0, success=True)
        score = mon.overall_integration_score()
        assert 0.0 <= score <= 1.0


class TestGetDegradationTrend:
    def test_insufficient_history(self):
        mon = E2EIntegrationHealth()
        result = mon.get_degradation_trend()
        assert result["trend"] == "stable"
        assert result["reason"] == "insufficient_history"

    def test_single_check_is_stable(self):
        mon = E2EIntegrationHealth(min_sample_count=2)
        mon.register_integration("svc-a-to-b", "svc-a", "svc-b", 5000.0, 0.5)
        for _ in range(5):
            mon.record_call("svc-a-to-b", 100.0, success=True)
        mon.check_all_integrations()
        result = mon.get_degradation_trend()
        assert result["trend"] == "stable"
