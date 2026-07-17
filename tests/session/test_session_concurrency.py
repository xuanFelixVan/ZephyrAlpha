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
# [TTL] task_bound

from __future__ import annotations

import os
import tempfile
import time

from zephyr.security.access_control.session_concurrency import (
    CONFLICT_SCENARIOS,
    LOCK_TTL_SECONDS,
    ConcurrencyManager,
    ConflictType,
    LockLevel,
    SessionConflictDetector,
    SessionInfo,
    SessionRegistry,
    ZephyrLock,
    _is_session_alive,
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


# 极不可能存在的 PID（用于模拟死进程；is_pid_alive 会返回 False）
_DEAD_PID = 999999


class TestIsSessionAlive:
    """_is_session_alive 辅助函数测试（S3-A: PID+TTL 双判据）。"""

    def test_dead_pid_returns_false(self):
        """PID 已死 → 立即 False（零窗口期，不等 TTL）。"""
        info = SessionInfo(
            session_id="sess-dead", pid=_DEAD_PID,
            start_time=time.time(), last_heartbeat=time.time(),
        )
        assert _is_session_alive(info, time.time()) is False

    def test_alive_pid_recent_heartbeat_returns_true(self):
        """PID 存活 + 心跳未过期 → True。"""
        info = SessionInfo(
            session_id="sess-alive", pid=os.getpid(),
            start_time=time.time(), last_heartbeat=time.time(),
        )
        assert _is_session_alive(info, time.time()) is True

    def test_alive_pid_expired_heartbeat_returns_false(self):
        """PID 存活但心跳过期 → False（TTL 兜底）。"""
        info = SessionInfo(
            session_id="sess-idle", pid=os.getpid(),
            start_time=0.0, last_heartbeat=0.0,
        )
        assert _is_session_alive(info, time.time()) is False

    def test_pid_zero_falls_back_to_ttl_only(self):
        """pid=0（缺失/旧版）→ 跳过 PID 检查，仅靠 TTL（保守不激进删除）。"""
        now = time.time()
        # pid=0 + 心跳新鲜 → 存活（TTL 通过）
        info_fresh = SessionInfo(
            session_id="sess-zero", pid=0,
            start_time=now, last_heartbeat=now,
        )
        assert _is_session_alive(info_fresh, now) is True
        # pid=0 + 心跳过期 → 失效（TTL 兜底）
        info_stale = SessionInfo(
            session_id="sess-zero", pid=0,
            start_time=0.0, last_heartbeat=0.0,
        )
        assert _is_session_alive(info_stale, now) is False


class TestSessionRegistryPidLiveness:
    """SessionRegistry PID liveness 集成测试（S3-A 治本）。

    核心场景：进程崩溃后 PID 已死但心跳新鲜（< 3600s TTL），
    原 TTL-only 设计会误判为活跃持续 1 小时；S3-A 改为 PID+TTL 双判据，零窗口期清理。
    """

    def test_list_active_reaps_dead_pid_immediately(self, tmp_path):
        """死 PID session 在 list_active() 中立即被清理（不等 TTL）。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-dead", pid=_DEAD_PID)
        # 心跳是新鲜的（刚注册），但 PID 已死
        active = reg.list_active()
        assert len(active) == 0  # 死 PID 立即 reap
        # 注册表中也应被删除
        assert "sess-dead" not in reg._load()

    def test_list_active_keeps_alive_pid(self, tmp_path):
        """活 PID session 在 list_active() 中保留。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-alive", pid=os.getpid())
        active = reg.list_active()
        assert len(active) == 1
        assert active[0].session_id == "sess-alive"

    def test_find_breaking_change_session_ignores_dead_pid(self, tmp_path):
        """死 PID 的 breaking_change session 不阻断新 session（S3-A 核心场景）。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-dead-bc", pid=_DEAD_PID, is_breaking_change=True)
        # 死 PID 的 breaking_change session 应被忽略
        result = reg.find_breaking_change_session(exclude_session_id="sess-new")
        assert result is None

    def test_find_breaking_change_session_finds_alive_pid(self, tmp_path):
        """活 PID 的 breaking_change session 正常被发现。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-alive-bc", pid=os.getpid(), is_breaking_change=True)
        result = reg.find_breaking_change_session(exclude_session_id="sess-other")
        assert result is not None
        assert result.session_id == "sess-alive-bc"

    def test_get_session_returns_none_for_dead_pid(self, tmp_path):
        """get_session() 对死 PID session 返回 None（零窗口期）。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-dead", pid=_DEAD_PID)
        assert reg.get_session("sess-dead") is None

    def test_other_held_files_ignores_dead_pid_session(self, tmp_path):
        """死 PID session 持有的文件不计入 other_held_files()。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-dead", pid=_DEAD_PID, held_files=[str(tmp_path / "a.py")])
        # 死 PID 的持有应被忽略
        held = reg.other_held_files("sess-other")
        assert len(held) == 0

    def test_claim_file_succeeds_when_blocker_has_dead_pid(self, tmp_path):
        """死 PID session 持有的文件可被新 session claim（无冲突）。"""
        reg = SessionRegistry(project_root=tmp_path)
        # sess-dead 持有 a.py，但 PID 已死
        reg.register("sess-dead", pid=_DEAD_PID, held_files=[str(tmp_path / "a.py")])
        # sess-B 应能成功 claim a.py（死 PID 的持有被忽略）
        assert reg.claim_file("sess-B", str(tmp_path / "a.py")) is True

    def test_claim_file_lazy_reregisters_dead_pid_session(self, tmp_path):
        """claim_file 对死 PID session 触发懒注册，用当前 PID 覆盖。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-zombie", pid=_DEAD_PID)
        # 死 PID → claim_file 应懒注册（用 os.getpid() 覆盖）
        reg.claim_file("sess-zombie", str(tmp_path / "a.py"))
        info = reg.get_session("sess-zombie")
        assert info is not None
        assert info.pid == os.getpid()  # PID 被覆盖为当前进程
        assert info.pid != _DEAD_PID

    def test_list_active_mixed_dead_and_alive(self, tmp_path):
        """混合场景：死 PID + 活 PID → 只保留活 PID。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-dead-1", pid=_DEAD_PID)
        reg.register("sess-alive", pid=os.getpid())
        reg.register("sess-dead-2", pid=_DEAD_PID + 1)
        active = reg.list_active()
        assert len(active) == 1
        assert active[0].session_id == "sess-alive"
        # 死 PID 被清理
        data = reg._load()
        assert "sess-dead-1" not in data
        assert "sess-dead-2" not in data
        assert "sess-alive" in data
