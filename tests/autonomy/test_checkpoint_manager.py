# [A_test] module_id: MOD-GOV_checkpoint_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §

# [MODULE] tests.test_checkpoint_manager

# [INVARIANTS] Checkpoint round-trip: save then restore yields identical object

# [MODIFY-GUARD] source change only

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] restore returns None for missing id

# [TESTS] python -m pytest tests/test_checkpoint_manager.py -q
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.autonomy_core.context.checkpoint_manager import Checkpoint, CheckpointManager


class TestCheckpoint:
    def test_instantiation(self):
        ckpt = Checkpoint(
            id="ckpt-001",
            context_snapshot="snapshot-data",
            ke_ids=["KE-01", "KE-02"],
            token_count=128,
        )
        assert ckpt.id == "ckpt-001"
        assert ckpt.context_snapshot == "snapshot-data"
        assert ckpt.ke_ids == ["KE-01", "KE-02"]
        assert ckpt.token_count == 128

    def test_instantiation_empty_fields(self):
        ckpt = Checkpoint(id="", context_snapshot="", ke_ids=[], token_count=0)
        assert ckpt.id == ""
        assert ckpt.context_snapshot == ""
        assert ckpt.ke_ids == []
        assert ckpt.token_count == 0

    def test_instantiation_none_snapshot_accepted(self):
        ckpt = Checkpoint(id="x", context_snapshot=None, ke_ids=[], token_count=0)
        assert ckpt.context_snapshot is None

    def test_dict_round_trip(self):
        ckpt = Checkpoint(
            id="ckpt-dict",
            context_snapshot="abc",
            ke_ids=["K1"],
            token_count=42,
        )
        serialized = ckpt.__dict__
        restored = Checkpoint(**serialized)
        assert restored == ckpt


class TestCheckpointManager:
    def test_instantiation_creates_dir(self, tmp_path):
        store = tmp_path / "my_checkpoints"
        mgr = CheckpointManager(store_dir=store)
        assert store.is_dir()

    def test_instantiation_default_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mgr = CheckpointManager()
        assert (tmp_path / ".ce_checkpoints").is_dir()

    def test_save_returns_path(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        ckpt = Checkpoint(id="save-1", context_snapshot="s", ke_ids=[], token_count=0)
        result = mgr.save(ckpt)
        assert Path(result).exists()
        assert result.endswith("save-1.json")

    def test_save_persist_json(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        ckpt = Checkpoint(
            id="persist-1",
            context_snapshot="hello",
            ke_ids=["KE-A", "KE-B"],
            token_count=99,
        )
        mgr.save(ckpt)
        data = json.loads((tmp_path / "store" / "persist-1.json").read_text(encoding="utf-8"))
        assert data["id"] == "persist-1"
        assert data["context_snapshot"] == "hello"
        assert data["ke_ids"] == ["KE-A", "KE-B"]
        assert data["token_count"] == 99

    def test_save_overwrite_existing(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        ckpt_v1 = Checkpoint(id="ov", context_snapshot="v1", ke_ids=[], token_count=1)
        ckpt_v2 = Checkpoint(id="ov", context_snapshot="v2", ke_ids=["K"], token_count=2)
        mgr.save(ckpt_v1)
        mgr.save(ckpt_v2)
        restored = mgr.restore("ov")
        assert restored is not None
        assert restored.context_snapshot == "v2"
        assert restored.ke_ids == ["K"]
        assert restored.token_count == 2

    def test_restore_existing(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        ckpt = Checkpoint(
            id="restore-1",
            context_snapshot="world",
            ke_ids=["KE-X"],
            token_count=7,
        )
        mgr.save(ckpt)
        restored = mgr.restore("restore-1")
        assert restored is not None
        assert restored.id == ckpt.id
        assert restored.context_snapshot == ckpt.context_snapshot
        assert restored.ke_ids == ckpt.ke_ids
        assert restored.token_count == ckpt.token_count

    def test_restore_missing_returns_none(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        result = mgr.restore("nonexistent-id")
        assert result is None

    def test_restore_empty_id_returns_none(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        result = mgr.restore("")
        assert result is None

    def test_round_trip_unicode(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        ckpt = Checkpoint(
            id="unicode-1",
            context_snapshot="中文快照 🚀",
            ke_ids=["KE-日本語"],
            token_count=256,
        )
        mgr.save(ckpt)
        restored = mgr.restore("unicode-1")
        assert restored is not None
        assert restored.context_snapshot == "中文快照 🚀"
        assert restored.ke_ids == ["KE-日本語"]

    def test_round_trip_large_ke_ids(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        ke_ids = [f"KE-{i:04d}" for i in range(1000)]
        ckpt = Checkpoint(
            id="large",
            context_snapshot="big",
            ke_ids=ke_ids,
            token_count=99999,
        )
        mgr.save(ckpt)
        restored = mgr.restore("large")
        assert restored is not None
        assert len(restored.ke_ids) == 1000
        assert restored.ke_ids[0] == "KE-0000"
        assert restored.ke_ids[-1] == "KE-0999"

    def test_save_with_path_object(self, tmp_path):
        mgr = CheckpointManager(store_dir=Path(tmp_path) / "pathobj")
        ckpt = Checkpoint(id="pobj", context_snapshot="x", ke_ids=[], token_count=1)
        result = mgr.save(ckpt)
        assert Path(result).exists()

    def test_multiple_checkpoints_independent(self, tmp_path):
        mgr = CheckpointManager(store_dir=tmp_path / "store")
        ckpt_a = Checkpoint(id="a", context_snapshot="A", ke_ids=[], token_count=10)
        ckpt_b = Checkpoint(id="b", context_snapshot="B", ke_ids=["K"], token_count=20)
        mgr.save(ckpt_a)
        mgr.save(ckpt_b)
        restored_a = mgr.restore("a")
        restored_b = mgr.restore("b")
        assert restored_a is not None and restored_b is not None
        assert restored_a.context_snapshot == "A"
        assert restored_b.context_snapshot == "B"
        assert restored_a.token_count == 10
        assert restored_b.token_count == 20
