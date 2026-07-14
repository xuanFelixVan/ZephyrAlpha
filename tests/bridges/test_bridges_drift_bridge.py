# [A_test] module_id: SRC-TST-0457 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_bridges_drift_bridge
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

import json
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from zephyr.gov_audit.drift_bridge import BridgeResult, DriftBridge


@pytest.fixture
def bridge(tmp_path):
    return DriftBridge(audit_events_path=tmp_path / "events.jsonl")


@pytest.fixture
def bridge_with_events(tmp_path):
    log_path = tmp_path / "events.jsonl"
    events = [
        {
            "entry_id": "e1",
            "event_type": "anomaly_detected",
            "agent_id": "a",
            "timestamp": datetime.now(UTC).isoformat(),
            "target_path": "/tmp/f1.py",
            "severity": "HIGH",
        },
    ]
    with open(log_path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    return DriftBridge(audit_events_path=log_path)


class TestBridgeResult:
    def test_default_values(self):
        result = BridgeResult()
        assert result.audit_anomalies == 0
        assert result.drift_events == 0
        assert result.matched == 0
        assert result.unmatched_audit == 0
        assert result.unmatched_drift == 0
        assert result.critical_gaps == 0

    def test_custom_values(self):
        result = BridgeResult(audit_anomalies=5, drift_events=3, matched=2)
        assert result.audit_anomalies == 5
        assert result.matched == 2


class TestDriftBridge:
    def test_instantiation(self, tmp_path):
        b = DriftBridge(audit_events_path=tmp_path / "events.jsonl")
        assert b._audit_events_path == tmp_path / "events.jsonl"

    def test_sync_no_events(self, bridge):
        with (
            patch.object(bridge, "_scan_audit_anomalies", return_value=[]),
            patch.object(bridge, "_scan_drift_events", return_value=[]),
        ):
            result = bridge.sync()
            assert isinstance(result, BridgeResult)
            assert result.audit_anomalies == 0
            assert result.drift_events == 0
            assert result.matched == 0

    def test_sync_with_matches(self, bridge):
        audit_anomalies = [
            {"signature_id": "ANM-001", "severity": "HIGH", "target_path": "/tmp/f1.py"},
        ]
        drift_events = [
            {"drift_id": "d1", "target_path": "/tmp/f1.py", "severity": "HIGH"},
        ]
        with (
            patch.object(bridge, "_scan_audit_anomalies", return_value=audit_anomalies),
            patch.object(bridge, "_scan_drift_events", return_value=drift_events),
        ):
            result = bridge.sync()
            assert result.matched == 1
            assert result.unmatched_audit == 0
            assert result.unmatched_drift == 0

    def test_sync_with_unmatched(self, bridge):
        audit_anomalies = [
            {"signature_id": "ANM-001", "severity": "HIGH", "target_path": "/tmp/f1.py"},
        ]
        drift_events = [
            {"drift_id": "d1", "target_path": "/tmp/f2.py", "severity": "MEDIUM"},
        ]
        with (
            patch.object(bridge, "_scan_audit_anomalies", return_value=audit_anomalies),
            patch.object(bridge, "_scan_drift_events", return_value=drift_events),
        ):
            result = bridge.sync()
            assert result.matched == 0
            assert result.unmatched_audit == 1
            assert result.unmatched_drift == 1

    def test_sync_critical_gaps(self, bridge):
        audit_anomalies = [
            {"signature_id": "ANM-001", "severity": "CRITICAL", "target_path": "/tmp/critical.py"},
        ]
        drift_events = []
        with (
            patch.object(bridge, "_scan_audit_anomalies", return_value=audit_anomalies),
            patch.object(bridge, "_scan_drift_events", return_value=drift_events),
        ):
            result = bridge.sync()
            assert result.critical_gaps == 1

    def test_scan_audit_anomalies_import_error(self, bridge):
        with patch("zephyr.gov_audit.anomaly.AnomalyDetector", side_effect=ImportError):
            result = bridge._scan_audit_anomalies()
            assert result == []

    def test_scan_drift_events_import_error(self, bridge):
        with patch("builtins.__import__", side_effect=ImportError("no module")):
            result = bridge._scan_drift_events()
            assert result == []

    def test_load_events_no_file(self, bridge):
        events = bridge._load_events()
        assert events == []

    def test_load_events_with_data(self, bridge_with_events):
        events = bridge_with_events._load_events()
        assert len(events) == 1

    def test_sync_timestamp_set(self, bridge):
        with (
            patch.object(bridge, "_scan_audit_anomalies", return_value=[]),
            patch.object(bridge, "_scan_drift_events", return_value=[]),
        ):
            result = bridge.sync()
            assert result.synced_at != ""
