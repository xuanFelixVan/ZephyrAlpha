# [A_test] module_id: MOD-GOV_observability_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_observability
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试 L6 Observability — 指标上报与异常检测"""

from zephyr.security.access_control.observability import (
    ObservabilityReporter,
)


class TestMetrics:
    def test_record_decision(self):
        reporter = ObservabilityReporter()
        reporter.record_decision("agent-001", "L1", "ALLOW")
        summary = reporter.get_metrics_summary()
        assert summary["total_metrics"] == 1

    def test_signal_noise_ratio(self):
        reporter = ObservabilityReporter()
        reporter.record_decision("a1", "L1", "ALLOW")
        reporter.record_decision("a1", "L1", "BLOCKED")
        assert reporter.signal_noise_ratio > 1

    def test_noise_recording(self):
        reporter = ObservabilityReporter()
        reporter.record_noise("test_source")
        assert reporter._noise_count == 1

    def test_signal_noise_alert_with_high_noise(self):
        reporter = ObservabilityReporter()
        for _ in range(10):
            reporter.record_noise("s1")
        assert reporter.check_signal_noise_alert()

    def test_density_anomaly(self):
        reporter = ObservabilityReporter()
        result = reporter.detect_density_anomaly("a1", 100, threshold_per_minute=60)
        assert result.anomaly

    def test_density_normal(self):
        reporter = ObservabilityReporter()
        result = reporter.detect_density_anomaly("a1", 10)
        assert not result.anomaly

    def test_off_hours_destructive_detected(self):
        reporter = ObservabilityReporter()
        import time

        midnight_ts = time.mktime((2026, 5, 7, 23, 30, 0, 3, 127, -1))
        result = reporter.detect_off_hours_destructive("a1", "delete:file", midnight_ts)
        assert result.anomaly

    def test_maturity_jump_anomaly(self):
        reporter = ObservabilityReporter()
        result = reporter.detect_maturity_escalation("a1", "L0_INTERN", "L2_REGULAR")
        assert result.anomaly

    def test_maturity_single_step_normal(self):
        reporter = ObservabilityReporter()
        result = reporter.detect_maturity_escalation("a1", "L0_INTERN", "L1_JUNIOR")
        assert not result.anomaly


class TestReset:
    def test_reset_clears(self):
        reporter = ObservabilityReporter()
        reporter.record_decision("a1", "L1", "ALLOW")
        reporter.reset()
        assert reporter.get_metrics_summary()["total_metrics"] == 0
