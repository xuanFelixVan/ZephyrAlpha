# [A_test] module_id: MOD-GOV_concurrency_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §concurrency_guard
# [MODULE] tests.unit.test_concurrency_guard
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for concurrency_guard — 回滚并发安全守卫（方案C）。

Tests: scan_active_locks, check_rollback_conflict, classify_uncommitted_files.
覆盖场景：无锁/本session锁/其他session锁/过期锁/混合归属。
"""

import json
import time
from pathlib import Path

import pytest

from zephyr.infrastructure.runtime.concurrency_guard import (
    ConcurrencyConflictError,
    ConflictResult,
    LockInfo,
    StashPlan,
    check_rollback_conflict,
    classify_uncommitted_files,
    scan_active_locks,
)


def _write_registry(project_root: Path, locks: dict[str, dict]) -> None:
    """写入 .ailocks/registry.json。"""
    lock_dir = project_root / ".ailocks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    registry = {"locks": locks}
    (lock_dir / "registry.json").write_text(json.dumps(registry), encoding="utf-8")


def _make_lock_entry(owner: str, task: str = "", ts_offset: float = 0.0, pid: int = 1) -> dict:
    return {
        "owner_id": owner,
        "task": task,
        "timestamp": time.time() + ts_offset,
        "pid": pid,
    }


class TestScanActiveLocks:
    """scan_active_locks() — 扫描 .ailocks/registry.json 活跃锁"""

    def test_no_registry_returns_empty(self, tmp_path: Path):
        result = scan_active_locks(tmp_path)
        assert result == []

    def test_empty_registry_returns_empty(self, tmp_path: Path):
        _write_registry(tmp_path, {})
        result = scan_active_locks(tmp_path)
        assert result == []

    def test_returns_active_locks(self, tmp_path: Path):
        _write_registry(
            tmp_path,
            {
                "src/foo.py": _make_lock_entry("session-A", "task1"),
                "src/bar.py": _make_lock_entry("session-B", "task2"),
            },
        )
        result = scan_active_locks(tmp_path)
        assert len(result) == 2
        owners = {l.owner_id for l in result}
        assert owners == {"session-A", "session-B"}

    def test_filters_stale_locks(self, tmp_path: Path):
        _write_registry(
            tmp_path,
            {
                "src/fresh.py": _make_lock_entry("session-A", ts_offset=0.0),
                "src/stale.py": _make_lock_entry("session-B", ts_offset=-3600.0),
            },
        )
        result = scan_active_locks(tmp_path)
        assert len(result) == 1
        assert result[0].file_path == "src/fresh.py"

    def test_corrupt_registry_returns_empty(self, tmp_path: Path):
        lock_dir = tmp_path / ".ailocks"
        lock_dir.mkdir(parents=True)
        (lock_dir / "registry.json").write_text("not json", encoding="utf-8")
        result = scan_active_locks(tmp_path)
        assert result == []


class TestCheckRollbackConflict:
    """check_rollback_conflict() — 回滚文件与活跃锁冲突检测"""

    def test_no_locks_no_conflict(self, tmp_path: Path):
        result = check_rollback_conflict(["src/a.py"], "session-X", tmp_path)
        assert not result.has_conflict
        assert result.blocked_files == []

    def test_own_lock_not_conflict(self, tmp_path: Path):
        _write_registry(
            tmp_path,
            {
                "src/a.py": _make_lock_entry("session-X"),
            },
        )
        result = check_rollback_conflict(["src/a.py"], "session-X", tmp_path)
        assert not result.has_conflict

    def test_other_session_lock_is_conflict(self, tmp_path: Path):
        _write_registry(
            tmp_path,
            {
                "src/a.py": _make_lock_entry("session-OTHER"),
            },
        )
        result = check_rollback_conflict(["src/a.py"], "session-X", tmp_path)
        assert result.has_conflict
        assert "src/a.py" in result.blocked_files
        assert result.locked_by["src/a.py"] == "session-OTHER"

    def test_path_normalization_backslash(self, tmp_path: Path):
        _write_registry(
            tmp_path,
            {
                "src/a.py": _make_lock_entry("session-OTHER"),
            },
        )
        result = check_rollback_conflict(["src\\a.py"], "session-X", tmp_path)
        assert result.has_conflict

    def test_mixed_locks_partial_conflict(self, tmp_path: Path):
        _write_registry(
            tmp_path,
            {
                "src/a.py": _make_lock_entry("session-OTHER"),
                "src/b.py": _make_lock_entry("session-X"),
            },
        )
        result = check_rollback_conflict(["src/a.py", "src/b.py", "src/c.py"], "session-X", tmp_path)
        assert result.has_conflict
        assert result.blocked_files == ["src/a.py"]
        assert "src/b.py" not in result.blocked_files


class TestClassifyUncommittedFiles:
    """classify_uncommitted_files() — 未提交文件归属分类"""

    def test_no_locks_all_own(self, tmp_path: Path):
        result = classify_uncommitted_files(["a.py", "b.py"], "session-X", tmp_path)
        assert result.should_stash
        assert result.own_files == ["a.py", "b.py"]
        assert result.other_files == []

    def test_other_session_locked_goes_to_other(self, tmp_path: Path):
        _write_registry(
            tmp_path,
            {
                "a.py": _make_lock_entry("session-OTHER"),
            },
        )
        result = classify_uncommitted_files(["a.py", "b.py"], "session-X", tmp_path)
        assert "a.py" in result.other_files
        assert "b.py" in result.own_files
        assert result.other_owners["a.py"] == "session-OTHER"

    def test_own_lock_goes_to_own(self, tmp_path: Path):
        _write_registry(
            tmp_path,
            {
                "a.py": _make_lock_entry("session-X"),
            },
        )
        result = classify_uncommitted_files(["a.py"], "session-X", tmp_path)
        assert "a.py" in result.own_files
        assert result.other_files == []

    def test_empty_list(self, tmp_path: Path):
        result = classify_uncommitted_files([], "session-X", tmp_path)
        assert not result.should_stash
        assert result.own_files == []
        assert result.other_files == []


class TestConcurrencyConflictError:
    """ConcurrencyConflictError — 异常类格式化"""

    def test_error_message_contains_files(self):
        err = ConcurrencyConflictError(
            blocked_files=["a.py", "b.py"],
            locked_by={"a.py": "session-A", "b.py": "session-B"},
            reason="test",
        )
        msg = str(err)
        assert "a.py" in msg
        assert "session-A" in msg
        assert "test" in msg

    def test_error_attributes(self):
        err = ConcurrencyConflictError(["x.py"], {"x.py": "owner1"})
        assert err.blocked_files == ["x.py"]
        assert err.locked_by == {"x.py": "owner1"}
