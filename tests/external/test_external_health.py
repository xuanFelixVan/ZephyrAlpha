# [A_test] module_id: SRC-TST-0882 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_external_health
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_external_health.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.external_health import (
    DependencyHealth,
    DependencyStatus,
    ExternalHealth,
)


class TestDependencyStatus:
    def test_enum_values(self):
        assert DependencyStatus.HEALTHY.value == "HEALTHY"
        assert DependencyStatus.DEGRADED.value == "DEGRADED"
        assert DependencyStatus.DOWN.value == "DOWN"


class TestDependencyHealth:
    def test_default_instantiation(self):
        dep = DependencyHealth(service="api_gateway")
        assert dep.service == "api_gateway"
        assert dep.status == DependencyStatus.HEALTHY
        assert dep.consecutive_failures == 0
        assert dep.health_score == 100.0

    def test_is_dataclass(self):
        dep = DependencyHealth(service="test")
        assert hasattr(dep, "__dataclass_fields__")


class TestExternalHealthInstantiation:
    def test_default_instantiation(self):
        health = ExternalHealth()
        assert health.dependencies == {}

    def test_is_dataclass(self):
        health = ExternalHealth()
        assert hasattr(health, "__dataclass_fields__")


class TestRegister:
    def test_register_service(self):
        health = ExternalHealth()
        dep = health.register("api_gateway")
        assert "api_gateway" in health.dependencies
        assert dep.service == "api_gateway"

    def test_register_returns_dependency_health(self):
        health = ExternalHealth()
        dep = health.register("redis")
        assert isinstance(dep, DependencyHealth)

    def test_register_multiple_services(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.register("redis")
        assert len(health.dependencies) == 2


class TestReportSuccess:
    def test_success_sets_healthy(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.report_failure("api_gateway")
        health.report_success("api_gateway")
        dep = health.dependencies["api_gateway"]
        assert dep.status == DependencyStatus.HEALTHY

    def test_success_resets_consecutive_failures(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.report_failure("api_gateway")
        health.report_failure("api_gateway")
        health.report_success("api_gateway")
        assert health.dependencies["api_gateway"].consecutive_failures == 0

    def test_success_increases_health_score(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.report_failure("api_gateway")
        score_before = health.dependencies["api_gateway"].health_score
        health.report_success("api_gateway")
        assert health.dependencies["api_gateway"].health_score > score_before

    def test_success_caps_at_100(self):
        health = ExternalHealth()
        health.register("api_gateway")
        for _ in range(20):
            health.report_success("api_gateway")
        assert health.dependencies["api_gateway"].health_score <= 100.0

    def test_success_unknown_service_no_error(self):
        health = ExternalHealth()
        health.report_success("nonexistent")


class TestReportFailure:
    def test_failure_increments_consecutive(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.report_failure("api_gateway")
        assert health.dependencies["api_gateway"].consecutive_failures == 1

    def test_failure_decreases_health_score(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.report_failure("api_gateway")
        assert health.dependencies["api_gateway"].health_score < 100.0

    def test_three_failures_sets_down(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.report_failure("api_gateway")
        health.report_failure("api_gateway")
        health.report_failure("api_gateway")
        assert health.dependencies["api_gateway"].status == DependencyStatus.DOWN

    def test_failure_unknown_service_no_error(self):
        health = ExternalHealth()
        health.report_failure("nonexistent")

    def test_health_score_does_not_go_below_zero(self):
        health = ExternalHealth()
        health.register("api_gateway")
        for _ in range(10):
            health.report_failure("api_gateway")
        assert health.dependencies["api_gateway"].health_score >= 0.0


class TestSuppressInternalAlerts:
    def test_no_down_services(self):
        health = ExternalHealth()
        health.register("api_gateway")
        assert health.suppress_internal_alerts() == set()

    def test_down_service_suppressed(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.report_failure("api_gateway")
        health.report_failure("api_gateway")
        health.report_failure("api_gateway")
        suppressed = health.suppress_internal_alerts()
        assert "api_gateway" in suppressed

    def test_mixed_statuses(self):
        health = ExternalHealth()
        health.register("api_gateway")
        health.register("redis")
        health.report_failure("api_gateway")
        health.report_failure("api_gateway")
        health.report_failure("api_gateway")
        suppressed = health.suppress_internal_alerts()
        assert "api_gateway" in suppressed
        assert "redis" not in suppressed
