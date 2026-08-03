# [A_test] module_id: MOD-GOV_gov_session_concurrency | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-390 | docs/03_modules/_domain_governance/blueprint.md | §test
# [MODULE] tests.test_gov_session_concurrency
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] ZephyrLock状态机正确;ConcurrencyManager冲突检测完整
# [MODIFY-GUARD] src/zephyr/governance/session_concurrency.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_gov_session_concurrency.py
# [TTL] task_bound

from __future__ import annotations

import os
import tempfile

import pytest

sc_mod = pytest.importorskip("zephyr.security.access_control.session_concurrency")
LockLevel = sc_mod.LockLevel
ConflictType = sc_mod.ConflictType
CONFLICT_SCENARIOS = sc_mod.CONFLICT_SCENARIOS
LOCK_TTL_SECONDS = sc_mod.LOCK_TTL_SECONDS
ZephyrLock = sc_mod.ZephyrLock
ConcurrencyManager = sc_mod.ConcurrencyManager
detect_mtime_conflict = sc_mod.detect_mtime_conflict


class TestLockLevel:
    def test_exclusive_value(self):
        assert LockLevel.EXCLUSIVE.value == "EXCLUSIVE"

    def test_member_count(self):
        assert len(LockLevel) == 1

    def test_is_str_enum(self):
        assert isinstance(LockLevel.EXCLUSIVE, str)


class TestConflictType:
    def test_all_values(self):
        assert ConflictType.SAME_FILE.value == "two_sessions_same_file"
        assert ConflictType.IMPORT_DEP.value == "import_dependency_change"
        assert ConflictType.REFACTOR_SIG.value == "refactor_signature_mismatch"
        assert ConflictType.BLUEPRINT_DRIFT.value == "blueprint_vs_construction"

    def test_member_count(self):
        assert len(ConflictType) == 4

    def test_is_str_enum(self):
        assert isinstance(ConflictType.SAME_FILE, str)


class TestConflictScenarios:
    def test_all_types_have_descriptions(self):
        for ct in ConflictType:
            assert ct in CONFLICT_SCENARIOS, f"Missing scenario for {ct}"

    def test_descriptions_are_nonempty(self):
        for ct, desc in CONFLICT_SCENARIOS.items():
            assert len(desc) > 0, f"Empty description for {ct}"


class TestLockTtlSeconds:
    def test_is_positive(self):
        assert LOCK_TTL_SECONDS > 0

    def test_is_integer(self):
        assert isinstance(LOCK_TTL_SECONDS, int)


class TestZephyrLock:
    def test_create_default(self):
        lock = ZephyrLock(file_path="test.py")
        assert lock.file_path == "test.py"
        assert lock.session_id == ""
        assert lock.acquired is False

    def test_create_with_session(self):
        lock = ZephyrLock(file_path="test.py", session_id="s-1", acquired=True)
        assert lock.session_id == "s-1"
        assert lock.acquired is True

    def test_acquire(self):
        lock = ZephyrLock(file_path="test.py")
        result = lock.acquire()
        assert result is True
        assert lock.acquired is True
        assert lock.is_active is True

    def test_release(self):
        lock = ZephyrLock(file_path="test.py", acquired=True)
        result = lock.release()
        assert result is True
        assert lock.acquired is False
        assert lock.is_active is False

    def test_is_active_reflects_state(self):
        lock = ZephyrLock(file_path="test.py")
        assert lock.is_active is False
        lock.acquire()
        assert lock.is_active is True
        lock.release()
        assert lock.is_active is False


class TestConcurrencyManager:
    def test_create_default(self):
        cm = ConcurrencyManager()
        assert cm.active_locks == {}

    def test_check_conflict_no_lock(self):
        cm = ConcurrencyManager()
        result = cm.check_conflict("test.py", "s-1")
        assert result is None

    def test_check_conflict_with_active_lock(self):
        cm = ConcurrencyManager()
        cm.active_locks["test.py"] = ZephyrLock(file_path="test.py", session_id="s-1", acquired=True)
        result = cm.check_conflict("test.py", "s-2")
        assert result == ConflictType.SAME_FILE

    def test_check_conflict_with_released_lock(self):
        cm = ConcurrencyManager()
        lock = ZephyrLock(file_path="test.py", session_id="s-1", acquired=True)
        lock.release()
        cm.active_locks["test.py"] = lock
        result = cm.check_conflict("test.py", "s-2")
        assert result is None

    def test_pre_allocate_empty_list(self):
        cm = ConcurrencyManager()
        result = cm.pre_allocate([], "s-1")
        assert result == []

    def test_pre_allocate_new_paths(self):
        cm = ConcurrencyManager()
        result = cm.pre_allocate(["a.py", "b.py"], "s-1")
        assert "a.py" in result
        assert "b.py" in result
        assert cm.active_locks["a.py"].is_active is True
        assert cm.active_locks["a.py"].session_id == "s-1"

    def test_pre_allocate_skips_locked(self):
        cm = ConcurrencyManager()
        cm.active_locks["a.py"] = ZephyrLock(file_path="a.py", session_id="s-1", acquired=True)
        result = cm.pre_allocate(["a.py", "b.py"], "s-2")
        assert "a.py" not in result
        assert "b.py" in result

    def test_resolve_conflict_same_file(self):
        cm = ConcurrencyManager()
        result = cm.resolve_conflict(ConflictType.SAME_FILE, ("a.py", "b.py"))
        assert result == "auto_merge"

    def test_resolve_conflict_other_types(self):
        cm = ConcurrencyManager()
        result = cm.resolve_conflict(ConflictType.IMPORT_DEP, ("a.py", "b.py"))
        assert result == "owner_decision"

    def test_resolve_conflict_blueprint_drift(self):
        cm = ConcurrencyManager()
        result = cm.resolve_conflict(ConflictType.BLUEPRINT_DRIFT, ("a.py", "b.py"))
        assert result == "owner_decision"


class TestDetectMtimeConflict:
    def test_no_conflict_when_unchanged(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
            f.write("test")
            path = f.name
        try:
            mtime = os.path.getmtime(path)
            assert detect_mtime_conflict(path, mtime) is False
        finally:
            os.unlink(path)

    def test_conflict_when_modified(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
            f.write("original")
            path = f.name
        try:
            old_mtime = os.path.getmtime(path) - 100
            assert detect_mtime_conflict(path, old_mtime) is True
        finally:
            os.unlink(path)

    def test_nonexistent_file_returns_false(self):
        result = detect_mtime_conflict("nonexistent_file_12345.py", 0.0)
        assert result is False
