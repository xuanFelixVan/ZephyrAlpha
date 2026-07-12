# [A_test] module_id: SRC-TST-1076 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_graceful_degradation_planner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.graceful_degradation_planner
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_graceful_degradation_planner.py
# [TTL] task_bound


from zephyr.feedback_loop.resilience.graceful_degradation_planner import (
    DegradationLevel,
    DegradationTier,
    GracefulDegradationPlanner,
)


class TestGracefulDegradationPlannerInstantiation:
    def test_default_instantiation(self):
        gdp = GracefulDegradationPlanner()
        assert gdp.cpu_threshold_pct == 85.0
        assert gdp.memory_threshold_pct == 85.0
        assert gdp.cooldown_seconds == 300.0
        assert gdp.current_level == DegradationLevel.FULL
        assert gdp.services == {}

    def test_custom_instantiation(self):
        gdp = GracefulDegradationPlanner(cpu_threshold_pct=70.0, memory_threshold_pct=75.0)
        assert gdp.cpu_threshold_pct == 70.0
        assert gdp.memory_threshold_pct == 75.0


class TestRegisterService:
    def test_register_service(self):
        gdp = GracefulDegradationPlanner()
        gdp.register_service("detector", DegradationTier.P0_CRITICAL, 1.0)
        assert "detector" in gdp.services
        assert gdp.services["detector"]["tier"] == DegradationTier.P0_CRITICAL
        assert gdp.services["detector"]["active"] is True
        assert gdp.services["detector"]["base_frequency_hz"] == 1.0

    def test_register_multiple_services(self):
        gdp = GracefulDegradationPlanner()
        gdp.register_service("core", DegradationTier.P0_CRITICAL, 1.0)
        gdp.register_service("archive", DegradationTier.P3_COSMETIC, 0.1)
        assert len(gdp.services) == 2


class TestEvaluateDegradation:
    def test_normal_load_stays_full(self):
        gdp = GracefulDegradationPlanner()
        gdp.register_service("core", DegradationTier.P0_CRITICAL, 1.0)
        result = gdp.evaluate_degradation(50.0, 50.0)
        assert result["level"] == DegradationLevel.FULL.value

    def test_high_load_triggers_degradation(self):
        gdp = GracefulDegradationPlanner(cooldown_seconds=0)
        gdp.register_service("core", DegradationTier.P0_CRITICAL, 1.0)
        gdp.register_service("archive", DegradationTier.P3_COSMETIC, 0.1)
        result = gdp.evaluate_degradation(90.0, 90.0)
        assert result["level"] in [
            DegradationLevel.REDUCED.value,
            DegradationLevel.MINIMAL.value,
            DegradationLevel.OBSERVE_ONLY.value,
        ]


class TestForceDegradation:
    def test_force_to_minimal(self):
        gdp = GracefulDegradationPlanner()
        gdp.register_service("core", DegradationTier.P0_CRITICAL, 1.0)
        gdp.register_service("archive", DegradationTier.P3_COSMETIC, 0.1)
        gdp.force_degradation(DegradationLevel.MINIMAL)
        assert gdp.current_level == DegradationLevel.MINIMAL
        assert gdp.services["archive"]["active"] is True
        assert gdp.services["core"]["active"] is False

    def test_force_to_observe_only(self):
        gdp = GracefulDegradationPlanner()
        gdp.register_service("core", DegradationTier.P0_CRITICAL, 1.0)
        gdp.register_service("diag", DegradationTier.P1_IMPORTANT, 0.5)
        gdp.force_degradation(DegradationLevel.OBSERVE_ONLY)
        assert gdp.current_level == DegradationLevel.OBSERVE_ONLY
        assert gdp.services["diag"]["active"] is True
        assert gdp.services["diag"]["current_frequency_hz"] == 0.25


class TestGetServiceStatus:
    def test_service_status_reflects_degradation(self):
        gdp = GracefulDegradationPlanner()
        gdp.register_service("core", DegradationTier.P0_CRITICAL, 1.0)
        gdp.register_service("fluff", DegradationTier.P3_COSMETIC, 0.1)
        gdp.force_degradation(DegradationLevel.REDUCED)
        status = gdp.get_service_status()
        assert status["fluff"]["active"] is True
        assert status["core"]["active"] is False
