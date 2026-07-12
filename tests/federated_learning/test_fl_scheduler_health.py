# [A_test] module_id: SRC-TST-1001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_scheduler_health
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.scheduler_health
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_scheduler_health.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.scheduler_health import HealthReporter


class TestHealthReporterInstantiation:
    def test_creates_with_defaults(self):
        reporter = HealthReporter()
        assert reporter.dogfood_monitor is not None
        assert reporter.bottleneck_detector is not None
        assert reporter.degradation_planner is not None


class TestReport:
    def test_report_returns_dict(self):
        reporter = HealthReporter()
        report = reporter.report()
        assert isinstance(report, dict)

    def test_report_contains_expected_keys(self):
        reporter = HealthReporter()
        report = reporter.report()
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
            assert key in report, f"Missing key: {key}"

    def test_report_has_20_keys(self):
        reporter = HealthReporter()
        report = reporter.report()
        assert len(report) == 20
