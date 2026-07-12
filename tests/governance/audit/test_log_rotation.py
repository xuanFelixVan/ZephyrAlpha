# [A_test] module_id: SRC-TST-1242 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_log_rotation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zephyr.gov_audit.log_rotation import (
    LogRotationManager,
    RotatedLogInfo,
    RotationRecord,
)


class TestLogRotationManagerInit:
    def test_creates_data_dir(self, tmp_path):
        data_dir = tmp_path / "audit_test"
        manager = LogRotationManager(data_dir=data_dir)
        assert data_dir.exists()

    def test_default_compress(self, tmp_path):
        manager = LogRotationManager(data_dir=tmp_path / "r1")
        assert manager._compress_rotated is True

    def test_custom_max_days(self, tmp_path):
        manager = LogRotationManager(data_dir=tmp_path / "r2", max_rotated_days=30)
        assert manager._max_rotated_days == 30


class TestRotate:
    def test_no_active_log_returns_none(self, tmp_path):
        manager = LogRotationManager(data_dir=tmp_path / "r3")
        result = manager.rotate()
        assert result is None

    def test_empty_active_log_returns_none(self, tmp_path):
        data_dir = tmp_path / "r4"
        data_dir.mkdir()
        (data_dir / "events.jsonl").write_text("", encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir)
        result = manager.rotate(force=True)
        assert result is None

    def test_rotate_creates_rotated_file(self, tmp_path):
        data_dir = tmp_path / "r5"
        data_dir.mkdir()
        active = data_dir / "events.jsonl"
        active.write_text('{"event": "test"}\n', encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir, compress_rotated=False)
        result = manager.rotate(force=True)
        assert isinstance(result, RotationRecord)
        assert result.entries_rotated == 1
        assert result.compressed is False
        rotated_files = list(data_dir.glob("audit-trail-*"))
        assert len(rotated_files) >= 1

    def test_rotate_with_compression(self, tmp_path):
        data_dir = tmp_path / "r6"
        data_dir.mkdir()
        active = data_dir / "events.jsonl"
        active.write_text('{"event": "test"}\n', encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir, compress_rotated=True)
        result = manager.rotate(force=True)
        assert result is not None
        assert result.compressed is True
        gz_files = list(data_dir.glob("*.gz"))
        assert len(gz_files) >= 1

    def test_rotate_creates_new_active_log(self, tmp_path):
        data_dir = tmp_path / "r7"
        data_dir.mkdir()
        active = data_dir / "events.jsonl"
        active.write_text('{"event": "test"}\n', encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir, compress_rotated=False)
        manager.rotate(force=True)
        assert active.exists()

    def test_no_double_rotation_same_day(self, tmp_path):
        data_dir = tmp_path / "r8"
        data_dir.mkdir()
        active = data_dir / "events.jsonl"
        active.write_text('{"event": "test"}\n', encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir, compress_rotated=False)
        first = manager.rotate(force=True)
        active.write_text('{"event": "test2"}\n', encoding="utf-8")
        second = manager.rotate(force=False)
        assert first is not None
        assert second is None


class TestGetRotatedLogs:
    def test_no_rotated_logs(self, tmp_path):
        manager = LogRotationManager(data_dir=tmp_path / "r9")
        logs = manager.get_rotated_logs()
        assert logs == []

    def test_lists_rotated_logs(self, tmp_path):
        data_dir = tmp_path / "r10"
        data_dir.mkdir()
        active = data_dir / "events.jsonl"
        active.write_text('{"event": "test"}\n', encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir, compress_rotated=False)
        manager.rotate(force=True)
        logs = manager.get_rotated_logs()
        assert len(logs) >= 1
        assert isinstance(logs[0], RotatedLogInfo)


class TestCleanupOldRotations:
    def test_deletes_old_files(self, tmp_path):
        data_dir = tmp_path / "r11"
        data_dir.mkdir()
        old_date = (datetime.now(UTC) - timedelta(days=100)).strftime("%Y-%m-%d")
        old_file = data_dir / f"audit-trail-{old_date}.jsonl"
        old_file.write_text('{"old": true}\n', encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir, max_rotated_days=90)
        deleted = manager.cleanup_old_rotations()
        assert deleted == 1
        assert not old_file.exists()

    def test_keeps_recent_files(self, tmp_path):
        data_dir = tmp_path / "r12"
        data_dir.mkdir()
        recent_date = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")
        recent_file = data_dir / f"audit-trail-{recent_date}.jsonl"
        recent_file.write_text('{"recent": true}\n', encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir, max_rotated_days=90)
        deleted = manager.cleanup_old_rotations()
        assert deleted == 0
        assert recent_file.exists()


class TestExtractDate:
    def test_valid_filename(self):
        result = LogRotationManager._extract_date("audit-trail-2026-05-22.jsonl")
        assert result == "2026-05-22"

    def test_compressed_filename(self):
        result = LogRotationManager._extract_date("audit-trail-2026-05-22.jsonl.gz")
        assert result == "2026-05-22"

    def test_invalid_filename(self):
        result = LogRotationManager._extract_date("random.txt")
        assert result is None
