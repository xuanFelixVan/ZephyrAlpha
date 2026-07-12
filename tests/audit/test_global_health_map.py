# [A_test] module_id: SRC-TST-1058 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_global_health_map
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.global_health_map
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_global_health_map.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.global_health_map import GlobalHealthMap


class TestGlobalHealthMapInstantiation:
    def test_default_empty_subsystems(self):
        m = GlobalHealthMap()
        assert m.subsystems == {}

    def test_custom_subsystems(self):
        m = GlobalHealthMap(subsystems={"db": 90.0, "api": 80.0})
        assert m.subsystems == {"db": 90.0, "api": 80.0}


class TestOverallHealth:
    def test_empty_subsystems_returns_100(self):
        m = GlobalHealthMap()
        assert m.overall_health() == 100.0

    def test_single_subsystem(self):
        m = GlobalHealthMap(subsystems={"db": 80.0})
        assert m.overall_health() == 80.0

    def test_multiple_subsystems_average(self):
        m = GlobalHealthMap(subsystems={"db": 90.0, "api": 70.0, "cache": 80.0})
        assert m.overall_health() == 80.0

    def test_all_healthy(self):
        m = GlobalHealthMap(subsystems={"a": 100.0, "b": 100.0})
        assert m.overall_health() == 100.0

    def test_all_zero(self):
        m = GlobalHealthMap(subsystems={"a": 0.0, "b": 0.0})
        assert m.overall_health() == 0.0

    def test_negative_health_value(self):
        m = GlobalHealthMap(subsystems={"a": -10.0})
        assert m.overall_health() == -10.0

    def test_health_above_100(self):
        m = GlobalHealthMap(subsystems={"a": 120.0})
        assert m.overall_health() == 120.0

    def test_mixed_health_values(self):
        m = GlobalHealthMap(subsystems={"a": 50.0, "b": 100.0})
        assert m.overall_health() == 75.0

    def test_single_subsystem_at_boundary(self):
        m = GlobalHealthMap(subsystems={"a": 0.0})
        assert m.overall_health() == 0.0

    def test_dynamic_subsystem_addition(self):
        m = GlobalHealthMap()
        m.subsystems["db"] = 90.0
        m.subsystems["api"] = 70.0
        assert m.overall_health() == 80.0
