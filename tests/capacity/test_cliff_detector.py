# [A_test] module_id: SRC-TST-0527 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_cliff_detector
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_cliff_detector.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip("zephyr.trading.feedback_loop.capacity_assurance.cliff_detector", reason="cliff_detector not available")
CliffDetector = mod.CliffDetector


class TestCliffDetector:
    def test_instantiation(self):
        cd = CliffDetector()
        assert cd.get_count() == 0
        assert cd.get_remaining() == 1500

    def test_register_healthy(self):
        cd = CliffDetector()
        result = cd.register("module_1")
        assert result["level"] == "HEALTHY"
        assert result["current_count"] == 1
        assert result["remaining"] == 1499
        assert result["suggestion"] == ""

    def test_register_multiple(self):
        cd = CliffDetector()
        for i in range(5):
            cd.register(f"module_{i}")
        assert cd.get_count() == 5

    def test_warning_threshold(self):
        cd = CliffDetector()
        for i in range(800):
            cd.register(f"mod_{i}")
        result = cd.register("mod_800")
        assert result["level"] == "WARNING"
        assert "Consider module optimization" in result["suggestion"]

    def test_critical_threshold(self):
        cd = CliffDetector()
        for i in range(1200):
            cd.register(f"mod_{i}")
        result = cd.register("mod_1200")
        assert result["level"] == "CRITICAL"

    def test_get_remaining(self):
        cd = CliffDetector()
        cd.register("mod_1")
        assert cd.get_remaining() == 1499

    def test_constants(self):
        assert CliffDetector.TOTAL_LIMIT == 1500
        assert CliffDetector.WARNING_THRESHOLD == 800
        assert CliffDetector.CRITICAL_THRESHOLD == 1200
