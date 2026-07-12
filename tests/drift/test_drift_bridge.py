# [A_test] module_id: SRC-TST-0770 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_drift_bridge
# [INVARIANTS] DriftBridge.sync returns BridgeResult; critical_gaps calculation
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

from zephyr.gov_audit.drift_bridge import BridgeResult, DriftBridge


class TestBridgeResult:
    def test_default_values(self):
        result = BridgeResult()
        assert result.synced_at == ""
        assert result.audit_anomalies == 0
        assert result.drift_events == 0
        assert result.matched == 0
        assert result.unmatched_audit == 0
        assert result.unmatched_drift == 0
        assert result.critical_gaps == 0


class TestDriftBridgeInstantiation:
    def test_default_path(self):
        bridge = DriftBridge()
        assert bridge._audit_events_path is not None

    def test_custom_path(self, tmp_path):
        p = tmp_path / "events.jsonl"
        bridge = DriftBridge(p)
        assert bridge._audit_events_path == p


class TestDriftBridgeSync:
    def test_sync_no_data(self, tmp_path):
        bridge = DriftBridge(tmp_path / "nonexistent.jsonl")
        with patch.object(bridge, "_scan_audit_anomalies", return_value=[]):
            with patch.object(bridge, "_scan_drift_events", return_value=[]):
                result = bridge.sync()
        assert isinstance(result, BridgeResult)
        assert result.audit_anomalies == 0
        assert result.drift_events == 0
        assert result.matched == 0
        assert result.critical_gaps == 0

    def test_sync_with_matched_events(self, tmp_path):
        bridge = DriftBridge(tmp_path / "events.jsonl")
        audit_anomalies = [
            {"target_path": "src/main.py", "severity": "MEDIUM"},
        ]
        drift_events = [
            {"target_path": "src/main.py", "severity": "MEDIUM"},
        ]
        with patch.object(bridge, "_scan_audit_anomalies", return_value=audit_anomalies):
            with patch.object(bridge, "_scan_drift_events", return_value=drift_events):
                result = bridge.sync()
        assert result.matched == 1
        assert result.unmatched_audit == 0
        assert result.unmatched_drift == 0

    def test_sync_with_unmatched_events(self, tmp_path):
        bridge = DriftBridge(tmp_path / "events.jsonl")
        audit_anomalies = [
            {"target_path": "src/a.py", "severity": "MEDIUM"},
        ]
        drift_events = [
            {"target_path": "src/b.py", "severity": "MEDIUM"},
        ]
        with patch.object(bridge, "_scan_audit_anomalies", return_value=audit_anomalies):
            with patch.object(bridge, "_scan_drift_events", return_value=drift_events):
                result = bridge.sync()
        assert result.matched == 0
        assert result.unmatched_audit == 1
        assert result.unmatched_drift == 1

    def test_sync_critical_gaps(self, tmp_path):
        bridge = DriftBridge(tmp_path / "events.jsonl")
        audit_anomalies = [
            {"target_path": "src/critical.py", "severity": "CRITICAL"},
        ]
        drift_events = []
        with patch.object(bridge, "_scan_audit_anomalies", return_value=audit_anomalies):
            with patch.object(bridge, "_scan_drift_events", return_value=drift_events):
                result = bridge.sync()
        assert result.critical_gaps == 1

    def test_sync_no_critical_gaps_for_medium(self, tmp_path):
        bridge = DriftBridge(tmp_path / "events.jsonl")
        audit_anomalies = [
            {"target_path": "src/medium.py", "severity": "MEDIUM"},
        ]
        drift_events = []
        with patch.object(bridge, "_scan_audit_anomalies", return_value=audit_anomalies):
            with patch.object(bridge, "_scan_drift_events", return_value=drift_events):
                result = bridge.sync()
        assert result.critical_gaps == 0

    def test_sync_sets_synced_at(self, tmp_path):
        bridge = DriftBridge(tmp_path / "events.jsonl")
        with patch.object(bridge, "_scan_audit_anomalies", return_value=[]):
            with patch.object(bridge, "_scan_drift_events", return_value=[]):
                result = bridge.sync()
        assert result.synced_at != ""


class TestDriftBridgeLoadEvents:
    def test_load_events_nonexistent_file(self, tmp_path):
        bridge = DriftBridge(tmp_path / "nonexistent.jsonl")
        events = bridge._load_events()
        assert events == []

    def test_load_events_with_data(self, tmp_path):
        log_file = tmp_path / "events.jsonl"
        log_file.write_text('{"event_type": "test"}\n{"event_type": "test2"}\n', encoding="utf-8")
        bridge = DriftBridge(log_file)
        events = bridge._load_events()
        assert len(events) == 2
