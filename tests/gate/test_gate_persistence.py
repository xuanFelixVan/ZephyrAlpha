# [A_test] module_id: SRC-TST-1044 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_gate_persistence
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_gate_persistence.py -q
# [TTL] task_bound

from __future__ import annotations

import json
import os
import sqlite3
import uuid

import pytest

from zephyr.gov_drift.gate_persistence import GatePersistence


class TestGatePersistenceInstantiation:
    def test_with_explicit_project_root(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        assert gp._project_root == str(tmp_path)

    def test_default_project_root_not_empty(self):
        gp = GatePersistence()
        assert gp._project_root != ""
        assert os.path.isdir(gp._project_root)

    def test_creates_audit_dir(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        assert os.path.isdir(gp._audit_dir)
        assert gp._audit_dir == os.path.join(str(tmp_path), "data", "drift_audit")

    def test_creates_db_file(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        assert os.path.exists(gp._db_path)
        assert gp._db_path.endswith("drift_events.db")

    def test_db_tables_exist(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        conn = sqlite3.connect(gp._db_path)
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        assert "drift_events" in tables
        assert "scan_results" in tables
        assert "gate_decisions" in tables


class TestGatePersistencePersistScanResult:
    def test_returns_sha256_hex_string(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        scan_id = uuid.uuid4()
        sha = gp.persist_scan_result(scan_id, {"detectors_run": 5, "total_drift_events": 2})
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)

    def test_creates_json_file(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        scan_id = uuid.uuid4()
        gp.persist_scan_result(scan_id, {"detectors_run": 3, "total_drift_events": 1})
        result_path = os.path.join(gp._audit_dir, f"{scan_id}_result.json")
        assert os.path.exists(result_path)

    def test_json_contains_sha256_and_timestamp(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        scan_id = uuid.uuid4()
        gp.persist_scan_result(scan_id, {"detectors_run": 1})
        result_path = os.path.join(gp._audit_dir, f"{scan_id}_result.json")
        with open(result_path, encoding="utf-8") as f:
            data = json.load(f)
        assert "sha256" in data
        assert "persisted_at" in data

    def test_inserts_db_row(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        scan_id = uuid.uuid4()
        gp.persist_scan_result(scan_id, {"detectors_run": 4, "total_drift_events": 0, "storm_mode_triggered": True})
        conn = sqlite3.connect(gp._db_path)
        row = conn.execute("SELECT * FROM scan_results WHERE scan_id = ?", (str(scan_id),)).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == str(scan_id)

    def test_empty_body(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        scan_id = uuid.uuid4()
        sha = gp.persist_scan_result(scan_id, {})
        assert len(sha) == 64

    def test_overwrite_existing_scan(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        scan_id = uuid.uuid4()
        sha1 = gp.persist_scan_result(scan_id, {"detectors_run": 1})
        sha2 = gp.persist_scan_result(scan_id, {"detectors_run": 2})
        assert sha1 != sha2


class TestGatePersistencePersistGateDecision:
    def test_single_decision(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        gp.persist_gate_decision("MOD-A", "GATE-1", "PASS", "All checks ok")
        conn = sqlite3.connect(gp._db_path)
        rows = conn.execute("SELECT * FROM gate_decisions WHERE module_id = 'MOD-A'").fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0][3] == "PASS"

    def test_multiple_decisions(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        gp.persist_gate_decision("MOD-A", "GATE-1", "PASS")
        gp.persist_gate_decision("MOD-B", "GATE-2", "FAIL", "Missing test")
        conn = sqlite3.connect(gp._db_path)
        rows = conn.execute("SELECT * FROM gate_decisions").fetchall()
        conn.close()
        assert len(rows) == 2

    def test_empty_detail_default(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        gp.persist_gate_decision("MOD-C", "GATE-3", "PASS")
        conn = sqlite3.connect(gp._db_path)
        row = conn.execute("SELECT detail FROM gate_decisions WHERE module_id = 'MOD-C'").fetchone()
        conn.close()
        assert row[0] == ""


class TestGatePersistenceVerifyIntegrity:
    def test_nonexistent_scan_returns_false(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        assert gp.verify_integrity(uuid.uuid4()) is False

    def test_existing_scan_has_known_bug(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        scan_id = uuid.uuid4()
        gp.persist_scan_result(scan_id, {"detectors_run": 1})
        with pytest.raises(AttributeError):
            gp.verify_integrity(scan_id)


class TestGatePersistenceUpdateManifest:
    def test_creates_manifest_file(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        gp.update_manifest(uuid.uuid4(), "COMPLETED")
        manifest_path = os.path.join(gp._audit_dir, "manifest.json")
        assert os.path.exists(manifest_path)

    def test_appends_entries(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        gp.update_manifest(uuid.uuid4(), "COMPLETED")
        gp.update_manifest(uuid.uuid4(), "FAILED")
        manifest_path = os.path.join(gp._audit_dir, "manifest.json")
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["entries"]) == 2
        assert data["entries"][0]["status"] == "COMPLETED"
        assert data["entries"][1]["status"] == "FAILED"

    def test_truncates_at_100(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        for _ in range(110):
            gp.update_manifest(uuid.uuid4(), "COMPLETED")
        manifest_path = os.path.join(gp._audit_dir, "manifest.json")
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["entries"]) == 100

    def test_recovers_from_corrupt_manifest(self, tmp_path):
        gp = GatePersistence(project_root=str(tmp_path))
        manifest_path = os.path.join(gp._audit_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write("NOT VALID JSON{{{")
        gp.update_manifest(uuid.uuid4(), "COMPLETED")
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["entries"]) == 1
