# [A_test] module_id: SRC-TST-1530 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_scheduler_health
# [INVARIANTS] test_coverage>=2_public_methods;boundary_tests_included
# [MODIFY-GUARD] sync_with_source_on_refactor
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest_exit_0_on_pass
# [TESTS] tests/test_scheduler_health.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.scheduler_health import HealthReporter


class TestHealthReporter:
    def setup_method(self):
        self.reporter = HealthReporter()

    def test_construction(self):
        assert self.reporter.dogfood_monitor is not None
        assert self.reporter.bottleneck_detector is not None

    def test_report_returns_dict(self):
        result = self.reporter.report()
        assert isinstance(result, dict)

    def test_report_has_required_keys(self):
        result = self.reporter.report()
        expected_keys = [
            "dogfood",
            "bottleneck",
            "degradation",
            "throttle",
            "bus_factor",
            "e2e",
            "storage",
            "numerical",
            "hygiene",
            "L2_guard_consistency",
            "L2_guard_conflicts",
            "L2_guard_oscillation",
            "L3_cascade",
            "L3_mod_rate_limiter",
            "L3_entropy",
            "L4_diminishing_returns",
            "L4_complexity_budget",
            "cold_start",
            "context_pressure",
            "session_consistency",
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_report_has_20_keys(self):
        result = self.reporter.report()
        assert len(result) == 20

    def test_degradation_is_string(self):
        result = self.reporter.report()
        assert isinstance(result["degradation"], str)

    def test_cold_start_is_dict(self):
        result = self.reporter.report()
        assert isinstance(result["cold_start"], dict)

    def test_report_idempotent(self):
        r1 = self.reporter.report()
        r2 = self.reporter.report()
        assert set(r1.keys()) == set(r2.keys())
