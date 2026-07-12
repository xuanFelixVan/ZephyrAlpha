# [A_test] module_id: SRC-TST-1526 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_scan_mutex
# [INVARIANTS] 扫描互斥不可绕过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_scan_mutex.py
# [TTL] task_bound

import json
import os
import tempfile
import uuid

from zephyr.gov_drift.drift_models import ScanLevel
from zephyr.gov_drift.scan_mutex import (
    QueuedScan,
    ScanLockRecord,
    ScanMutex,
)


class TestScanLockRecord:
    def test_instantiation(self):
        rec = ScanLockRecord(
            pid=1234,
            scan_id=uuid.uuid4(),
            scan_start_time="2026-01-01T00:00:00Z",
            scan_level=ScanLevel.STANDARD,
        )
        assert rec.pid == 1234
        assert rec.scan_level == ScanLevel.STANDARD
        assert rec.acquired_at == ""

    def test_instantiation_with_acquired_at(self):
        rec = ScanLockRecord(
            pid=5678,
            scan_id=uuid.uuid4(),
            scan_start_time="2026-01-01T00:00:00Z",
            scan_level=ScanLevel.DEEP,
            acquired_at="2026-01-01T00:00:01Z",
        )
        assert rec.acquired_at == "2026-01-01T00:00:01Z"


class TestQueuedScan:
    def test_instantiation(self):
        qs = QueuedScan(
            scan_id=uuid.uuid4(),
            level=ScanLevel.LIGHT,
            enqueued_at=100.0,
        )
        assert qs.level == ScanLevel.LIGHT
        assert qs.timeout_seconds == 60.0

    def test_custom_timeout(self):
        qs = QueuedScan(
            scan_id=uuid.uuid4(),
            level=ScanLevel.DEEP,
            enqueued_at=200.0,
            timeout_seconds=120.0,
        )
        assert qs.timeout_seconds == 120.0


class TestScanMutexInit:
    def test_instantiation_with_project_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            assert mutex._project_root == tmpdir
            assert os.path.isdir(mutex._lock_dir)

    def test_instantiation_default_root(self):
        mutex = ScanMutex()
        assert mutex._project_root is not None
        assert os.path.isdir(mutex._lock_dir)


class TestScanMutexIsLocked:
    def test_not_locked_initially(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            assert mutex.is_locked() is False

    def test_locked_after_acquire(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid = uuid.uuid4()
            mutex.try_acquire(sid, ScanLevel.STANDARD)
            assert mutex.is_locked() is True


class TestScanMutexTryAcquire:
    def test_acquire_when_free(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid = uuid.uuid4()
            result = mutex.try_acquire(sid, ScanLevel.STANDARD)
            assert result is True

    def test_acquire_fails_when_locked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid1 = uuid.uuid4()
            sid2 = uuid.uuid4()
            mutex.try_acquire(sid1, ScanLevel.STANDARD)
            result = mutex.try_acquire(sid2, ScanLevel.STANDARD)
            assert result is False


class TestScanMutexReadLock:
    def test_read_lock_none_when_no_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            assert mutex.read_lock() is None

    def test_read_lock_after_acquire(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid = uuid.uuid4()
            mutex.try_acquire(sid, ScanLevel.DEEP)
            lock = mutex.read_lock()
            assert lock is not None
            assert lock.scan_id == sid
            assert lock.scan_level == ScanLevel.DEEP

    def test_read_lock_corrupt_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            os.makedirs(mutex._lock_dir, exist_ok=True)
            with open(mutex._lock_path, "w", encoding="utf-8") as f:
                f.write("NOT JSON")
            assert mutex.read_lock() is None


class TestScanMutexRelease:
    def test_release_own_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid = uuid.uuid4()
            mutex.try_acquire(sid, ScanLevel.STANDARD)
            mutex.release(sid)
            assert mutex.is_locked() is False

    def test_release_wrong_scan_id_does_not_release(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid = uuid.uuid4()
            mutex.try_acquire(sid, ScanLevel.STANDARD)
            mutex.release(uuid.uuid4())
            assert mutex.is_locked() is True

    def test_release_when_no_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            mutex.release(uuid.uuid4())


class TestScanMutexForceRelease:
    def test_force_release(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid = uuid.uuid4()
            mutex.try_acquire(sid, ScanLevel.STANDARD)
            mutex.force_release()
            assert mutex.is_locked() is False

    def test_force_release_when_no_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            mutex.force_release()
            assert mutex.is_locked() is False


class TestScanMutexGetStaleLocks:
    def test_no_stale_locks_when_no_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            assert mutex.get_stale_locks() == []

    def test_fresh_lock_not_stale(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid = uuid.uuid4()
            mutex.try_acquire(sid, ScanLevel.STANDARD)
            assert mutex.get_stale_locks() == []

    def test_stale_lock_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mutex = ScanMutex(project_root=tmpdir)
            sid = uuid.uuid4()
            mutex.try_acquire(sid, ScanLevel.STANDARD)
            lock = mutex.read_lock()
            assert lock is not None
            stale_data = {
                "pid": lock.pid,
                "scan_id": str(lock.scan_id),
                "scan_start_time": "2020-01-01T00:00:00+00:00",
                "scan_level": lock.scan_level.name,
                "acquired_at": "2020-01-01T00:00:00+00:00",
            }
            with open(mutex._lock_path, "w", encoding="utf-8") as f:
                json.dump(stale_data, f)
            stale = mutex.get_stale_locks()
            assert len(stale) == 1
