# [A_test] module_id: SRC-TST-0454 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_bridges_anomaly
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_bridges_anomaly.py -q
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_audit.anomaly import AnomalyDetector, AnomalyEvent


class TestAnomalyEventInstantiation:
    def test_default_values(self):
        event = AnomalyEvent(agent_id="a1", operation_signature="perm=delete", resource_path="/tmp/f.py")
        assert event.severity == "WARN"
        assert event.event_type == "anomaly_detected"
        assert event.session_id == ""
        assert event.detail == ""
        assert event.timestamp != ""

    def test_custom_values(self):
        event = AnomalyEvent(
            agent_id="a1",
            operation_signature="perm=delete",
            resource_path="/tmp/f.py",
            severity="HIGH",
            session_id="s1",
            detail="Suspicious",
        )
        assert event.severity == "HIGH"
        assert event.session_id == "s1"
        assert event.detail == "Suspicious"

    def test_required_fields_missing_raises(self):
        with pytest.raises(Exception):
            AnomalyEvent()


class TestAnomalyDetectorInstantiation:
    def test_instantiation(self):
        detector = AnomalyDetector()
        assert "delete" in detector._SUSPICIOUS_OPERATIONS

    def test_suspicious_operations_contents(self):
        detector = AnomalyDetector()
        expected = {"delete", "truncate", "drop", "revoke", "sudo", "root"}
        assert expected == detector._SUSPICIOUS_OPERATIONS


class TestAnomalyDetectorDetect:
    def test_detect_suspicious_delete_granted(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "delete", "granted": True, "resource": "/tmp/important.py"}
        result = detector.detect(record)
        assert result is not None
        assert result.severity == "HIGH"
        assert result.agent_id == "a1"

    def test_detect_suspicious_truncate_granted(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "truncate", "granted": True, "resource": "/tmp/data.db"}
        result = detector.detect(record)
        assert result is not None
        assert result.severity == "HIGH"

    def test_detect_suspicious_sudo_granted(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "sudo", "granted": True, "resource": "/etc/passwd"}
        result = detector.detect(record)
        assert result is not None
        assert result.severity == "WARN"

    def test_detect_suspicious_drop_granted(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "drop", "granted": True, "resource": "/db/table"}
        result = detector.detect(record)
        assert result is not None
        assert result.severity == "WARN"

    def test_detect_not_granted_returns_none(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "delete", "granted": False, "resource": "/tmp/f.py"}
        result = detector.detect(record)
        assert result is None

    def test_detect_normal_operation_returns_none(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "read", "granted": True, "resource": "/tmp/f.py"}
        result = detector.detect(record)
        assert result is None

    def test_detect_empty_permission_returns_none(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "", "granted": True}
        result = detector.detect(record)
        assert result is None

    def test_detect_missing_fields_returns_none(self):
        detector = AnomalyDetector()
        result = detector.detect({})
        assert result is None

    def test_detect_case_insensitive(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "DELETE", "granted": True, "resource": "/tmp/f.py"}
        result = detector.detect(record)
        assert result is not None

    def test_detect_operation_signature_format(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "delete", "granted": True, "resource": "/tmp/f.py"}
        result = detector.detect(record)
        assert result is not None
        assert result.operation_signature == "permission=delete"

    def test_detect_resource_path_populated(self):
        detector = AnomalyDetector()
        record = {"agent_id": "a1", "permission": "sudo", "granted": True, "resource": "/etc/hosts"}
        result = detector.detect(record)
        assert result is not None
        assert result.resource_path == "/etc/hosts"


class TestBoundaryConditions:
    def test_granted_false_even_for_suspicious(self):
        detector = AnomalyDetector()
        for perm in ["delete", "truncate", "drop", "revoke", "sudo", "root"]:
            record = {"agent_id": "a1", "permission": perm, "granted": False, "resource": "/tmp/f"}
            assert detector.detect(record) is None

    def test_granted_true_for_non_suspicious(self):
        detector = AnomalyDetector()
        for perm in ["read", "write", "execute", "list"]:
            record = {"agent_id": "a1", "permission": perm, "granted": True, "resource": "/tmp/f"}
            assert detector.detect(record) is None

    def test_severity_high_only_for_delete_and_truncate(self):
        detector = AnomalyDetector()
        high_perms = {"delete", "truncate"}
        for perm in detector._SUSPICIOUS_OPERATIONS:
            record = {"agent_id": "a1", "permission": perm, "granted": True, "resource": "/tmp/f"}
            result = detector.detect(record)
            assert result is not None
            if perm in high_perms:
                assert result.severity == "HIGH"
            else:
                assert result.severity == "WARN"
