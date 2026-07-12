# [A_test] module_id: SRC-TST-0125 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-282 | tests/governance/test_gct_002_audit_to_rollback.py | §
# [TTL] task_bound
from __future__ import annotations

"""
[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-infra_ops/rollback-system/blueprint.md
[MODULE] tests.governance.test_gct_002_audit_to_rollback
[INVARIANTS] G-CT-002: Audit→Rollback 集成契约
[MODIFY-GUARD] anomaly.py; contracts.py
[CONSUMERS] —
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] —
[TESTS] self
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_anomaly_event_creation():
    from zephyr.gov_audit.anomaly import AnomalyEvent, AnomalySignature

    event = AnomalyEvent(
        signature=AnomalySignature.UNAUTHORIZED_ACCESS,
        severity="high",
        description="Unauthorized delete by agent-001",
        evidence={"agent_id": "agent-001", "resource": "/data/important.yaml"},
        score=0.9,
    )
    assert event.signature == AnomalySignature.UNAUTHORIZED_ACCESS
    assert event.severity == "high"
    assert event.detected_at != ""


def test_anomaly_detector_positive():
    import json
    import tempfile

    from zephyr.gov_audit.anomaly import AnomalyDetector

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "agent_id": "agent-003",
                    "permission": "delete",
                    "resource": "/data/secrets.yaml",
                    "granted": True,
                    "session_id": "session-xyz",
                    "timestamp": "2026-05-15T00:00:00Z",
                }
            )
            + "\n"
        )
        tmp_path = f.name
    detector = AnomalyDetector(event_log_path=tmp_path)
    results = detector.scan()
    assert len(results) > 0
    assert results[0].severity in ("high", "medium", "low")
    Path(tmp_path).unlink(missing_ok=True)


def test_anomaly_detector_negative():
    import json
    import tempfile

    from zephyr.gov_audit.anomaly import AnomalyDetector

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "agent_id": "agent-004",
                    "permission": "read",
                    "resource": "/data/public.yaml",
                    "granted": True,
                    "timestamp": "2026-05-15T00:00:00Z",
                }
            )
            + "\n"
        )
        tmp_path = f.name
    detector = AnomalyDetector(event_log_path=tmp_path)
    results = detector.scan()
    assert isinstance(results, list)
    Path(tmp_path).unlink(missing_ok=True)


def test_rollback_on_anomaly():
    from zephyr.gov_audit.anomaly import AnomalyEvent, AnomalySignature
    from zephyr.governance.escalation.contracts import RollbackHandler

    handler = RollbackHandler()
    event = AnomalyEvent(
        signature=AnomalySignature.UNAUTHORIZED_ACCESS,
        severity="high",
        description="Unauthorized delete by agent-001",
        evidence={"agent_id": "agent-001", "resource": "/data/important.yaml"},
        score=0.9,
    )
    result = handler.on_audit_anomaly(event)
    assert result["triggered"] is True
    assert result["action"] in ("IMMEDIATE_ROLLBACK", "FLAGGED_FOR_REVIEW")
