# [A_test] module_id: SRC-TST-1581 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-429 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.test_session_concurrency
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

from __future__ import annotations

import os
import tempfile

import pytest

from zephyr.security.access_control.session_concurrency import (
    CONFLICT_SCENARIOS,
    LOCK_TTL_SECONDS,
    ConflictType,
    ConcurrencyManager,
    LockLevel,
    ZephyrLock,
    detect_mtime_conflict,
)


class TestLockLevel:
    def test_enum_values(self):
        assert LockLevel.EXCLUSIVE == "EXCLUSIVE"

    def test_enum_members_count(self):
        assert len(LockLevel) == 1


class TestConflictType:
    def test_enum_values(self):
        assert ConflictType.SAME_FILE == "two_sessions_same_file"
        assert ConflictType.IMPORT_DEP == "import_dependency_change"
        assert ConflictType.REFACTOR_SIG == "refactor_signature_mismatch"
        assert ConflictType.BLUEPRINT_DRIFT == "blueprint_vs_construction"

    def test_conflict_scenarios_covered(self):
        for ct in ConflictType:
            assert ct in CONFLICT_SCENARIOS


class TestZephyrLock:
    def test_initial_state(self):
        lock = ZephyrLock(file_path="/test/file.py")
        assert lock.file_path == "/test/file.py"
        assert lock.acquired is False
        assert lock.is_active is False

    def test_acquire(self):
        lock = ZephyrLock(file_path="/test/file.py")
        result = lock.acquire()
        assert result is True
        assert lock.acquired is True
        assert lock.is_active is True

    def test_release(self):
        lock = ZephyrLock(file_path="/test/file.py")
        lock.acquire()
        result = lock.release()
        assert result is True
        assert lock.acquired is False
        assert lock.is_active is False


class TestConcurrencyManager:
    def test_no_conflict_when_no_locks(self):
        mgr = ConcurrencyManager()
        result = mgr.check_conflict("/test/file.py", "session-1")
        assert result is None

    def test_conflict_when_active_lock(self):
        mgr = ConcurrencyManager()
        mgr.pre_allocate(["/test/file.py"], "session-1")
        result = mgr.check_conflict("/test/file.py", "session-2")
        assert result == ConflictType.SAME_FILE

    def test_pre_allocate(self):
        mgr = ConcurrencyManager()
        allocated = mgr.pre_allocate(["/a.py", "/b.py"], "session-1")
        assert len(allocated) == 2

    def test_pre_allocate_skips_locked(self):
        mgr = ConcurrencyManager()
        mgr.pre_allocate(["/a.py"], "session-1")
        allocated = mgr.pre_allocate(["/a.py", "/b.py"], "session-2")
        assert len(allocated) == 1
        assert "/b.py" in allocated

    def test_resolve_conflict_same_file(self):
        mgr = ConcurrencyManager()
        result = mgr.resolve_conflict(ConflictType.SAME_FILE, ("/a.py", "/b.py"))
        assert result == "auto_merge"

    def test_resolve_conflict_other(self):
        mgr = ConcurrencyManager()
        result = mgr.resolve_conflict(ConflictType.IMPORT_DEP, ("/a.py", "/b.py"))
        assert result == "owner_decision"


class TestDetectMtimeConflict:
    def test_no_conflict_when_file_unchanged(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(b"test")
            path = f.name
        try:
            mtime = os.path.getmtime(path)
            assert detect_mtime_conflict(path, mtime) is False
        finally:
            os.unlink(path)

    def test_conflict_when_file_modified(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(b"test")
            path = f.name
        try:
            old_mtime = os.path.getmtime(path) - 100
            assert detect_mtime_conflict(path, old_mtime) is True
        finally:
            os.unlink(path)

    def test_nonexistent_file_returns_false(self):
        assert detect_mtime_conflict("/nonexistent/file.py", 0.0) is False


class TestLockTTL:
    def test_ttl_value(self):
        assert LOCK_TTL_SECONDS == 1800
        assert isinstance(LOCK_TTL_SECONDS, int)
