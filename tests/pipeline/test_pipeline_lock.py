# [A_test] module_id: MOD-GOV_pipeline_lock | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_pipeline_lock
# [INVARIANTS] MemoryLockBackend acquire/release cycle must be symmetric; PipelineLock timeout=0 must be non-blocking
# [MODIFY-GUARD] zephyr.infrastructure.pipeline.pipeline_lock
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.raises on invalid input
# [TESTS] —
# [TTL] task_bound


from zephyr.infrastructure.pipeline.pipeline_lock import (
    LockResult,
    LockStatus,
    MemoryLockBackend,
    PipelineLock,
)


class TestLockStatus:
    def test_enum_values(self):
        assert LockStatus.ACQUIRED == "acquired"
        assert LockStatus.CONFLICT == "conflict"
        assert LockStatus.TIMEOUT == "timeout"
        assert LockStatus.DEADLOCK == "deadlock"

    def test_is_str_enum(self):
        assert isinstance(LockStatus.ACQUIRED, str)


class TestLockResult:
    def test_defaults(self):
        r = LockResult(acquired=True, status=LockStatus.ACQUIRED, task_id="t1")
        assert r.locked_files == []
        assert r.conflict_tasks == []
        assert r.waited_ms == 0

    def test_with_values(self):
        r = LockResult(
            acquired=False,
            status=LockStatus.CONFLICT,
            task_id="t1",
            locked_files=["a.py"],
            conflict_tasks=["t2"],
            waited_ms=42,
        )
        assert r.acquired is False
        assert r.status == LockStatus.CONFLICT
        assert r.task_id == "t1"
        assert r.locked_files == ["a.py"]
        assert r.conflict_tasks == ["t2"]
        assert r.waited_ms == 42


class TestMemoryLockBackend:
    def test_acquire_single_file(self):
        backend = MemoryLockBackend()
        result = backend.try_acquire("task-1", ["src/foo.py"])
        assert result.acquired is True
        assert result.status == LockStatus.ACQUIRED
        assert result.task_id == "task-1"
        assert "src/foo.py" in result.locked_files

    def test_acquire_multiple_files(self):
        backend = MemoryLockBackend()
        result = backend.try_acquire("task-1", ["src/a.py", "src/b.py"])
        assert result.acquired is True
        assert len(result.locked_files) == 2

    def test_acquire_conflict_different_task(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/foo.py"])
        result = backend.try_acquire("task-2", ["src/foo.py"])
        assert result.acquired is False
        assert result.status == LockStatus.CONFLICT
        assert "task-1" in result.conflict_tasks

    def test_acquire_same_task_reacquire_same_files(self):
        backend = MemoryLockBackend()
        r1 = backend.try_acquire("task-1", ["src/foo.py"])
        assert r1.acquired is True
        r2 = backend.try_acquire("task-1", ["src/foo.py"])
        assert r2.acquired is True

    def test_acquire_same_task_additional_files(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/a.py"])
        r2 = backend.try_acquire("task-1", ["src/b.py"])
        assert r2.acquired is True
        assert backend.is_locked("src/a.py") == "task-1"
        assert backend.is_locked("src/b.py") == "task-1"

    def test_release_returns_files(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/a.py", "src/b.py"])
        released = backend.release("task-1")
        assert sorted(released) == ["src/a.py", "src/b.py"]

    def test_release_clears_locks(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/foo.py"])
        backend.release("task-1")
        assert backend.is_locked("src/foo.py") is None

    def test_release_nonexistent_task(self):
        backend = MemoryLockBackend()
        released = backend.release("ghost")
        assert released == []

    def test_list_locks_empty(self):
        backend = MemoryLockBackend()
        assert backend.list_locks() == {}

    def test_list_locks_after_acquire(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/a.py", "src/b.py"])
        locks = backend.list_locks()
        assert "task-1" in locks
        assert sorted(locks["task-1"]) == ["src/a.py", "src/b.py"]

    def test_list_locks_multiple_tasks(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/a.py"])
        backend.try_acquire("task-2", ["src/b.py"])
        locks = backend.list_locks()
        assert len(locks) == 2

    def test_is_locked_unlocked(self):
        backend = MemoryLockBackend()
        assert backend.is_locked("src/foo.py") is None

    def test_is_locked_after_acquire(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/foo.py"])
        assert backend.is_locked("src/foo.py") == "task-1"

    def test_layer_lock_blocks_file_with_layer_in_path(self):
        backend = MemoryLockBackend()
        r1 = backend.try_acquire("task-1", [], layer_locks=["L00/signals"])
        assert r1.acquired is True
        r2 = backend.try_acquire("task-2", ["L00/signals/data.py"])
        assert r2.acquired is False
        assert r2.status == LockStatus.CONFLICT

    def test_layer_lock_no_conflict_different_layer(self):
        backend = MemoryLockBackend()
        r1 = backend.try_acquire("task-1", [], layer_locks=["L00/signals"])
        assert r1.acquired is True
        r2 = backend.try_acquire("task-2", ["L01/other/file.py"])
        assert r2.acquired is True

    def test_layer_lock_conflict_same_layer(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", [], layer_locks=["L00/signals"])
        r2 = backend.try_acquire("task-2", [], layer_locks=["L00/signals"])
        assert r2.acquired is False
        assert "task-1" in r2.conflict_tasks

    def test_layer_lock_released_with_task(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", [], layer_locks=["L00/signals"])
        backend.release("task-1")
        r2 = backend.try_acquire("task-2", [], layer_locks=["L00/signals"])
        assert r2.acquired is True

    def test_reset_clears_all(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/a.py"])
        backend.try_acquire("task-2", ["src/b.py"])
        backend.reset()
        assert backend.list_locks() == {}
        assert backend.is_locked("src/a.py") is None
        assert backend.is_locked("src/b.py") is None

    def test_partial_conflict_blocks_entire_acquire(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/a.py"])
        r2 = backend.try_acquire("task-2", ["src/a.py", "src/b.py"])
        assert r2.acquired is False
        assert backend.is_locked("src/b.py") is None

    def test_acquire_empty_file_list(self):
        backend = MemoryLockBackend()
        r = backend.try_acquire("task-1", [])
        assert r.acquired is True

    def test_conflict_reports_multiple_owners(self):
        backend = MemoryLockBackend()
        backend.try_acquire("task-1", ["src/a.py"])
        backend.try_acquire("task-2", ["src/b.py"])
        r3 = backend.try_acquire("task-3", ["src/a.py", "src/b.py"])
        assert r3.acquired is False
        assert sorted(r3.conflict_tasks) == ["task-1", "task-2"]


class TestPipelineLock:
    def test_acquire_nonblocking_success(self):
        lock = PipelineLock()
        result = lock.acquire("task-1", ["src/foo.py"], timeout_s=0)
        assert result.acquired is True
        assert result.status == LockStatus.ACQUIRED

    def test_acquire_nonblocking_conflict(self):
        lock = PipelineLock()
        lock.acquire("task-1", ["src/foo.py"], timeout_s=0)
        result = lock.acquire("task-2", ["src/foo.py"], timeout_s=0)
        assert result.acquired is False
        assert result.status == LockStatus.CONFLICT

    def test_release(self):
        lock = PipelineLock()
        lock.acquire("task-1", ["src/foo.py"], timeout_s=0)
        released = lock.release("task-1")
        assert "src/foo.py" in released

    def test_conflicts_check(self):
        lock = PipelineLock()
        lock.acquire("task-1", ["src/foo.py"], timeout_s=0)
        conflicts = lock.conflicts("task-2", ["src/foo.py"])
        assert "task-1" in conflicts

    def test_conflicts_no_conflict(self):
        lock = PipelineLock()
        lock.acquire("task-1", ["src/foo.py"], timeout_s=0)
        conflicts = lock.conflicts("task-2", ["src/other.py"])
        assert conflicts == []

    def test_conflicts_same_task_not_reported(self):
        lock = PipelineLock()
        lock.acquire("task-1", ["src/foo.py"], timeout_s=0)
        conflicts = lock.conflicts("task-1", ["src/foo.py"])
        assert conflicts == []

    def test_list_all_empty(self):
        lock = PipelineLock()
        assert lock.list_all() == {}

    def test_list_all_after_acquire(self):
        lock = PipelineLock()
        lock.acquire("task-1", ["src/a.py"], timeout_s=0)
        all_locks = lock.list_all()
        assert "task-1" in all_locks

    def test_reset(self):
        lock = PipelineLock()
        lock.acquire("task-1", ["src/a.py"], timeout_s=0)
        lock.reset()
        assert lock.list_all() == {}

    def test_backend_property(self):
        lock = PipelineLock()
        assert isinstance(lock.backend, MemoryLockBackend)

    def test_custom_backend(self):
        backend = MemoryLockBackend()
        lock = PipelineLock(backend=backend)
        assert lock.backend is backend

    def test_acquire_with_layer_locks(self):
        lock = PipelineLock()
        result = lock.acquire("task-1", ["src/a.py"], timeout_s=0, layer_locks=["L00/signals"])
        assert result.acquired is True

    def test_acquire_timeout_returns_timeout_status(self):
        lock = PipelineLock()
        lock.acquire("task-1", ["src/foo.py"], timeout_s=0)
        result = lock.acquire("task-2", ["src/foo.py"], timeout_s=0.1, poll_interval_s=0.05)
        assert result.acquired is False
        assert result.status == LockStatus.TIMEOUT
