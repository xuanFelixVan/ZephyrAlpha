# [A_test] module_id: SRC-TST-1719 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_tamper_proof_audit
# [INVARIANTS] append_only_triggers;event_hash_deterministic;anomaly_detection_thresholds
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_tamper_proof_audit.py
# [TTL] task_bound

import os
import sqlite3
import tempfile
from datetime import datetime

import pytest

from zephyr.gov_drift.tamper_proof_audit import (
    AnomalyAlert,
    AuditRecord,
    _sha256,
    count_states,
    detect_anomalies,
    setup_append_only,
    snapshot_event_hash,
)


class TestSha256:
    def test_deterministic(self):
        assert _sha256("hello") == _sha256("hello")

    def test_different_inputs(self):
        assert _sha256("a") != _sha256("b")

    def test_hex_length(self):
        h = _sha256("test")
        assert len(h) == 64


class TestAuditRecord:
    def test_creation(self):
        r = AuditRecord(
            scan_id="scan-001",
            state_counts={"DETECTED": 5},
            events_hash="abc123",
            file_hashes={"src/foo.py": "def456"},
        )
        assert r.scan_id == "scan-001"
        assert r.state_counts == {"DETECTED": 5}
        assert r.committed_to_git is False
        assert r.verified is False

    def test_timestamp_auto_set(self):
        r = AuditRecord(scan_id="s", state_counts={}, events_hash="", file_hashes={})
        assert isinstance(r.timestamp, datetime)


class TestAnomalyAlert:
    def test_creation(self):
        a = AnomalyAlert(
            alert_id="a1",
            anomaly_type="TOTAL_ROW_DROP",
            description="count dropped",
        )
        assert a.severity == "CRITICAL"
        assert a.recovery_suggestion == ""

    def test_custom_severity(self):
        a = AnomalyAlert(alert_id="a2", anomaly_type="X", severity="HIGH")
        assert a.severity == "HIGH"


class TestSetupAppendOnly:
    def test_creates_triggers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn = sqlite3.connect(db_path)
            try:
                conn.execute(
                    "CREATE TABLE drift_events (event_id TEXT, detector_id TEXT, severity TEXT, state TEXT, timestamp TEXT)"
                )
                conn.commit()
            finally:
                conn.close()
            result = setup_append_only(db_path)
            assert result is True
            conn = sqlite3.connect(db_path)
            try:
                conn.execute("INSERT INTO drift_events VALUES ('1','d','H','DETECTED','2026-01-01')")
                conn.commit()
                with pytest.raises(sqlite3.IntegrityError, match="denied"):
                    conn.execute("UPDATE drift_events SET state='RESOLVED' WHERE event_id='1'")
                with pytest.raises(sqlite3.IntegrityError, match="denied"):
                    conn.execute("DELETE FROM drift_events WHERE event_id='1'")
            finally:
                conn.close()

    def test_invalid_path_returns_false(self):
        assert setup_append_only("/nonexistent/path/db.db") is False


class TestSnapshotEventHash:
    def test_empty_db(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn = sqlite3.connect(db_path)
            conn.execute(
                "CREATE TABLE drift_events (event_id TEXT, detector_id TEXT, severity TEXT, state TEXT, timestamp TEXT)"
            )
            conn.commit()
            conn.close()
            h = snapshot_event_hash(db_path)
            assert isinstance(h, str)
            assert len(h) == 64

    def test_with_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn = sqlite3.connect(db_path)
            conn.execute(
                "CREATE TABLE drift_events (event_id TEXT, detector_id TEXT, severity TEXT, state TEXT, timestamp TEXT)"
            )
            conn.execute("INSERT INTO drift_events VALUES ('1','d','H','DETECTED','2026-01-01')")
            conn.commit()
            conn.close()
            h = snapshot_event_hash(db_path)
            assert len(h) == 64

    def test_invalid_path_returns_empty(self):
        assert snapshot_event_hash("/nonexistent/db.db") == ""


class TestCountStates:
    def test_empty_db(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn = sqlite3.connect(db_path)
            conn.execute(
                "CREATE TABLE drift_events (event_id TEXT, detector_id TEXT, severity TEXT, state TEXT, timestamp TEXT)"
            )
            conn.commit()
            conn.close()
            assert count_states(db_path) == {}

    def test_with_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            conn = sqlite3.connect(db_path)
            conn.execute(
                "CREATE TABLE drift_events (event_id TEXT, detector_id TEXT, severity TEXT, state TEXT, timestamp TEXT)"
            )
            conn.execute("INSERT INTO drift_events VALUES ('1','d','H','DETECTED','2026-01-01')")
            conn.execute("INSERT INTO drift_events VALUES ('2','d','M','RESOLVED','2026-01-02')")
            conn.execute("INSERT INTO drift_events VALUES ('3','d','L','DETECTED','2026-01-03')")
            conn.commit()
            conn.close()
            counts = count_states(db_path)
            assert counts.get("DETECTED") == 2
            assert counts.get("RESOLVED") == 1


class TestDetectAnomalies:
    def test_no_previous_no_alerts(self):
        current = AuditRecord(scan_id="s1", state_counts={"DETECTED": 10}, events_hash="h", file_hashes={})
        alerts = detect_anomalies(current)
        assert alerts == []

    def test_total_row_drop_triggers_alert(self):
        previous = AuditRecord(scan_id="s0", state_counts={"DETECTED": 100}, events_hash="h", file_hashes={})
        current = AuditRecord(scan_id="s1", state_counts={"DETECTED": 10}, events_hash="h", file_hashes={})
        alerts = detect_anomalies(current, previous)
        assert len(alerts) >= 1
        assert alerts[0].anomaly_type == "TOTAL_ROW_DROP"

    def test_resolved_rewind_triggers_alert(self):
        previous = AuditRecord(
            scan_id="s0", state_counts={"DETECTED": 20, "RESOLVED": 50}, events_hash="h", file_hashes={}
        )
        current = AuditRecord(
            scan_id="s1", state_counts={"DETECTED": 20, "RESOLVED": 10}, events_hash="h", file_hashes={}
        )
        alerts = detect_anomalies(current, previous)
        assert any(a.anomaly_type == "RESOLVED_REWIND" for a in alerts)

    def test_no_anomaly_when_stable(self):
        previous = AuditRecord(
            scan_id="s0", state_counts={"DETECTED": 10, "RESOLVED": 5}, events_hash="h", file_hashes={}
        )
        current = AuditRecord(
            scan_id="s1", state_counts={"DETECTED": 12, "RESOLVED": 6}, events_hash="h", file_hashes={}
        )
        alerts = detect_anomalies(current, previous)
        assert alerts == []

    def test_small_counts_no_false_positive(self):
        previous = AuditRecord(scan_id="s0", state_counts={"DETECTED": 5}, events_hash="h", file_hashes={})
        current = AuditRecord(scan_id="s1", state_counts={"DETECTED": 1}, events_hash="h", file_hashes={})
        alerts = detect_anomalies(current, previous)
        total_drop_alerts = [a for a in alerts if a.anomaly_type == "TOTAL_ROW_DROP"]
        assert len(total_drop_alerts) == 0
