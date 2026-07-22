# [A_test] module_id: MOD-GOV_rollback_wal | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_rollback_wal
# [INVARIANTS] EXIT_CODE_WAL_INCOMPLETE=45; WAL_FILE=.zephyr/rollback_wal.jsonl
# [MODIFY-GUARD] Do not change test data without updating source module
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] All public methods return dataclass/primitive results even on file errors
# [TESTS] pytest tests/test_rollback_wal.py -q
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.rollback_wal import (
    RollbackWAL,
    WALEntry,
)


@pytest.fixture
def wal_dir(tmp_path):
    return tmp_path


@pytest.fixture
def wal(wal_dir):
    return RollbackWAL(project_root=wal_dir)


class TestInstantiation:
    def test_custom_root(self, wal_dir):
        w = RollbackWAL(project_root=wal_dir)
        assert w._project_root == wal_dir

    def test_none_root_defaults_to_cwd(self):
        w = RollbackWAL(project_root=None)
        assert w._project_root == Path.cwd()

    def test_wal_path_set(self, wal_dir):
        w = RollbackWAL(project_root=wal_dir)
        assert w._wal_path == wal_dir / ".zephyr" / "rollback_wal.jsonl"


class TestWriteAhead:
    def test_creates_entry_and_file(self, wal, wal_dir):
        entry = wal.write_ahead(
            operation="git_revert",
            from_commit="aaa1111",
            to_commit="bbb2222",
            files=["src/main.py", "config.yaml"],
        )
        assert isinstance(entry, WALEntry)
        assert entry.operation == "git_revert"
        assert entry.from_commit == "aaa1111"
        assert entry.to_commit == "bbb2222"
        assert entry.files == ["src/main.py", "config.yaml"]
        assert entry.status == "PENDING"
        assert entry.entry_id.startswith("WAL-")
        assert entry.written_at != ""

        wal_file = wal_dir / ".zephyr" / "rollback_wal.jsonl"
        assert wal_file.exists()
        lines = wal_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["operation"] == "git_revert"

    def test_empty_files_list(self, wal):
        entry = wal.write_ahead(
            operation="db_rebuild",
            from_commit="ccc",
            to_commit="ddd",
            files=[],
        )
        assert entry.files == []

    def test_multiple_entries_appended(self, wal, wal_dir):
        wal.write_ahead("op1", "a", "b", ["f1"])
        wal.write_ahead("op2", "c", "d", ["f2"])
        wal_file = wal_dir / ".zephyr" / "rollback_wal.jsonl"
        lines = wal_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2


class TestMarkComplete:
    def test_mark_existing_entry(self, wal):
        entry = wal.write_ahead("git_revert", "a", "b", ["f1"])
        result = wal.mark_complete(entry.entry_id)
        assert result is True
        entries = wal._read_all()
        assert entries[0]["status"] == "COMPLETE"
        assert "completed_at" in entries[0]

    def test_mark_nonexistent_entry(self, wal):
        result = wal.mark_complete("WAL-NONEXISTENT")
        assert result is False

    def test_mark_when_no_wal_file(self, wal_dir):
        w = RollbackWAL(project_root=wal_dir)
        result = w.mark_complete("anything")
        assert result is False


class TestCheckIncomplete:
    def test_all_complete(self, wal):
        entry = wal.write_ahead("op1", "a", "b", ["f1"])
        wal.mark_complete(entry.entry_id)
        status = wal.check_incomplete()
        assert status.complete is True
        assert status.pending_count == 0
        assert status.exit_code == 0

    def test_pending_entries(self, wal):
        for i in range(4):
            wal.write_ahead(f"op{i}", "a", "b", ["f"])
        status = wal.check_incomplete()
        assert status.complete is False
        assert status.pending_count == 4
        assert status.exit_code == 45

    def test_few_pending_no_exit_code(self, wal):
        wal.write_ahead("op1", "a", "b", ["f"])
        status = wal.check_incomplete()
        assert status.complete is False
        assert status.pending_count == 1
        assert status.exit_code == 0

    def test_empty_wal(self, wal_dir):
        w = RollbackWAL(project_root=wal_dir)
        status = w.check_incomplete()
        assert status.complete is True
        assert status.entry_count == 0
        assert status.pending_count == 0

    def test_oldest_pending_populated(self, wal):
        e1 = wal.write_ahead("op1", "a", "b", ["f1"])
        wal.write_ahead("op2", "c", "d", ["f2"])
        status = wal.check_incomplete()
        assert status.oldest_pending == e1.written_at


class TestGetReverseOperation:
    def test_existing_entry(self, wal):
        entry = wal.write_ahead("git_revert", "aaa", "bbb", ["f1", "f2"])
        reverse = wal.get_reverse_operation(entry.entry_id)
        assert reverse is not None
        assert reverse["operation"] == "reverse_git_revert"
        assert reverse["from_commit"] == "bbb"
        assert reverse["to_commit"] == "aaa"
        assert reverse["files"] == ["f1", "f2"]

    def test_nonexistent_entry(self, wal):
        result = wal.get_reverse_operation("WAL-FAKE")
        assert result is None

    def test_empty_wal(self, wal_dir):
        w = RollbackWAL(project_root=wal_dir)
        result = w.get_reverse_operation("anything")
        assert result is None


class TestReadAll:
    def test_corrupt_line_skipped(self, wal, wal_dir):
        wal.write_ahead("op1", "a", "b", ["f1"])
        wal_file = wal_dir / ".zephyr" / "rollback_wal.jsonl"
        with open(wal_file, "a", encoding="utf-8") as f:
            f.write("NOT JSON\n")
        wal.write_ahead("op2", "c", "d", ["f2"])
        entries = wal._read_all()
        assert len(entries) == 2

    def test_no_wal_file(self, wal_dir):
        w = RollbackWAL(project_root=wal_dir)
        entries = w._read_all()
        assert entries == []


class TestConstants:
    def test_exit_code(self):
        assert RollbackWAL.EXIT_CODE_WAL_INCOMPLETE == 45

    def test_wal_file_path(self):
        assert RollbackWAL.WAL_FILE == ".zephyr/rollback_wal.jsonl"
