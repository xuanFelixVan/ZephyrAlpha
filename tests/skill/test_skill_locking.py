# [A_test] module_id: MOD-GOV_skill_locking | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_locking
# [INVARIANTS] SkillLock uses RLock; SkillFileLock uses atomic file creation
# [MODIFY-GUARD] changes require review of skill_locking.py API
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises TimeoutError on lock timeout
# [TESTS] pytest tests/test_skill_locking.py -q
# [TTL] task_bound

import os
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.autonomy_core.skills.skill_locking import SkillFileLock, SkillLock


class TestSkillLockInstantiation:
    def test_class_has_locks_dict(self):
        assert isinstance(SkillLock.get_locks(), dict)

    def test_class_has_lock_factory(self):
        assert isinstance(SkillLock.get_lock_factory(), type(threading.Lock()))

    def test_default_timeout(self):
        assert SkillLock.DEFAULT_TIMEOUT_S == 30.0

    def test_lock_dir_default(self):
        assert Path("_locks") == SkillLock.LOCK_DIR


class TestSkillLockGetLock:
    def test_creates_new_lock_for_new_key(self):
        original_count = len(SkillLock.get_locks())
        lock = SkillLock.get_lock("test-new-key-001")
        assert lock is not None
        assert isinstance(lock, type(threading.RLock()))
        assert len(SkillLock.get_locks()) >= original_count + 1

    def test_returns_same_lock_for_same_key(self):
        lock1 = SkillLock.get_lock("test-same-key-002")
        lock2 = SkillLock.get_lock("test-same-key-002")
        assert lock1 is lock2


class TestSkillLockReadLock:
    def test_read_lock_acquires_and_releases(self):
        with SkillLock.read_lock("test-read-001"):
            assert SkillLock.is_lock_owned("r:test-read-001")
        assert not SkillLock.is_lock_owned("r:test-read-001")

    def test_read_lock_context_manager(self):
        executed = False
        with SkillLock.read_lock("test-read-002"):
            executed = True
        assert executed


class TestSkillLockWriteLock:
    def test_write_lock_acquires_and_releases(self):
        with SkillLock.write_lock("test-write-001"):
            assert SkillLock.is_lock_owned("w:test-write-001")
        assert not SkillLock.is_lock_owned("w:test-write-001")

    def test_write_lock_context_manager(self):
        executed = False
        with SkillLock.write_lock("test-write-002"):
            executed = True
        assert executed


class TestSkillLockRegistryLock:
    def test_registry_lock_acquires_and_releases(self):
        with SkillLock.registry_lock():
            assert SkillLock.is_lock_owned("registry")
        assert not SkillLock.is_lock_owned("registry")

    def test_registry_lock_context_manager(self):
        executed = False
        with SkillLock.registry_lock():
            executed = True
        assert executed


class TestSkillLockStats:
    def test_lock_stats_returns_dict(self):
        stats = SkillLock.lock_stats()
        assert "active_locks" in stats
        assert isinstance(stats["active_locks"], int)

    def test_lock_stats_reflects_locks(self):
        before = SkillLock.lock_stats()["active_locks"]
        SkillLock.get_lock("test-stats-key-999")
        after = SkillLock.lock_stats()["active_locks"]
        assert after >= before


class TestSkillLockTimeout:
    def test_read_lock_timeout_raises(self):
        lock = SkillLock.get_lock("r:test-timeout-read")
        acquired = threading.Event()

        def hold_lock():
            lock.acquire()
            acquired.set()
            time.sleep(0.5)
            lock.release()

        t = threading.Thread(target=hold_lock, daemon=True)
        t.start()
        acquired.wait(timeout=5)
        with pytest.raises(TimeoutError, match="Read lock timeout"):
            with patch.object(SkillLock, "DEFAULT_TIMEOUT_S", 0.01):
                with SkillLock.read_lock("test-timeout-read"):
                    pass
        t.join(timeout=5)

    def test_write_lock_timeout_raises(self):
        lock = SkillLock.get_lock("w:test-timeout-write")
        acquired = threading.Event()

        def hold_lock():
            lock.acquire()
            acquired.set()
            time.sleep(0.5)
            lock.release()

        t = threading.Thread(target=hold_lock, daemon=True)
        t.start()
        acquired.wait(timeout=5)
        with pytest.raises(TimeoutError, match="Write lock timeout"):
            with patch.object(SkillLock, "DEFAULT_TIMEOUT_S", 0.01):
                with SkillLock.write_lock("test-timeout-write"):
                    pass
        t.join(timeout=5)


class TestSkillFileLockInstantiation:
    def test_lock_dir_default(self):
        assert Path("_locks") == SkillFileLock.LOCK_DIR


class TestSkillFileLockAcquire:
    def test_acquire_and_release(self, tmp_path):
        lock_dir = tmp_path / "flocks"
        with patch.object(SkillFileLock, "LOCK_DIR", lock_dir):
            with SkillFileLock.acquire("test-file-lock-001", timeout_s=2.0):
                lock_path = lock_dir / "test-file-lock-001.lock"
                assert lock_path.exists()
            assert not lock_path.exists()

    def test_acquire_creates_lock_file(self, tmp_path):
        lock_dir = tmp_path / "flocks2"
        with patch.object(SkillFileLock, "LOCK_DIR", lock_dir):
            with SkillFileLock.acquire("test-file-lock-002", timeout_s=2.0):
                lock_path = lock_dir / "test-file-lock-002.lock"
                assert lock_path.exists()
                content = lock_path.read_text()
                assert content == str(os.getpid())

    def test_acquire_timeout_raises(self, tmp_path):
        lock_dir = tmp_path / "flocks3"
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_path = lock_dir / "test-file-lock-003.lock"
        lock_path.write_text("99999", encoding="utf-8")
        with patch.object(SkillFileLock, "LOCK_DIR", lock_dir):
            with pytest.raises(TimeoutError, match="File lock timeout"):
                with SkillFileLock.acquire("test-file-lock-003", timeout_s=0.1):
                    pass
        try:
            lock_path.unlink()
        except OSError:
            pass

    def test_acquire_context_manager_executes_body(self, tmp_path):
        lock_dir = tmp_path / "flocks4"
        executed = False
        with patch.object(SkillFileLock, "LOCK_DIR", lock_dir):
            with SkillFileLock.acquire("test-file-lock-004", timeout_s=2.0):
                executed = True
        assert executed


class TestSkillFileLockLockPath:
    def test_lock_path_creates_dir(self, tmp_path):
        lock_dir = tmp_path / "nested" / "flocks"
        with patch.object(SkillFileLock, "LOCK_DIR", lock_dir):
            path = SkillFileLock.lock_path("mylock")
            assert lock_dir.exists()
            assert path.name == "mylock.lock"
