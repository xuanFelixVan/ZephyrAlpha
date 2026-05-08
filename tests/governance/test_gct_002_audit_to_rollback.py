"""G-CT-002 集成测试 — Audit 异常事件→Rollback 触发."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_anomaly_event_creation():
    from zephyr.governance.audit_trail.anomaly import AnomalyEvent
    event = AnomalyEvent(
        agent_id="agent-001",
        operation_signature="permission=delete",
        resource_path="/data/important.yaml",
        severity="HIGH",
        session_id="session-test",
    )
    assert event.agent_id == "agent-001"
    assert event.severity == "HIGH"
    assert event.timestamp != ""


def test_anomaly_detector_positive():
    from zephyr.governance.audit_trail.anomaly import AnomalyDetector
    detector = AnomalyDetector()
    record = {
        "agent_id": "agent-003",
        "permission": "delete",
        "resource": "/data/secrets.yaml",
        "granted": True,
        "session_id": "session-xyz",
    }
    event = detector.detect(record)
    assert event is not None
    assert event.severity == "HIGH"


def test_anomaly_detector_negative():
    from zephyr.governance.audit_trail.anomaly import AnomalyDetector
    detector = AnomalyDetector()
    record = {
        "agent_id": "agent-004",
        "permission": "read",
        "resource": "/data/public.yaml",
        "granted": True,
    }
    event = detector.detect(record)
    assert event is None


def test_rollback_on_anomaly():
    from zephyr.governance.audit_trail.anomaly import AnomalyEvent
    from zephyr.governance.rollback.contracts import RollbackHandler
    handler = RollbackHandler()
    event = AnomalyEvent(
        agent_id="agent-001",
        operation_signature="permission=delete",
        resource_path="/data/important.yaml",
        severity="HIGH",
    )
    result = handler.on_audit_anomaly(event)
    assert result["triggered"] is True
    assert result["action"] == "IMMEDIATE_ROLLBACK"
