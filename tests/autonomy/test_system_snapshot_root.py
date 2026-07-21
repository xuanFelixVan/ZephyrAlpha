# [A_test] module_id: MOD-GOV_system_snapshot_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.system_snapshot
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import sqlite3

import pytest

try:
    from zephyr.infrastructure.system_snapshot import (
        CESnapshot,
        SystemSnapshot,
        SystemSnapshotter,
        take_snapshot,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestSystemSnapshot:
    def test_frozen_model(self):
        snap = SystemSnapshot(
            timestamp="2026-01-01T00:00:00",
            module_versions={"zephyr.test": "v1.0.0"},
            provenance_fingerprint="abc123",
            registry_hashes={"G1": "hash1"},
            blueprint_v12_pass_rate=0.95,
        )
        with pytest.raises(Exception):
            snap.timestamp = "changed"

    def test_fields(self):
        snap = SystemSnapshot(
            timestamp="2026-01-01T00:00:00",
            module_versions={"zephyr.test": "v1.0.0"},
            provenance_fingerprint="abc123",
            registry_hashes={"G1": "hash1"},
            blueprint_v12_pass_rate=0.95,
        )
        assert snap.timestamp == "2026-01-01T00:00:00"
        assert snap.module_versions == {"zephyr.test": "v1.0.0"}
        assert snap.provenance_fingerprint == "abc123"
        assert snap.registry_hashes == {"G1": "hash1"}
        assert snap.blueprint_v12_pass_rate == 0.95

    def test_pass_rate_sentinel(self):
        snap = SystemSnapshot(
            timestamp="2026-01-01T00:00:00",
            module_versions={},
            provenance_fingerprint="unavailable",
            registry_hashes={},
            blueprint_v12_pass_rate=-1.0,
        )
        assert snap.blueprint_v12_pass_rate == -1.0

    def test_pass_rate_boundary_validation(self):
        with pytest.raises(Exception):
            SystemSnapshot(
                timestamp="t",
                module_versions={},
                provenance_fingerprint="x",
                registry_hashes={},
                blueprint_v12_pass_rate=1.5,
            )


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestSystemSnapshotter:
    def test_capture_with_temp_dirs(self, tmp_path):
        snapshots_dir = tmp_path / "snapshots"
        gates_dir = tmp_path / "gates"
        db_path = tmp_path / "test.db"
        snapshots_dir.mkdir()
        gates_dir.mkdir()
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE gate_runs (gate_id TEXT, passed INTEGER)")
        conn.execute("INSERT INTO gate_runs VALUES ('G4-001', 1)")
        conn.execute("INSERT INTO gate_runs VALUES ('G4-002', 0)")
        conn.commit()
        conn.close()
        snapshotter = SystemSnapshotter(
            repo_root=tmp_path,
            snapshots_dir=snapshots_dir,
            db_path=db_path,
            gates_dir=gates_dir,
            module_manifests={"zephyr.test": "v1.0.0"},
        )
        snapshot, path = snapshotter.capture()
        assert isinstance(snapshot, SystemSnapshot)
        assert snapshot.module_versions == {"zephyr.test": "v1.0.0"}
        assert path is not None
        assert path.exists()

    def test_capture_no_db(self, tmp_path):
        snapshots_dir = tmp_path / "snapshots"
        gates_dir = tmp_path / "gates"
        db_path = tmp_path / "nonexistent.db"
        snapshots_dir.mkdir()
        gates_dir.mkdir()
        snapshotter = SystemSnapshotter(
            repo_root=tmp_path,
            snapshots_dir=snapshots_dir,
            db_path=db_path,
            gates_dir=gates_dir,
        )
        snapshot, _ = snapshotter.capture()
        assert snapshot.blueprint_v12_pass_rate == -1.0

    def test_capture_missing_gates_dir(self, tmp_path):
        snapshots_dir = tmp_path / "snapshots"
        db_path = tmp_path / "test.db"
        gates_dir = tmp_path / "no_gates"
        snapshots_dir.mkdir()
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE gate_runs (gate_id TEXT, passed INTEGER)")
        conn.commit()
        conn.close()
        snapshotter = SystemSnapshotter(
            repo_root=tmp_path,
            snapshots_dir=snapshots_dir,
            db_path=db_path,
            gates_dir=gates_dir,
        )
        snapshot, _ = snapshotter.capture()
        for v in snapshot.registry_hashes.values():
            assert v == "missing"

    def test_provenance_fingerprint_unavailable(self, tmp_path):
        snapshots_dir = tmp_path / "snapshots"
        gates_dir = tmp_path / "gates"
        db_path = tmp_path / "test.db"
        for d in [snapshots_dir, gates_dir]:
            d.mkdir()
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE gate_runs (gate_id TEXT, passed INTEGER)")
        conn.commit()
        conn.close()
        snapshotter = SystemSnapshotter(
            repo_root=tmp_path,
            snapshots_dir=snapshots_dir,
            db_path=db_path,
            gates_dir=gates_dir,
        )
        snapshot, _ = snapshotter.capture()
        assert snapshot.provenance_fingerprint == "unavailable"

    def test_run_in_build_classmethod(self, tmp_path):
        snapshots_dir = tmp_path / "snapshots"
        gates_dir = tmp_path / "gates"
        db_path = tmp_path / "test.db"
        for d in [snapshots_dir, gates_dir]:
            d.mkdir()
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE gate_runs (gate_id TEXT, passed INTEGER)")
        conn.commit()
        conn.close()
        snapshot, _ = SystemSnapshotter.run_in_build(
            repo_root=tmp_path,
            snapshots_dir=snapshots_dir,
            db_path=db_path,
        )
        assert isinstance(snapshot, SystemSnapshot)


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestCESnapshot:
    def test_defaults(self):
        snap = CESnapshot()
        assert snap.active_sessions == 0
        assert snap.vms_connected is False
        assert snap.ce_pipeline_stats == {}
        assert snap.memory_usage_mb == 0.0
        assert snap.timestamp == ""

    def test_frozen(self):
        snap = CESnapshot(active_sessions=5, vms_connected=True)
        with pytest.raises(Exception):
            snap.active_sessions = 10

    def test_custom_values(self):
        snap = CESnapshot(
            active_sessions=3,
            vms_connected=True,
            ce_pipeline_stats={"build_ms": 100.0},
            memory_usage_mb=256.0,
            timestamp="2026-05-22T10:00:00",
        )
        assert snap.active_sessions == 3
        assert snap.vms_connected is True
        assert snap.ce_pipeline_stats == {"build_ms": 100.0}
        assert snap.memory_usage_mb == 256.0


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestTakeSnapshot:
    def test_returns_ce_snapshot(self):
        snap = take_snapshot()
        assert isinstance(snap, CESnapshot)

    def test_snapshot_has_timestamp(self):
        snap = take_snapshot()
        assert len(snap.timestamp) > 0

    def test_snapshot_memory_non_negative(self):
        snap = take_snapshot()
        assert snap.memory_usage_mb >= 0.0
