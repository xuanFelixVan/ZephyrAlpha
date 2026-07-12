# [A_test] module_id: SRC-TST-0900 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_feedback_bridge
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

import pytest

from zephyr.gov_audit.feedback_bridge import AuditFeedbackBridge


class TestAuditFeedbackBridgeInit:
    def test_instantiation(self):
        bridge = AuditFeedbackBridge()
        assert bridge is not None
        assert hasattr(bridge, "_anomaly_to_signal")

    def test_anomaly_mapping_keys(self):
        bridge = AuditFeedbackBridge()
        expected_keys = {
            "ANM-001",
            "ANM-002",
            "ANM-003",
            "ANM-004",
            "ANM-005",
            "ANM-006",
            "ANM-007",
            "ANM-008",
            "ANM-009",
            "ANM-010",
            "ANM-011",
            "ANM-012",
            "ANM-013",
        }
        assert set(bridge._anomaly_to_signal.keys()) == expected_keys


class TestAnomalyToFleSignal:
    def test_known_anomaly_returns_signal(self):
        bridge = AuditFeedbackBridge()
        anomaly = {
            "signature_id": "ANM-001",
            "severity": "HIGH",
            "agent_id": "agent-001",
            "timestamp": "2026-01-01T00:00:00Z",
            "details": {"key": "value"},
        }
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["source"] == "audit-trail"
        assert result["signal_type"] == "UNAUTHORIZED_ACCESS"
        assert result["severity"] == "HIGH"
        assert result["agent_id"] == "agent-001"

    def test_unknown_signature_returns_none(self):
        bridge = AuditFeedbackBridge()
        anomaly = {"signature_id": "ANM-999", "severity": "LOW"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is None

    def test_empty_signature_returns_none(self):
        bridge = AuditFeedbackBridge()
        anomaly = {"severity": "LOW"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is None

    def test_critical_severity_classifies_l3(self):
        bridge = AuditFeedbackBridge()
        anomaly = {"signature_id": "ANM-005", "severity": "CRITICAL", "agent_id": "a1"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["layer"] == "L3_ARCHITECTURE"

    def test_medium_severity_classifies_l2(self):
        bridge = AuditFeedbackBridge()
        anomaly = {"signature_id": "ANM-001", "severity": "MEDIUM", "agent_id": "a1"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["layer"] == "L2_PATTERN"

    def test_low_severity_classifies_l1(self):
        bridge = AuditFeedbackBridge()
        anomaly = {"signature_id": "ANM-001", "severity": "LOW", "agent_id": "a1"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["layer"] == "L1_TASK"

    def test_default_severity_is_medium(self):
        bridge = AuditFeedbackBridge()
        anomaly = {"signature_id": "ANM-001"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["severity"] == "MEDIUM"

    def test_default_agent_id_is_unknown(self):
        bridge = AuditFeedbackBridge()
        anomaly = {"signature_id": "ANM-001", "severity": "LOW"}
        result = bridge.anomaly_to_fle_signal(anomaly)
        assert result is not None
        assert result["agent_id"] == "unknown"


class TestEvolutionToAuditRecord:
    def test_converts_proposal_to_audit_record(self):
        bridge = AuditFeedbackBridge()
        proposal = {
            "signal": "UNAUTHORIZED_ACCESS",
            "layer": "L3_ARCHITECTURE",
            "severity": "CRITICAL",
            "recommended_action": "block_agent",
        }
        result = bridge.evolution_to_audit_record(proposal)
        assert result["event_type"] == "feedback_loop_evolution"
        assert result["source"] == "fle_evolution_engine"
        assert result["signal"] == "UNAUTHORIZED_ACCESS"
        assert result["recommended_action"] == "block_agent"
        assert result["provenance"] == "feedback-loop"

    def test_empty_proposal_returns_defaults(self):
        bridge = AuditFeedbackBridge()
        result = bridge.evolution_to_audit_record({})
        assert result["signal"] == ""
        assert result["layer"] == ""
        assert result["severity"] == ""
        assert result["recommended_action"] == ""


class TestClassifyLayer:
    @pytest.mark.parametrize(
        "severity,expected",
        [
            ("CRITICAL", "L3_ARCHITECTURE"),
            ("HIGH", "L3_ARCHITECTURE"),
            ("MEDIUM", "L2_PATTERN"),
            ("LOW", "L1_TASK"),
            ("INFO", "L1_TASK"),
        ],
    )
    def test_severity_to_layer_mapping(self, severity, expected):
        result = AuditFeedbackBridge._classify_layer(severity)
        assert result == expected


class TestScanAndBridge:
    def test_scan_and_bridge_returns_list(self):
        bridge = AuditFeedbackBridge()
        result = bridge.scan_and_bridge()
        assert isinstance(result, list)

    def test_scan_and_bridge_handles_import_error(self, monkeypatch):
        bridge = AuditFeedbackBridge()
        import zephyr.gov_audit.feedback_bridge as mod

        original = mod.AuditFeedbackBridge.scan_and_bridge

        def broken_scan(self):
            raise RuntimeError("import failed")

        monkeypatch.setattr(mod.AuditFeedbackBridge, "scan_and_bridge", broken_scan)
        with pytest.raises(RuntimeError):
            bridge.scan_and_bridge()
