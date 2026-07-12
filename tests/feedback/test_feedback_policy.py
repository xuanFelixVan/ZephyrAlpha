# [A_test] module_id: SRC-TST-0904 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_feedback_policy
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.feedback_policy import (
    FeedbackSummary,
    PolicyAction,
    PolicyFeedbackBridge,
    PolicyRecommendation,
    feedback_to_policy,
)


class TestPolicyFeedbackBridgeInit:
    def test_instantiation(self):
        bridge = PolicyFeedbackBridge()
        assert bridge._patterns == {}
        assert bridge._recommendations == []


class TestAggregatePatterns:
    def test_single_anomaly_creates_pattern(self):
        bridge = PolicyFeedbackBridge()
        results = [{"signature": "UNAUTHORIZED_ACCESS", "severity": "high", "agent_id": "a1"}]
        patterns = bridge.aggregate_patterns(results)
        assert len(patterns) == 1
        assert patterns[0].anomaly_type == "UNAUTHORIZED_ACCESS"
        assert patterns[0].frequency == 1

    def test_duplicate_anomaly_increments_frequency(self):
        bridge = PolicyFeedbackBridge()
        results = [
            {"signature": "UNAUTHORIZED_ACCESS", "severity": "high", "agent_id": "a1"},
            {"signature": "UNAUTHORIZED_ACCESS", "severity": "high", "agent_id": "a2"},
        ]
        patterns = bridge.aggregate_patterns(results)
        assert len(patterns) == 1
        assert patterns[0].frequency == 2
        assert "a1" in patterns[0].affected_agents
        assert "a2" in patterns[0].affected_agents

    def test_empty_input_returns_empty(self):
        bridge = PolicyFeedbackBridge()
        patterns = bridge.aggregate_patterns([])
        assert patterns == []

    def test_critical_severity_upgrades_pattern(self):
        bridge = PolicyFeedbackBridge()
        results = [
            {"signature": "X", "severity": "low", "agent_id": "a1"},
            {"signature": "X", "severity": "critical", "agent_id": "a2"},
        ]
        patterns = bridge.aggregate_patterns(results)
        assert patterns[0].severity == "critical"

    def test_uses_anomaly_type_fallback(self):
        bridge = PolicyFeedbackBridge()
        results = [{"anomaly_type": "BULK_DELETE", "severity": "medium", "agent_id": ""}]
        patterns = bridge.aggregate_patterns(results)
        assert patterns[0].anomaly_type == "BULK_DELETE"


class TestGenerateRecommendations:
    def test_generates_alert_for_low_severity(self):
        bridge = PolicyFeedbackBridge()
        bridge.aggregate_patterns([{"signature": "X", "severity": "low", "agent_id": "a1"}])
        recs = bridge.generate_recommendations()
        assert len(recs) == 1
        assert recs[0].action == PolicyAction.ALERT

    def test_critical_high_frequency_generates_block(self):
        bridge = PolicyFeedbackBridge()
        for _ in range(3):
            bridge.aggregate_patterns([{"signature": "X", "severity": "critical", "agent_id": "a1"}])
        recs = bridge.generate_recommendations()
        assert recs[0].action == PolicyAction.BLOCK

    def test_critical_low_frequency_generates_escalate(self):
        bridge = PolicyFeedbackBridge()
        bridge.aggregate_patterns([{"signature": "X", "severity": "critical", "agent_id": "a1"}])
        recs = bridge.generate_recommendations()
        assert recs[0].action == PolicyAction.ESCALATE

    def test_high_high_frequency_generates_throttle(self):
        bridge = PolicyFeedbackBridge()
        for _ in range(5):
            bridge.aggregate_patterns([{"signature": "X", "severity": "high", "agent_id": "a1"}])
        recs = bridge.generate_recommendations()
        assert recs[0].action == PolicyAction.THROTTLE

    def test_no_patterns_returns_empty(self):
        bridge = PolicyFeedbackBridge()
        recs = bridge.generate_recommendations()
        assert recs == []


class TestGetSummary:
    def test_summary_reflects_state(self):
        bridge = PolicyFeedbackBridge()
        bridge.aggregate_patterns(
            [
                {"signature": "A", "severity": "critical", "agent_id": "a1"},
                {"signature": "B", "severity": "low", "agent_id": "a2"},
            ]
        )
        bridge.generate_recommendations()
        summary = bridge.get_summary()
        assert isinstance(summary, FeedbackSummary)
        assert summary.total_patterns == 2
        assert summary.total_recommendations == 2
        assert summary.high_severity_count == 1

    def test_empty_bridge_summary(self):
        bridge = PolicyFeedbackBridge()
        summary = bridge.get_summary()
        assert summary.total_patterns == 0
        assert summary.total_recommendations == 0
        assert summary.high_severity_count == 0


class TestFeedbackToPolicyFunction:
    def test_function_returns_recommendations(self):
        results = [{"signature": "Y", "severity": "medium", "agent_id": "a1"}]
        recs = feedback_to_policy(results)
        assert len(recs) >= 1
        assert isinstance(recs[0], PolicyRecommendation)

    def test_function_empty_input(self):
        recs = feedback_to_policy([])
        assert recs == []
