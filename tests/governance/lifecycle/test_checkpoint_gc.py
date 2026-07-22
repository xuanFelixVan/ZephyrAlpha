# [A_test] module_id: MOD-GOV_checkpoint_gc | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §6.2
# [MODULE] tests.test_checkpoint_gc
# [INVARIANTS] knowngoodstate快照不可清
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
import os
import time

from zephyr.infrastructure.rollback.checkpoint_gc import CheckpointGC, GCResult


class TestCheckpointGCInstantiation:
    def test_creates_instance_with_default_root(self):
        gc = CheckpointGC()
        assert isinstance(gc, CheckpointGC)

    def test_creates_instance_with_custom_root(self, tmp_path):
        gc = CheckpointGC(project_root=tmp_path)
        assert gc._project_root == tmp_path

    def test_dump_dir_set_correctly(self, tmp_path):
        gc = CheckpointGC(project_root=tmp_path)
        assert gc._dump_dir == tmp_path / CheckpointGC.DUMP_DIR


class TestCollect:
    def test_collect_empty_dir(self, tmp_path):
        gc = CheckpointGC(project_root=tmp_path)
        result = gc.collect()
        assert isinstance(result, GCResult)
        assert result.total_before == 0
        assert result.total_after == 0
        assert result.deleted == []

    def test_collect_nonexistent_dir(self, tmp_path):
        gc = CheckpointGC(project_root=tmp_path / "nonexistent")
        result = gc.collect()
        assert result.total_before == 0
        assert result.total_after == 0

    def test_collect_deletes_expired_snapshots(self, tmp_path):
        dump_dir = tmp_path / CheckpointGC.DUMP_DIR
        dump_dir.mkdir(parents=True, exist_ok=True)

        old_file = dump_dir / "abc1234.jsonl"
        old_file.write_text("data", encoding="utf-8")
        old_age = time.time() - (91 * 86400)
        os.utime(old_file, (old_age, old_age))

        gc = CheckpointGC(project_root=tmp_path)
        result = gc.collect()
        assert result.total_before == 1
        assert result.total_after == 0
        assert old_file.name in result.deleted

    def test_collect_preserves_recent_snapshots(self, tmp_path):
        dump_dir = tmp_path / CheckpointGC.DUMP_DIR
        dump_dir.mkdir(parents=True, exist_ok=True)

        recent_file = dump_dir / "def5678.jsonl"
        recent_file.write_text("data", encoding="utf-8")

        gc = CheckpointGC(project_root=tmp_path)
        result = gc.collect()
        assert result.total_before == 1
        assert result.total_after == 1
        assert result.deleted == []

    def test_collect_preserves_known_good_snapshots(self, tmp_path):
        dump_dir = tmp_path / CheckpointGC.DUMP_DIR
        dump_dir.mkdir(parents=True, exist_ok=True)

        ledger_dir = tmp_path / ".zephyr"
        ledger_dir.mkdir(parents=True, exist_ok=True)
        ledger_path = ledger_dir / "knowngoodstate_ledger.jsonl"

        commit_sha = "aaa1111"
        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"commit_sha": commit_sha}) + "\n")

        old_file = dump_dir / f"{commit_sha}.jsonl"
        old_file.write_text("data", encoding="utf-8")
        old_age = time.time() - (91 * 86400)
        os.utime(old_file, (old_age, old_age))

        gc = CheckpointGC(project_root=tmp_path)
        result = gc.collect()
        assert result.total_before == 1
        assert result.total_after == 1
        assert commit_sha in result.preserved_known_good

    def test_collect_excess_snapshots_deleted(self, tmp_path):
        dump_dir = tmp_path / CheckpointGC.DUMP_DIR
        dump_dir.mkdir(parents=True, exist_ok=True)

        for i in range(105):
            f = dump_dir / f"snap{i:04d}.jsonl"
            f.write_text("data", encoding="utf-8")

        gc = CheckpointGC(project_root=tmp_path)
        result = gc.collect()
        assert result.total_before == 105
        assert result.total_after <= CheckpointGC.MAX_SNAPSHOTS


class TestGetKnownGoodCommits:
    def test_no_ledger_returns_empty(self, tmp_path):
        gc = CheckpointGC(project_root=tmp_path)
        commits = gc._get_known_good_commits()
        assert commits == []

    def test_reads_ledger_correctly(self, tmp_path):
        ledger_dir = tmp_path / ".zephyr"
        ledger_dir.mkdir(parents=True, exist_ok=True)
        ledger_path = ledger_dir / "knowngoodstate_ledger.jsonl"

        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"commit_sha": "sha1aaa"}) + "\n")
            f.write(json.dumps({"commit_sha": "sha2bbb"}) + "\n")

        gc = CheckpointGC(project_root=tmp_path)
        commits = gc._get_known_good_commits()
        assert commits == ["sha1aaa", "sha2bbb"]

    def test_handles_malformed_json(self, tmp_path):
        ledger_dir = tmp_path / ".zephyr"
        ledger_dir.mkdir(parents=True, exist_ok=True)
        ledger_path = ledger_dir / "knowngoodstate_ledger.jsonl"

        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write("not json\n")
            f.write(json.dumps({"commit_sha": "validsha"}) + "\n")
            f.write(json.dumps({"wrong_key": "oops"}) + "\n")

        gc = CheckpointGC(project_root=tmp_path)
        commits = gc._get_known_good_commits()
        assert commits == ["validsha"]
