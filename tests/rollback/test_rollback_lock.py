# [A_test] module_id: MOD-GOV_rollback_lock | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_lock
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC
from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.rollback_lock import (
    LockAcquireResult,
    LockPriority,
    LockStatus,
    RollbackLock,
)


@pytest.fixture
def lock_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".zephyr"
    d.mkdir()
    return d


@pytest.fixture
def rollback_lock(tmp_path: Path, lock_dir: Path) -> RollbackLock:
    return RollbackLock(project_root=tmp_path, lock_dir=lock_dir)


class TestRollbackLockInstantiation:
    def test_creates_with_defaults(self, tmp_path: Path):
        lk = RollbackLock(project_root=tmp_path)
        assert lk.lock_dir.exists()

    def test_creates_with_custom_dir(self, tmp_path: Path, lock_dir: Path):
        lk = RollbackLock(project_root=tmp_path, lock_dir=lock_dir)
        assert lk.lock_dir == lock_dir

    def test_lock_path_set(self, rollback_lock: RollbackLock):
        assert rollback_lock.lock_path.name == "rollback.lock"

    def test_queue_path_set(self, rollback_lock: RollbackLock):
        assert rollback_lock.queue_path.name == "rollback_lock_queue.jsonl"


class TestAcquire:
    def test_acquire_success(self, rollback_lock: RollbackLock):
        result = rollback_lock.acquire(owner="test-owner", task="test-task")
        assert isinstance(result, LockAcquireResult)
        assert result.acquired is True
        assert result.lock_id.startswith("RBLK-")
        assert result.wait_time_ms >= 0

    def test_acquire_creates_lock_file(self, rollback_lock: RollbackLock):
        rollback_lock.acquire(owner="test-owner")
        assert rollback_lock.lock_path.exists()
        data = json.loads(rollback_lock.lock_path.read_text(encoding="utf-8"))
        assert data["owner"] == "test-owner"

    def test_acquire_with_priority(self, rollback_lock: RollbackLock):
        result = rollback_lock.acquire(owner="test-owner", priority=LockPriority.CRITICAL, task="urgent")
        assert result.acquired is True
        data = json.loads(rollback_lock.lock_path.read_text(encoding="utf-8"))
        assert data["priority"] == "critical"

    def test_double_acquire_fails(self, rollback_lock: RollbackLock):
        r1 = rollback_lock.acquire(owner="owner-1", timeout_ms=500)
        assert r1.acquired is True
        r2 = rollback_lock.acquire(owner="owner-2", timeout_ms=500)
        assert r2.acquired is False

    def test_acquire_default_priority(self, rollback_lock: RollbackLock):
        result = rollback_lock.acquire(owner="test")
        data = json.loads(rollback_lock.lock_path.read_text(encoding="utf-8"))
        assert data["priority"] == "normal"


class TestRelease:
    def test_release_success(self, rollback_lock: RollbackLock):
        acquire_result = rollback_lock.acquire(owner="test-owner")
        release_result = rollback_lock.release(acquire_result.lock_id)
        assert release_result.acquired is True
        assert not rollback_lock.lock_path.exists()

    def test_release_wrong_lock_id(self, rollback_lock: RollbackLock):
        acquire_result = rollback_lock.acquire(owner="test-owner")
        release_result = rollback_lock.release("WRONG-ID")
        assert release_result.acquired is False
        assert "not WRONG-ID" in release_result.reason

    def test_release_no_lock_file(self, rollback_lock: RollbackLock):
        result = rollback_lock.release("any-id")
        assert result.acquired is False
        assert "does not exist" in result.reason

    def test_release_corrupted_lock(self, rollback_lock: RollbackLock):
        rollback_lock.lock_path.write_text("not-json", encoding="utf-8")
        result = rollback_lock.release("any-id")
        assert result.acquired is True
        assert "Corrupted" in result.reason

    def test_release_empty_lock_id(self, rollback_lock: RollbackLock):
        # 5.58.7 安全契约：空 lock_id 必须拒绝释放（防误释放他人锁），锁文件保留。
        acquire_result = rollback_lock.acquire(owner="test-owner")
        release_result = rollback_lock.release("")
        assert release_result.acquired is False
        assert "lock_id is required" in release_result.reason
        assert rollback_lock.lock_path.exists()


class TestStatus:
    def test_status_unlocked(self, rollback_lock: RollbackLock):
        status = rollback_lock.status()
        assert isinstance(status, LockStatus)
        assert status.locked is False
        assert status.owner == ""
        assert status.queue_length == 0

    def test_status_locked(self, rollback_lock: RollbackLock):
        rollback_lock.acquire(owner="test-owner", priority=LockPriority.HIGH)
        status = rollback_lock.status()
        assert status.locked is True
        assert status.owner == "test-owner"
        assert status.priority == "high"

    def test_status_after_release(self, rollback_lock: RollbackLock):
        r = rollback_lock.acquire(owner="test-owner")
        rollback_lock.release(r.lock_id)
        status = rollback_lock.status()
        assert status.locked is False


class TestForceRelease:
    def test_force_release_existing(self, rollback_lock: RollbackLock):
        rollback_lock.acquire(owner="test-owner")
        result = rollback_lock.force_release()
        assert result.acquired is True
        assert "Forced" in result.reason
        assert not rollback_lock.lock_path.exists()

    def test_force_release_no_lock(self, rollback_lock: RollbackLock):
        result = rollback_lock.force_release()
        assert result.acquired is True
        assert "No lock" in result.reason

    def test_force_release_then_acquire(self, rollback_lock: RollbackLock):
        rollback_lock.acquire(owner="owner-1")
        rollback_lock.force_release()
        r = rollback_lock.acquire(owner="owner-2")
        assert r.acquired is True


class TestLockExpiry:
    def test_expired_lock_can_be_stolen(self, rollback_lock: RollbackLock):
        rollback_lock.acquire(owner="old-owner")
        data = json.loads(rollback_lock.lock_path.read_text(encoding="utf-8"))
        data["acquired_at"] = "2000-01-01T00:00:00+00:00"
        rollback_lock.lock_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        assert rollback_lock.try_steal_expired_lock() is True

    def test_fresh_lock_cannot_be_stolen(self, rollback_lock: RollbackLock):
        rollback_lock.acquire(owner="fresh-owner")
        assert rollback_lock.try_steal_expired_lock() is False

    def test_no_lock_file_steal(self, rollback_lock: RollbackLock):
        assert rollback_lock.try_steal_expired_lock() is False


class TestQueueManagement:
    def test_enqueue_creates_file(self, rollback_lock: RollbackLock):
        from zephyr.infrastructure.rollback.rollback_lock import LockRequest

        req = LockRequest(
            lock_id="TEST-001",
            priority=LockPriority.NORMAL,
            owner="test",
            task="test-task",
            created_at="2026-01-01T00:00:00+00:00",
            timeout_ms=5000,
            expires_at="",
        )
        rollback_lock.enqueue_request(req)
        assert rollback_lock.queue_path.exists()

    def test_count_empty_queue(self, rollback_lock: RollbackLock):
        assert rollback_lock.count_queue() == 0

    def test_count_queue_with_entries(self, rollback_lock: RollbackLock):
        from datetime import datetime

        from zephyr.infrastructure.rollback.rollback_lock import LockRequest

        req = LockRequest(
            lock_id="TEST-001",
            priority=LockPriority.NORMAL,
            owner="test",
            task="test-task",
            created_at=datetime.now(UTC).isoformat(),
            timeout_ms=5000,
            expires_at="",
        )
        rollback_lock.enqueue_request(req)
        count = rollback_lock.count_queue()
        assert count >= 1
