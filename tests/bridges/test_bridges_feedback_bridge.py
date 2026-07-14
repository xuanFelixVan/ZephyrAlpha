# [A_test] module_id: SRC-TST-0458 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_bridges_feedback_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.gov_audit.bridges.audit_feedback_bridge import AuditFeedbackBridge


@pytest.fixture
def bridge():
    return AuditFeedbackBridge()


class TestAuditFeedbackBridge:
    def test_instantiation(self):
        b = AuditFeedbackBridge()
        assert len(b._anomaly_to_signal) == 13
        assert "ANM-001" in b._anomaly_to_signal

    def test_anomaly_to_fle_signal_known(self, bridge):
        anomaly = {
            "signature_id": "ANM-001",
            "severity": "HIGH",
            "agent_id": "a1",
            "timestamp": "2026-01-01T00:00:00Z",
            "details": {"target": "/tmp/f.py"},
        }
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["source"] == "audit-trail"
        assert result["signal_type"] == "UNAUTHORIZED_ACCESS"
        assert result["layer"] == "L3_ARCHITECTURE"
        assert result["severity"] == "HIGH"

    def test_anomaly_to_fle_signal_unknown(self, bridge):
        anomaly = {"signature_id": "UNKNOWN-999", "severity": "LOW", "agent_id": "a1"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is None

    def test_anomaly_to_fle_signal_medium_severity(self, bridge):
        anomaly = {"signature_id": "ANM-004", "severity": "MEDIUM", "agent_id": "a1"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["layer"] == "L2_PATTERN"

    def test_anomaly_to_fle_signal_low_severity(self, bridge):
        anomaly = {"signature_id": "ANM-006", "severity": "LOW", "agent_id": "a1"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["layer"] == "L1_TASK"

    def test_anomaly_to_fle_signal_critical(self, bridge):
        anomaly = {"signature_id": "ANM-005", "severity": "CRITICAL", "agent_id": "a1"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["layer"] == "L3_ARCHITECTURE"

    def test_evolution_to_audit_record(self, bridge):
        proposal = {
            "signal": "UNAUTHORIZED_ACCESS",
            "layer": "L3_ARCHITECTURE",
            "severity": "HIGH",
            "recommended_action": "tighten_rbac",
        }
        result = bridge.evolution_to_audit_record(proposal)
        assert result["event_type"] == "feedback_loop_evolution"
        assert result["source"] == "fle_evolution_engine"
        assert result["signal"] == "UNAUTHORIZED_ACCESS"
        assert result["recommended_action"] == "tighten_rbac"
        assert result["provenance"] == "feedback-loop"

    def test_evolution_to_audit_record_empty(self, bridge):
        result = bridge.evolution_to_audit_record({})
        assert result["signal"] == ""
        assert result["layer"] == ""

    def test_scan_and_bridge_no_events(self, bridge):
        with patch("zephyr.gov_audit.query.AuditQuery") as mock_q:
            mock_inst = MagicMock()
            mock_inst._load_events.return_value = []
            mock_q.return_value = mock_inst
            result = bridge.scan_and_bridge()
            assert result == []

    def test_scan_and_bridge_with_anomalies(self, bridge):
        with (
            patch("zephyr.gov_audit.query.AuditQuery") as mock_q,
            patch("zephyr.gov_audit.anomaly.AnomalyDetector") as mock_d,
        ):
            mock_q_inst = MagicMock()
            mock_q_inst._load_events.return_value = [{"event_type": "test"}]
            mock_q.return_value = mock_q_inst
            mock_anomaly = MagicMock()
            mock_anomaly.signature_id = "ANM-001"
            mock_anomaly.severity = MagicMock(value="HIGH")
            mock_anomaly.agent_id = "a1"
            mock_anomaly.timestamp = "2026-01-01T00:00:00Z"
            mock_anomaly.details = {}
            mock_d_inst = MagicMock()
            mock_d_inst.scan.return_value = [mock_anomaly]
            mock_d.return_value = mock_d_inst
            result = bridge.scan_and_bridge()
            assert len(result) >= 1

    def test_scan_and_bridge_exception(self, bridge):
        with patch("zephyr.gov_audit.query.AuditQuery", side_effect=Exception("fail")):
            result = bridge.scan_and_bridge()
            assert result == []

    def test_classify_layer_critical(self):
        assert AuditFeedbackBridge._classify_layer("CRITICAL") == "L3_ARCHITECTURE"

    def test_classify_layer_high(self):
        assert AuditFeedbackBridge._classify_layer("HIGH") == "L3_ARCHITECTURE"

    def test_classify_layer_medium(self):
        assert AuditFeedbackBridge._classify_layer("MEDIUM") == "L2_PATTERN"

    def test_classify_layer_low(self):
        assert AuditFeedbackBridge._classify_layer("LOW") == "L1_TASK"
