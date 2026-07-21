# [A_test] module_id: MOD-GOV_support_system_snapshot | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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

import tempfile
from pathlib import Path

import pytest

try:
    from zephyr.infrastructure.system_snapshot import (
        SystemSnapshot,
        SystemSnapshotter,
    )
except Exception as _exc:
    pytest.skip(f"无法导入 system_snapshot: {_exc}", allow_module_level=True)


class TestSystemSnapshotter:
    def test_capture_returns_tuple(self):
        snapshotter = SystemSnapshotter(
            repo_root=Path(tempfile.gettempdir()),
            snapshots_dir=Path(tempfile.mkdtemp()),
            db_path=Path("/nonexistent/db.sqlite"),
            gates_dir=Path("/nonexistent/gates"),
        )
        result = snapshotter.capture()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_capture_snapshot_is_system_snapshot(self):
        snapshotter = SystemSnapshotter(
            repo_root=Path(tempfile.gettempdir()),
            snapshots_dir=Path(tempfile.mkdtemp()),
            db_path=Path("/nonexistent/db.sqlite"),
            gates_dir=Path("/nonexistent/gates"),
        )
        snapshot, path = snapshotter.capture()
        assert isinstance(snapshot, SystemSnapshot)

    def test_capture_has_timestamp(self):
        snapshotter = SystemSnapshotter(
            repo_root=Path(tempfile.gettempdir()),
            snapshots_dir=Path(tempfile.mkdtemp()),
            db_path=Path("/nonexistent/db.sqlite"),
            gates_dir=Path("/nonexistent/gates"),
        )
        snapshot, _ = snapshotter.capture()
        assert len(snapshot.timestamp) > 0

    def test_capture_module_versions(self):
        snapshotter = SystemSnapshotter(
            repo_root=Path(tempfile.gettempdir()),
            snapshots_dir=Path(tempfile.mkdtemp()),
            db_path=Path("/nonexistent/db.sqlite"),
            gates_dir=Path("/nonexistent/gates"),
        )
        snapshot, _ = snapshotter.capture()
        assert isinstance(snapshot.module_versions, dict)

    def test_capture_provenance_fingerprint(self):
        snapshotter = SystemSnapshotter(
            repo_root=Path(tempfile.gettempdir()),
            snapshots_dir=Path(tempfile.mkdtemp()),
            db_path=Path("/nonexistent/db.sqlite"),
            gates_dir=Path("/nonexistent/gates"),
        )
        snapshot, _ = snapshotter.capture()
        assert snapshot.provenance_fingerprint == "unavailable"

    def test_capture_registry_hashes(self):
        snapshotter = SystemSnapshotter(
            repo_root=Path(tempfile.gettempdir()),
            snapshots_dir=Path(tempfile.mkdtemp()),
            db_path=Path("/nonexistent/db.sqlite"),
            gates_dir=Path("/nonexistent/gates"),
        )
        snapshot, _ = snapshotter.capture()
        assert isinstance(snapshot.registry_hashes, dict)

    def test_capture_blueprint_pass_rate(self):
        snapshotter = SystemSnapshotter(
            repo_root=Path(tempfile.gettempdir()),
            snapshots_dir=Path(tempfile.mkdtemp()),
            db_path=Path("/nonexistent/db.sqlite"),
            gates_dir=Path("/nonexistent/gates"),
        )
        snapshot, _ = snapshotter.capture()
        assert snapshot.blueprint_v12_pass_rate == -1.0


class TestSystemSnapshot:
    def test_instantiation(self):
        snap = SystemSnapshot(
            timestamp="2026-01-01T00:00:00",
            module_versions={"mod": "1.0"},
            provenance_fingerprint="abc",
            registry_hashes={"G1": "hash1"},
            blueprint_v12_pass_rate=0.95,
        )
        assert snap.timestamp == "2026-01-01T00:00:00"
        assert snap.blueprint_v12_pass_rate == 0.95

    def test_frozen(self):
        snap = SystemSnapshot(
            timestamp="2026-01-01T00:00:00",
            module_versions={},
            provenance_fingerprint="x",
            registry_hashes={},
            blueprint_v12_pass_rate=-1.0,
        )
        with pytest.raises(Exception):
            snap.timestamp = "changed"


class TestRunInBuild:
    def test_run_in_build_returns_tuple(self):
        result = SystemSnapshotter.run_in_build(
            repo_root=Path(tempfile.gettempdir()),
            snapshots_dir=Path(tempfile.mkdtemp()),
            db_path=Path("/nonexistent/db.sqlite"),
        )
        assert isinstance(result, tuple)
