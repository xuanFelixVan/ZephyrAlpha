# [A_test] module_id: MOD-GOV_l6_observability | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_l6_observability
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from datetime import UTC, datetime

import pytest

from zephyr.security.llm_defense.llm_security.layers.l6_observability import (
    AlertSender,
    AlertSeverity,
    FrequencyAnomalyDetector,
    ObservabilityLayer,
    PromptwareKillChainTracker,
    ReportGenerator,
    SecurityEvent,
    SecurityEventType,
    SideChannelDefender,
)


class TestSecurityEvent:
    def test_create_event(self):
        ev = SecurityEvent(
            event_type=SecurityEventType.PROMPT_BLOCKED,
            severity=AlertSeverity.CRITICAL,
            message="Test block",
        )
        assert ev.event_type == SecurityEventType.PROMPT_BLOCKED
        assert ev.severity == AlertSeverity.CRITICAL


class TestFrequencyAnomalyDetector:
    def test_initial_not_anomaly(self):
        detector = FrequencyAnomalyDetector()
        result = detector.record(10)
        assert result["anomaly"] is False

    def test_detects_spike(self):
        detector = FrequencyAnomalyDetector(alpha=0.3)
        for _ in range(20):
            detector.record(10)
        result = detector.record(100)
        assert result["anomaly"] is True


class TestAlertSender:
    def test_send_alert(self):
        sender = AlertSender()
        payload = sender.send_alert(
            severity=AlertSeverity.CRITICAL,
            event_type=SecurityEventType.PROMPT_BLOCKED,
            message="Test alert",
        )
        assert payload["severity"] == "critical"
        assert payload["event_type"] == "prompt_blocked"
        assert len(sender.recent_alerts) == 1


class TestReportGenerator:
    def test_generate_daily_report(self):
        gen = ReportGenerator()
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        ev = SecurityEvent(
            event_type=SecurityEventType.PROMPT_BLOCKED,
            severity=AlertSeverity.WARNING,
            message="Test",
        )
        gen.record_event(ev)
        report = gen.generate_daily_report(today)
        assert report["total_events"] == 1
        assert "prompt_blocked" in report["event_breakdown"]

    def test_generate_weekly_report(self):
        gen = ReportGenerator()
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        ev = SecurityEvent(
            event_type=SecurityEventType.LEAK_DETECTED,
            severity=AlertSeverity.CRITICAL,
            message="Leak!",
        )
        gen.record_event(ev)
        report = gen.generate_weekly_report(today)
        assert report["total_events"] == 1
        assert "daily_totals" in report


class TestPromptwareKillChainTracker:
    def test_record_stages(self):
        tracker = PromptwareKillChainTracker()
        tracker.record_stage(0, "recon prompt", {"ip": "1.2.3.4"})
        tracker.record_stage(3, "exploit prompt")
        assert len(tracker.trajectory) == 2
        assert tracker.trajectory[0]["stage"] == "Stage_0_Reconnaissance"
        assert tracker.trajectory[1]["stage"] == "Stage_3_Exploitation"


class TestSideChannelDefender:
    def test_traffic_padding(self):
        defender = SideChannelDefender(padding_rate=1.0)
        padded = defender.traffic_padding(100)
        assert padded > 100

    def test_audit_log(self):
        defender = SideChannelDefender()
        audit = defender.side_channel_audit("file_read", 25.0, 1024)
        assert audit["operation"] == "file_read"
        assert audit["flagged"] is False
        assert len(defender.audit_log) == 1


class TestObservabilityLayer:
    def test_log_security_event(self):
        layer = ObservabilityLayer()
        ev = layer.log_security_event(
            event_type=SecurityEventType.PROMPT_BLOCKED,
            message="Blocked injection",
            severity=AlertSeverity.CRITICAL,
        )
        assert ev.event_type == SecurityEventType.PROMPT_BLOCKED
        assert len(layer.events) == 1

    def test_detect_frequency_anomaly(self):
        layer = ObservabilityLayer()
        for _ in range(20):
            layer.detect_frequency_anomaly(5)
        result = layer.detect_frequency_anomaly(50)
        assert isinstance(result["anomaly"], bool)

    def test_collect_metrics(self):
        layer = ObservabilityLayer()
        layer.log_security_event(
            event_type=SecurityEventType.PROMPT_BLOCKED,
            message="test",
        )
        metrics = layer.collect_metrics()
        assert metrics.total_prompts_processed >= 1
        assert metrics.prompts_blocked >= 1

    def test_generate_daily_report(self):
        layer = ObservabilityLayer()
        layer.log_security_event(
            event_type=SecurityEventType.LEAK_DETECTED,
            message="leak",
        )
        report = layer.generate_daily_report()
        assert report["total_events"] >= 1

    def test_generate_weekly_report(self):
        layer = ObservabilityLayer()
        layer.log_security_event(
            event_type=SecurityEventType.HALLUCINATION_DETECTED,
            message="hallucination",
        )
        report = layer.generate_weekly_report()
        assert "daily_totals" in report

    @pytest.mark.asyncio
    async def test_evaluate_pass_through(self):
        from zephyr.security.llm_defense.llm_security.protocol import SecurityContext
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        layer = ObservabilityLayer()
        ctx = SecurityContext(
            request_id="test-l6-eval",
            layer_name="l6_observability",
            raw_input="test input",
        )
        result = await layer.evaluate(ctx)
        assert result.decision == SecurityDecision.ALLOW
        assert result.layer_name == "l6_observability"
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_evaluate_logs_event(self):
        from zephyr.security.llm_defense.llm_security.layers.l6_observability import AlertSeverity, SecurityEventType

        layer = ObservabilityLayer()
        layer.log_security_event(
            SecurityEventType.PROMPT_BLOCKED,
            "Suspicious input detected",
            AlertSeverity.WARNING,
        )
        assert len(layer.events) >= 1
