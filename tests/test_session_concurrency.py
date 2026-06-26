# [A_test] module_id: SRC-TST-1581 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-429 | docs/03_modules/_domain_governance/blueprint.md | §
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

from zephyr.security.access_control.session_concurrency import (
    CONFLICT_SCENARIOS,
    LOCK_TTL_SECONDS,
    ConcurrencyManager,
    ConflictType,
    LockLevel,
    SessionConflictDetector,
    SessionRegistry,
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


class TestSessionRegistryClaimRelease:
    """SessionRegistry claim_file/release_file/get_session 测试（P2-SES 扩展）。"""

    def test_claim_file_auto_registers_unknown_session(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.claim_file("sess-A", str(tmp_path / "a.py")) is True
        info = reg.get_session("sess-A")
        assert info is not None and len(info.held_files) == 1

    def test_claim_file_idempotent_same_session(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.claim_file("sess-A", str(tmp_path / "a.py"))
        assert reg.claim_file("sess-A", str(tmp_path / "a.py")) is True  # 幂等
        info = reg.get_session("sess-A")
        assert len(info.held_files) == 1  # 不重复

    def test_claim_file_conflict_other_session_returns_false(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.claim_file("sess-A", str(tmp_path / "a.py"))
        assert reg.claim_file("sess-B", str(tmp_path / "a.py")) is False  # 不覆盖
        # sess-B 应被懒注册但 held_files 为空
        info_b = reg.get_session("sess-B")
        assert info_b is not None and len(info_b.held_files) == 0

    def test_claim_file_path_normalization(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.claim_file("sess-A", "a.py")  # 相对路径
        # 用绝对路径查应命中
        holder = reg.find_session_by_file(str((tmp_path / "a.py").resolve()))
        assert holder is not None and holder.session_id == "sess-A"

    def test_release_file_success(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.claim_file("sess-A", str(tmp_path / "a.py"))
        assert reg.release_file("sess-A", str(tmp_path / "a.py")) is True
        assert len(reg.get_session("sess-A").held_files) == 0

    def test_release_file_not_held_returns_false(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A")
        assert reg.release_file("sess-A", str(tmp_path / "x.py")) is False

    def test_release_file_unregistered_session_returns_false(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.release_file("sess-ghost", str(tmp_path / "a.py")) is False

    def test_get_session_unregistered_returns_none(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.get_session("sess-x") is None

    def test_get_session_expired_returns_none_no_write(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A")
        # 手动把 last_heartbeat 改老
        data = reg._load()
        data["sess-A"]["last_heartbeat"] = 0.0
        reg._save(data)
        assert reg.get_session("sess-A") is None
        # 过期 session 仍留在文件里（get_session 不删除）
        assert "sess-A" in reg._load()


class TestSessionConflictDetectorAcquireWriteback:
    """SessionConflictDetector.acquire_files 写回 registry 测试（修复验证）。"""

    def test_acquire_files_writes_back_to_registry(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        det = SessionConflictDetector(reg)
        allocated = det.acquire_files([str(tmp_path / "a.py")], "sess-A")
        assert len(allocated) == 1
        # 关键：写回了 registry
        info = reg.get_session("sess-A")
        assert info is not None and len(info.held_files) == 1

    def test_acquire_files_skips_conflict(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.claim_file("sess-A", str(tmp_path / "a.py"))
        det = SessionConflictDetector(reg)
        allocated = det.acquire_files([str(tmp_path / "a.py")], "sess-B")
        assert len(allocated) == 0  # 冲突跳过
