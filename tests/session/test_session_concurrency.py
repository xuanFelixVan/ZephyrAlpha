# [A_test] module_id: MOD-GOV_session_concurrency | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-429 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_session_concurrency
# [DOMAIN] D_AUTONOMY_CORE
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

import json
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

    def test_claim_files_batch_matches_per_file_semantics(self, tmp_path):
        """批量版与逐件版结果集等价：他人持有件排除、其余全收。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.claim_file("sess-A", str(tmp_path / "a.py"))
        got = reg.claim_files_batch("sess-B", ["a.py", "b.py", "c.py"])
        assert got == [str((tmp_path / p).resolve()) for p in ("b.py", "c.py")]
        assert len(reg.get_session("sess-B").held_files) == 2
        # a.py 仍归 sess-A（批量不得越权改写他人持有）
        holder_a = reg.find_session_by_file(str((tmp_path / "a.py").resolve()))
        assert holder_a is not None and holder_a.session_id == "sess-A"

    def test_claim_files_batch_idempotent_no_duplicate(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        files = ["a.py", "b.py", "c.py"]
        first = reg.claim_files_batch("sess-A", files)
        second = reg.claim_files_batch("sess-A", files)
        assert first == second
        assert len(reg.get_session("sess-A").held_files) == 3

    def test_claim_files_batch_writes_registry_once(self, tmp_path, monkeypatch):
        """O(N²) 治本断言：整表写回次数与件数无关（逐件版每件写一次）。"""
        reg = SessionRegistry(project_root=tmp_path)
        calls = {"n": 0}
        orig_save = reg._save

        def _counting_save(data):
            calls["n"] += 1
            return orig_save(data)

        monkeypatch.setattr(reg, "_save", _counting_save)
        reg.claim_files_batch("sess-A", [f"f{i}.py" for i in range(50)])
        assert calls["n"] <= 2, f"批量 claim 整表写了 {calls['n']} 次（期望懒注册 1 + 提交 1）"
        assert len(reg.get_session("sess-A").held_files) == 50

    def test_claim_files_batch_empty_list_is_noop(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.claim_files_batch("sess-A", []) == []

    def test_release_files_batch_removes_all_and_skips_unheld(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.claim_files_batch("sess-A", ["a.py", "b.py"])
        released = reg.release_files_batch("sess-A", ["a.py", "b.py", "ghost.py"])
        assert released == [str((tmp_path / p).resolve()) for p in ("a.py", "b.py")]
        assert reg.get_session("sess-A").held_files == []

    def test_release_files_batch_unregistered_session_returns_empty(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.release_files_batch("sess-ghost", ["a.py"]) == []

    def test_get_session_unregistered_returns_none(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.get_session("sess-x") is None

    def test_get_session_expired_returns_none_no_write(self, tmp_path):
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A")
        # 手动把 last_heartbeat 改老
        data = reg.load()
        data["sess-A"]["last_heartbeat"] = 0.0
        reg.save(data)
        assert reg.get_session("sess-A") is None
        # 过期 session 仍留在文件里（get_session 不删除）
        assert "sess-A" in reg.load()


class TestSessionRegistrySaveRace:
    """_save per-pid tmp 竞态治本回归（2026-08-15 WinError 2 实证：
    共享 session_registry.tmp 跨进程互踩——A replace 移走后 B replace 报
    '系统找不到指定的文件'，该次写静默丢失致 session 假性过期）。"""

    def test_save_uses_per_pid_tmp_no_shared_tmp_residue(self, tmp_path, monkeypatch):
        monkeypatch.setattr(os, "getpid", lambda: 424242)
        reg = SessionRegistry(project_root=tmp_path)
        reg._save({"sess-A": {"x": 1}})
        runtime = tmp_path / ".runtime"
        final = json.loads((runtime / "session_registry.json").read_text(encoding="utf-8"))
        assert final == {"sess-A": {"x": 1}}
        assert not (runtime / "session_registry.tmp").exists()  # 共享名 tmp 不再使用
        assert not list(runtime.glob("*.tmp"))  # 自身 tmp 已被 os.replace 消耗

    def test_save_ignores_foreign_inflight_tmp(self, tmp_path, monkeypatch):
        """他进程在飞的共享名 tmp 不被吞（旧实现 os.replace 会吞掉它致对方 WinError 2）。"""
        monkeypatch.setattr(os, "getpid", lambda: 424243)
        reg = SessionRegistry(project_root=tmp_path)
        foreign = tmp_path / ".runtime" / "session_registry.tmp"
        foreign.write_text('{"other": {}}', encoding="utf-8")
        reg._save({"mine": {"x": 1}})
        final = json.loads((tmp_path / ".runtime" / "session_registry.json").read_text(encoding="utf-8"))
        assert final == {"mine": {"x": 1}}
        assert foreign.exists()  # 旧实现会吞掉它
        assert foreign.read_text(encoding="utf-8") == '{"other": {}}'

    def test_handoff_uses_per_pid_tmp(self, tmp_path, monkeypatch):
        from zephyr.security.access_control.session_concurrency import SessionHandoff

        monkeypatch.setattr(os, "getpid", lambda: 424244)
        handoff_dir = tmp_path / ".runtime" / "handoffs"
        handoff_dir.mkdir(parents=True, exist_ok=True)
        foreign = handoff_dir / "handoff_sess-A.tmp"
        foreign.write_text("inflight", encoding="utf-8")
        h = SessionHandoff(project_root=tmp_path)
        out = h.write_handoff("sess-A", summary="s")
        assert out.exists()
        assert foreign.exists()  # 他进程 tmp 不被吞

    def test_save_retries_on_access_denied_then_succeeds(self, tmp_path, monkeypatch):
        """WinError 5 治本（2026-09-13）：读方持锁的前两次 replace 报 EACCES
        → 退避重试后第三次成功，注册表内容完整落盘（watchdog/心跳 daemon 读
        窗口毫秒级，实证连锁：保存失败→会话不在表→漂移误报 critical）。"""
        import errno

        monkeypatch.setattr(os, "getpid", lambda: 424245)
        # S4-D 双写后一次 _save=片写+旧表镜像写——本测钉的是旧表写路径的退避纪律
        # （kill-switch 定格单写面，replace 计数语义与治本时点一致）
        monkeypatch.setenv("ZEPHYR_SESSION_REGISTRY_SHARDS", "0")
        reg = SessionRegistry(project_root=tmp_path)
        calls = {"n": 0}
        real_replace = os.replace

        def flaky_replace(src, dst):
            calls["n"] += 1
            if calls["n"] <= 2:
                raise OSError(errno.EACCES, "Permission denied (simulated reader lock)")
            return real_replace(src, dst)

        monkeypatch.setattr(os, "replace", flaky_replace)
        # 压缩退避等待（模拟即可，真实 10/50/100ms 语义不变）
        import zephyr.security.access_control.session_concurrency as sc

        monkeypatch.setattr(sc, "time", type("T", (), {"sleep": staticmethod(lambda *_: None)}))
        reg._save({"sess-A": {"x": 1}})
        assert calls["n"] == 3, "EACCES 必须重试到成功"
        final = json.loads((tmp_path / ".runtime" / "session_registry.json").read_text(encoding="utf-8"))
        assert final == {"sess-A": {"x": 1}}

    def test_save_gives_up_after_max_retries(self, tmp_path, monkeypatch):
        """持续 EACCES（读方死锁等病态场景）→ 重试耗尽后抛 OSError 由 _save
        捕获降 warning（不崩进程，下一心跳自愈重写）——重试有界，不无限转。"""
        import errno

        monkeypatch.setattr(os, "getpid", lambda: 424246)
        reg = SessionRegistry(project_root=tmp_path)
        monkeypatch.setattr(
            os, "replace", lambda *_: (_ for _ in ()).throw(OSError(errno.EACCES, "Permission denied (persistent)"))
        )
        import zephyr.security.access_control.session_concurrency as sc

        monkeypatch.setattr(sc, "time", type("T", (), {"sleep": staticmethod(lambda *_: None)}))
        reg._save({"sess-A": {"x": 1}})  # 不抛——_save 捕获 OSError 降 warning
        assert not (tmp_path / ".runtime" / "session_registry.json").exists()

    def test_save_no_retry_on_other_oserror(self, tmp_path, monkeypatch):
        """非 EACCES 错误（如 ENOENT）不重试——一次即抛，维持原语义。"""
        import errno

        monkeypatch.setattr(os, "getpid", lambda: 424247)
        # S4-D 双写后一次 _save=片写+旧表镜像写——本测钉的是旧表写路径的非 EACCES
        # 不重试纪律（kill-switch 定格单写面，replace 计数语义与治本时点一致）
        monkeypatch.setenv("ZEPHYR_SESSION_REGISTRY_SHARDS", "0")
        reg = SessionRegistry(project_root=tmp_path)
        calls = {"n": 0}

        def enoent_replace(*_):
            calls["n"] += 1
            raise OSError(errno.ENOENT, "No such file")

        monkeypatch.setattr(os, "replace", enoent_replace)
        reg._save({"sess-A": {"x": 1}})  # _save 捕获降 warning
        assert calls["n"] == 1, "非 EACCES 不得重试"


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
            session_id="sess-dead",
            pid=_DEAD_PID,
            start_time=time.time(),
            last_heartbeat=time.time(),
        )
        assert _is_session_alive(info, time.time()) is False

    def test_alive_pid_recent_heartbeat_returns_true(self):
        """PID 存活 + 心跳未过期 → True。"""
        info = SessionInfo(
            session_id="sess-alive",
            pid=os.getpid(),
            start_time=time.time(),
            last_heartbeat=time.time(),
        )
        assert _is_session_alive(info, time.time()) is True

    def test_alive_pid_expired_heartbeat_returns_false(self):
        """PID 存活但心跳过期 → False（TTL 兜底）。"""
        info = SessionInfo(
            session_id="sess-idle",
            pid=os.getpid(),
            start_time=0.0,
            last_heartbeat=0.0,
        )
        assert _is_session_alive(info, time.time()) is False

    def test_pid_zero_falls_back_to_ttl_only(self):
        """pid=0（缺失/旧版）→ 跳过 PID 检查，仅靠 TTL（保守不激进删除）。"""
        now = time.time()
        # pid=0 + 心跳新鲜 → 存活（TTL 通过）
        info_fresh = SessionInfo(
            session_id="sess-zero",
            pid=0,
            start_time=now,
            last_heartbeat=now,
        )
        assert _is_session_alive(info_fresh, now) is True
        # pid=0 + 心跳过期 → 失效（TTL 兜底）
        info_stale = SessionInfo(
            session_id="sess-zero",
            pid=0,
            start_time=0.0,
            last_heartbeat=0.0,
        )
        assert _is_session_alive(info_stale, now) is False


class TestSessionRegistryPidLiveness:
    """SessionRegistry PID liveness 集成测试（S3-A 治本）。

    核心场景：进程崩溃后 PID 已死但心跳新鲜（< 3600s TTL），
    原 TTL-only 设计会误判为活跃持续 1 小时；S3-A 改为 PID+TTL 双判据，零窗口期清理。
    """

    def test_list_active_dead_pid_tombstoned_within_grace(self, tmp_path):
        """死 PID session 立即从 active 排除（S3-A 功能判死零窗口），但心跳在
        _REAP_GRACE_SECONDS 宽限窗内时物理保留 tombstone（086d0e24 worker 证3
        近期活跃宽限窗的记录存续前提——记录被即删致 worker 证3 误判 rogue，
        #119：2026-08-17 REGF/TDEBT/GOVB 三起拒启实证）。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-dead", pid=_DEAD_PID)
        # 心跳是新鲜的（刚注册），但 PID 已死
        active = reg.list_active()
        assert len(active) == 0  # 死 PID 功能判死：不进 active
        # tombstone：心跳在宽限窗内 -> 物理保留
        assert "sess-dead" in reg.load()

    def test_list_active_reaps_dead_pid_after_grace(self, tmp_path):
        """死 PID + 心跳超 _REAP_GRACE_SECONDS -> 物理删除（S3-A 清理语义保留）。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-dead-old", pid=_DEAD_PID)
        data = reg.load()
        data["sess-dead-old"]["last_heartbeat"] = time.time() - 20 * 60
        reg.save(data)
        active = reg.list_active()
        assert len(active) == 0
        assert "sess-dead-old" not in reg.load()

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
        # 死 PID 功能判死：不进 active；心跳新鲜 -> tombstone 物理保留（#119）
        data = reg.load()
        assert "sess-dead-1" in data
        assert "sess-dead-2" in data
        assert "sess-alive" in data


class TestSessionRegistryAnchorsLandingWorktree:
    """#ARCH-324 治本双向钉：队列落地 worktree 必须锚主仓 registry。

    旧判据只认父目录名 ".worktrees"，漏掉队列落地 worktree
    （…/.runtime/commit_queue/worktree，父名 "commit_queue"）→ 落地面读到 worktree
    自带的小 session_registry.json → SESSION-REQUIRED 假红（已实测）。
    """

    @staticmethod
    def _make_commit_queue_worktree(tmp_path):
        """构造主仓 + 队列落地 worktree（.git 为 gitdir 指针文件，父名 commit_queue）。"""
        main = tmp_path / "main"
        (main / ".git" / "worktrees" / "worktree").mkdir(parents=True)
        (main / ".runtime").mkdir(parents=True, exist_ok=True)
        (main / ".runtime" / "session_registry.json").write_text(
            json.dumps({"alice": {"pid": 0, "held_files": [], "last_heartbeat": time.time()}}),
            encoding="utf-8",
        )
        wt = main / ".runtime" / "commit_queue" / "worktree"
        (wt / ".runtime").mkdir(parents=True, exist_ok=True)
        (wt / ".git").write_text(f"gitdir: {main / '.git' / 'worktrees' / 'worktree'}\n", encoding="utf-8")
        # worktree 自带空 registry——旧代码读到它即产生假红
        (wt / ".runtime" / "session_registry.json").write_text("{}", encoding="utf-8")
        return main, wt

    def test_landing_worktree_anchors_main_registry(self, tmp_path):
        """绿向钉：落地 worktree 经唯一真源判据锚主仓，读到主仓共享 registry。"""
        main, wt = self._make_commit_queue_worktree(tmp_path)
        assert wt.parent.name == "commit_queue"  # 旧 ".worktrees" 名猜测命不中的形态
        reg = SessionRegistry(project_root=wt)
        assert reg._project_root == main
        assert reg._registry_path == main / ".runtime" / "session_registry.json"
        assert "alice" in reg.load()  # 读主仓内容，非 worktree 空副本

    def test_old_name_guess_would_not_anchor(self, tmp_path, monkeypatch):
        """变异承重钉：把判据打回旧 ".worktrees" 名猜测 → 落地 worktree 不再锚主仓（证红）。"""

        def _old_guess(root):
            if root.parent.name == ".worktrees":
                return root.parent.parent
            return root

        monkeypatch.setattr("zephyr.security.access_control.session_concurrency.anchor_main_root", _old_guess)
        main, wt = self._make_commit_queue_worktree(tmp_path)
        reg = SessionRegistry(project_root=wt)
        assert reg._project_root != main  # 旧行为漏判——不锚主仓（此即被治好的病根）
        assert reg._registry_path == wt / ".runtime" / "session_registry.json"
        assert reg.load() == {}  # 读到 worktree 空副本 → 若据此判活必假红


# ---------------------------------------------------------------------------
# S4-D 整表重写竞态 → 每会话分片（全流通夜战 G2 st-circ-g2-20260930）
# 手术簿：docs/_working/total_circulation_night/s4_d_session_registry.md
# 病根：_load 整表读+_save 整表重写（跨进程零互斥）——A load→B load→B save→A save
# 交错抹掉 B 的新增/心跳（SESSION-REQUIRED 假红/心跳假死）；单文件一损俱损。
# 处方：写只碰本会话片（.runtime/session_registry/<sid>.json），读侧聚合+迁移双写。
# ---------------------------------------------------------------------------

_DEAD_PID_0 = 0  # 逻辑会话：走心跳新鲜度判据（register 即活，90s 窗）


class TestS4DShardRedNeedles:
    """红测两针（先红后修纪律——现码必红，分片后天然绿）。"""

    def test_rd1_stale_snapshot_writeback_must_not_erase_sibling(self, tmp_path):
        """R-D1 交错写竞态判别：A load → B register → A save(旧快照) —— B 不得被抹。

        现码：a.save(snap) 整表替换 → sB 丢失（last-writer-wins 结构性丢失，必红）。
        """
        a = SessionRegistry(project_root=tmp_path)
        b = SessionRegistry(project_root=tmp_path)
        a.register("sA", pid=_DEAD_PID_0)
        snap = a.load()  # A 进程读到旧表 {sA}
        b.register("sB", pid=_DEAD_PID_0)  # B 读改写（新增 sB）
        a.save(snap)  # A 用旧快照整表写回
        assert a.get_session("sB") is not None, "B 的新增被 A 的过期写回抹除（整表重写竞态）"

    def test_rd2a_corrupt_storage_single_session_loss_radius(self, tmp_path):
        """R-D2 损伤半径：单会话存储损坏 → 其他会话 register/heartbeat/get_session 必须正常。

        现码：单文件一损俱损整表退 {}（必红）；分片后损失半径=单片。
        """
        a = SessionRegistry(project_root=tmp_path)
        a.register("sess-A", pid=_DEAD_PID_0)
        a.register("sess-B", pid=_DEAD_PID_0)
        # 损坏 sB 的存储位（分片后=sB 片；现码退化为唯一单表文件）
        p = tmp_path / ".runtime" / "session_registry" / "sess-B.json"
        if not p.exists():
            p = tmp_path / ".runtime" / "session_registry.json"
        p.write_text("{CORRUPTED!!", encoding="utf-8")
        assert a.get_session("sess-A") is not None, "他片损坏不得牵连本会话查询（一损俱损）"
        assert a.heartbeat("sess-A") is True, "他片损坏不得吞本会话心跳"
        a.register("sess-C", pid=_DEAD_PID_0)
        assert a.get_session("sess-C") is not None, "损坏后新注册必须可查询"

    def test_rd2b_sibling_write_leaves_own_bytes_untouched(self, tmp_path):
        """R-D2 写隔离：写 B 片不得改 A 片字节（mtime+内容断言）。

        现码：heartbeat(sB) 整表重写同一文件 → A 的存储字节被动（必红）。
        """
        a = SessionRegistry(project_root=tmp_path)
        b = SessionRegistry(project_root=tmp_path)
        a.register("sess-A", pid=_DEAD_PID_0)
        b.register("sess-B", pid=_DEAD_PID_0)
        pa = tmp_path / ".runtime" / "session_registry" / "sess-A.json"
        own = pa if pa.exists() else tmp_path / ".runtime" / "session_registry.json"
        before = own.read_bytes()
        b.heartbeat("sess-B")
        assert own.read_bytes() == before, "他会话心跳不得重写本会话存储字节（共享可变面未拆）"


class TestS4DShardDifferentialMatrix:
    """S4-D 差分矩阵（簿 §5，13 例映射；1/2/4/13 由既有用例与 e2e 套件承载）。"""

    def test_m3_dependency_roundtrip_on_shards(self, tmp_path):
        """矩阵3：depends_on 登记跨片一致性（register_dependency/clear_dependency）。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-dep", pid=0)
        assert reg.register_dependency("sess-dep", "sess-other") is True
        info = reg.get_session("sess-dep")
        assert info is not None and "sess-other" in info.depends_on_sessions
        assert reg.clear_dependency("sess-dep", "sess-other") is True
        info = reg.get_session("sess-dep")
        assert info is not None and "sess-other" not in info.depends_on_sessions
        assert reg.clear_dependency("sess-ghost", "x") is False  # 未注册=False

    def test_m6_shard_missing_reads_as_unregistered(self, tmp_path):
        """矩阵6：片缺失 → 读侧视作未注册（get_session None）。"""
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.get_session("sess-never-registered") is None

    def test_m7_shards_dir_absent_falls_back_to_legacy(self, tmp_path):
        """矩阵7：片目录缺席（部署前形态）→ 回退读旧表。"""
        runtime = tmp_path / ".runtime"
        runtime.mkdir(parents=True)
        (runtime / "session_registry.json").write_text(
            json.dumps(
                {
                    "sess-legacy": {
                        "session_id": "sess-legacy",
                        "pid": 0,
                        "start_time": 1.0,
                        "held_files": [],
                        # noqa: m46-time — 测试夹具新鲜心跳构造（非 schema 生成器）
                        "last_heartbeat": time.time(),
                        # noqa: m46-time — 同上，活性锚点新鲜值
                        "last_activity": time.time(),
                        "is_breaking_change": False,
                        "task_files": [],
                        "depends_on_sessions": [],
                        "logical": False,
                    }
                }
            ),
            encoding="utf-8",
        )
        reg = SessionRegistry(project_root=tmp_path)
        assert not (runtime / "session_registry").exists()  # 读路径不得创建片目录
        info = reg.get_session("sess-legacy")
        assert info is not None and info.session_id == "sess-legacy"

    def test_m8_migration_dualwrite_both_sides_consistent(self, tmp_path):
        """矩阵8：迁移双写窗口（旧表+片并存，两侧读一致）。"""
        a = SessionRegistry(project_root=tmp_path)
        a.register("sess-mig", pid=0)
        runtime = tmp_path / ".runtime"
        shard = runtime / "session_registry" / "sess-mig.json"
        legacy = runtime / "session_registry.json"
        assert shard.exists() and legacy.exists(), "双写：片与旧表并存"
        shard_entry = json.loads(shard.read_text(encoding="utf-8"))
        legacy_entry = json.loads(legacy.read_text(encoding="utf-8"))["sess-mig"]
        assert shard_entry == legacy_entry, "双写两侧内容一致"
        b = SessionRegistry(project_root=tmp_path)
        info = b.get_session("sess-mig")
        assert info is not None and info.session_id == "sess-mig"
        assert "sess-mig" in b.load()

    def test_m9_ttl_sweep_spares_live_and_recently_dead(self, tmp_path):
        """矩阵9：TTL 清扫不误杀——活片（pid 活/心跳新鲜）与宽限窗内死记录保留。"""
        from zephyr.security.access_control.session_concurrency import _REAP_GRACE_SECONDS

        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-live", pid=os.getpid())  # PID 活+心跳新鲜
        reg.register("sess-dead-recent", pid=_DEAD_PID)  # PID 死但心跳新鲜（宽限窗 tombstone）
        data = reg.load()
        # noqa: m46-time — 宽限窗相对偏移计时（非 schema 生成器）
        data["sess-dead-recent"]["last_heartbeat"] = time.time() - 60  # 宽限 900s 内
        reg.save(data)
        active_ids = {i.session_id for i in reg.list_active()}
        assert "sess-live" in active_ids
        assert "sess-dead-recent" not in active_ids  # 功能判死：消费方立即过滤（S3-A 零窗口）
        assert "sess-dead-recent" in reg.load()  # 物理记录宽限窗内保留（#119 tombstone）
        assert reg.get_session("sess-dead-recent") is None  # 只读消费者同样过滤

    def test_m10_sweep_dead_reaps_shard_and_legacy(self, tmp_path):
        """矩阵10：清扫死片（超宽限）→ 片+旧表双侧移除，gate 立即可见。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-corpse", pid=_DEAD_PID)
        data = reg.load()
        data["sess-corpse"]["last_heartbeat"] = 0.0  # 超宽限（epoch 老于 900s）
        reg.save(data)
        active_ids = {i.session_id for i in reg.list_active()}
        assert "sess-corpse" not in active_ids
        assert reg.get_session("sess-corpse") is None
        assert not (tmp_path / ".runtime" / "session_registry" / "sess-corpse.json").exists()
        assert "sess-corpse" not in json.loads(
            (tmp_path / ".runtime" / "session_registry.json").read_text(encoding="utf-8")
        )

    def test_m11_shard_layout_under_anchor_root(self, tmp_path):
        """矩阵11：anchor_main_root 路径下目录布局——片目录与旧表同根（主仓锚定不变）。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-anchor", pid=0)
        runtime = tmp_path / ".runtime"
        assert (runtime / "session_registry" / "sess-anchor.json").exists()
        assert (runtime / "session_registry.json").exists()

    def test_m_killswitch_env_falls_back_to_legacy_only(self, tmp_path, monkeypatch):
        """回退手柄：ZEPHYR_SESSION_REGISTRY_SHARDS=0 → 纯旧表模式（不写片）。"""
        monkeypatch.setenv("ZEPHYR_SESSION_REGISTRY_SHARDS", "0")
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-ks", pid=0)
        runtime = tmp_path / ".runtime"
        assert not (runtime / "session_registry").exists(), "kill-switch 下不得创建片目录"
        assert reg.get_session("sess-ks") is not None  # 旧表读正常
        reg.heartbeat("sess-ks")
        assert "sess-ks" in reg.load()

    def test_m12_soak_ten_writers_zero_loss(self, tmp_path):
        """矩阵12：高并发 10 写者×30 轮心跳 soak——零丢失（进程内并发形态）。"""
        reg = SessionRegistry(project_root=tmp_path)
        sids = [f"sess-soak-{i}" for i in range(10)]
        for s in sids:
            reg.register(s, pid=0)
        errors: list[Exception] = []

        def _hammer(sid: str) -> None:
            try:
                r = SessionRegistry(project_root=tmp_path)
                for _ in range(30):
                    assert r.heartbeat(sid) is True
            except Exception as e:  # noqa: BLE001 — soak 收集全部异常后统一断言
                errors.append(e)

        import threading

        threads = [threading.Thread(target=_hammer, args=(s,)) for s in sids]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=60)
        assert not errors, f"soak 异常: {errors[:3]}"
        for s in sids:
            info = reg.get_session(s)
            assert info is not None, f"{s} 心跳被并发写抹除（零丢失破约）"
            # noqa: m46-time — soak 新鲜度计时断言（非 schema 生成器）
            assert time.time() - info.last_heartbeat < 60

    def test_m12b_cross_process_register_race_zero_loss(self, tmp_path):
        """矩阵12 实形态：跨进程并发注册/心跳——R-D1 病根的真进程复现，零丢失。"""
        import subprocess
        import sys

        child_code = (
            "import sys, time\n"
            "from pathlib import Path\n"
            "from zephyr.security.access_control.session_concurrency import SessionRegistry\n"
            f"root = Path({str(tmp_path)!r})\n"
            "r = SessionRegistry(project_root=root)\n"
            "for i in range(20):\n"
            "    r.register('sess-child', pid=0)\n"
            "    r.heartbeat('sess-child')\n"
            "    time.sleep(0.005)\n"
            "print('CHILD_DONE')\n"
        )
        parent = SessionRegistry(project_root=tmp_path)
        parent.register("sess-parent", pid=0)
        proc = subprocess.run(  # noqa: S603 — 受控子进程跑注册循环
            [sys.executable, "-c", child_code],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(tmp_path),
        )
        assert "CHILD_DONE" in proc.stdout, f"子进程失败: {proc.stderr[-400:]}"
        for i in range(20):
            assert parent.heartbeat("sess-parent") is True  # 与子进程并发写
        child_info = parent.get_session("sess-child")
        parent_info = parent.get_session("sess-parent")
        assert child_info is not None, "子会话注册/心跳被父进程写回抹除（跨进程竞态）"
        assert parent_info is not None
        # noqa: m46-time — 跨进程竞态后新鲜度计时断言（非 schema 生成器）
        assert time.time() - child_info.last_heartbeat < 30
        assert time.time() - parent_info.last_heartbeat < 30

    def test_m_unregister_removes_from_both_sides(self, tmp_path):
        """矩阵1 补充：unregister 双侧移除+未知会话 False。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-unreg", pid=0)
        assert reg.unregister("sess-unreg") is True
        assert reg.get_session("sess-unreg") is None
        assert not (tmp_path / ".runtime" / "session_registry" / "sess-unreg.json").exists()
        assert "sess-unreg" not in json.loads(
            (tmp_path / ".runtime" / "session_registry.json").read_text(encoding="utf-8")
        )
        assert reg.unregister("sess-unreg") is False  # 幂等：已注销再注销=False
        assert reg.unregister("sess-ghost") is False
