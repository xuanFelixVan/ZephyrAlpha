# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.scan_mutex
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_models
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_scanners.py; tests/audit/test_scan_mutex.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 扫描互斥不可绕过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_scan_mutex | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Scan Mutex — scan_mutex.py





module_id: MOD-INF-023


多实例竞态控制：文件锁 + 排队/合并策略 + 优先级抢占 + stale lock 检测。


对标 blueprint.md §2.15（多实例竞态控制）。"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from .drift_models import ScanLevel


@dataclass
class ScanLockRecord:
    pid: int

    scan_id: uuid.UUID

    scan_start_time: str

    scan_level: ScanLevel

    acquired_at: str = ""


@dataclass
class QueuedScan:
    scan_id: uuid.UUID

    level: ScanLevel

    enqueued_at: float

    timeout_seconds: float = 60.0


class ScanMutex:
    LOCK_FILE: str = "drift_scan.lock"

    SLO_MULTIPLIER: float = 2.0

    MAX_WAIT_LIGHT_S: float = 30.0

    MAX_WAIT_DEEP_S: float = 120.0

    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._lock_dir = os.path.join(project_root, "data", "drift_audit")

        os.makedirs(self._lock_dir, exist_ok=True)

        self._lock_path = os.path.join(self._lock_dir, self.LOCK_FILE)

        self._queue: list[QueuedScan] = []

    def is_locked(self) -> bool:
        return os.path.exists(self._lock_path)

    def read_lock(self) -> ScanLockRecord | None:
        if not os.path.exists(self._lock_path):
            return None

        try:
            with open(self._lock_path, encoding="utf-8") as fh:
                data = json.load(fh)

            return ScanLockRecord(
                pid=int(data.get("pid", 0)),
                scan_id=uuid.UUID(data.get("scan_id", str(uuid.uuid4()))),
                scan_start_time=data.get("scan_start_time", ""),
                scan_level=ScanLevel[data.get("scan_level", "STANDARD")],
                acquired_at=data.get("acquired_at", ""),
            )

        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def try_acquire(self, scan_id: uuid.UUID, level: ScanLevel) -> bool:
        if self.is_locked():
            lock = self.read_lock()

            if lock and self._is_stale(lock):
                self.force_release()

            else:
                return False

        record = ScanLockRecord(
            pid=os.getpid(),
            scan_id=scan_id,
            scan_start_time=datetime.now(UTC).isoformat(),
            scan_level=level,
            acquired_at=datetime.now(UTC).isoformat(),
        )

        self._write_lock(record)

        return True

    def acquire(self, scan_id: uuid.UUID, level: ScanLevel) -> bool:
        if self.try_acquire(scan_id, level):
            return True

        lock = self.read_lock()

        if lock is None:
            return self.try_acquire(scan_id, level)

        self._handle_collision(scan_id, level, lock)

        max_wait = self.MAX_WAIT_LIGHT_S if level is ScanLevel.LIGHT else self.MAX_WAIT_DEEP_S

        deadline = time.monotonic() + max_wait

        while time.monotonic() < deadline:
            time.sleep(0.5)

            if self.try_acquire(scan_id, level):
                return True

        return False

    def release(self, scan_id: uuid.UUID) -> None:
        lock = self.read_lock()

        if lock is None:
            return

        if lock.scan_id == scan_id:
            if os.path.exists(self._lock_path):
                try:
                    os.remove(self._lock_path)

                except OSError:
                    pass

    def force_release(self) -> None:
        if os.path.exists(self._lock_path):
            try:
                os.remove(self._lock_path)

            except OSError:
                pass

    def get_stale_locks(self) -> list[ScanLockRecord]:
        lock = self.read_lock()

        if lock and self._is_stale(lock):
            return [lock]

        return []

    def _handle_collision(
        self,
        scan_id: uuid.UUID,
        level: ScanLevel,
        lock: ScanLockRecord,
    ) -> None:
        if level == lock.scan_level:
            queued = QueuedScan(
                scan_id=scan_id,
                level=level,
                enqueued_at=time.monotonic(),
                timeout_seconds=self.MAX_WAIT_DEEP_S,
            )

            found = False

            for i, q in enumerate(self._queue):
                if q.level == level:
                    self._queue[i] = queued

                    found = True

                    break

            if not found:
                self._queue.append(queued)

        elif level is ScanLevel.LIGHT and lock.scan_level is ScanLevel.DEEP:
            self.force_release()

    def _is_stale(self, lock: ScanLockRecord) -> bool:
        try:
            acquired = datetime.fromisoformat(lock.acquired_at)

        except (ValueError, TypeError):
            acquired = datetime.now(UTC)

        age = datetime.now(UTC).replace(tzinfo=None) - acquired.replace(tzinfo=None)

        slo = 60.0

        return age.total_seconds() > slo * self.SLO_MULTIPLIER

    def _write_lock(self, record: ScanLockRecord) -> None:
        data = {
            "pid": record.pid,
            "scan_id": str(record.scan_id),
            "scan_start_time": record.scan_start_time,
            "scan_level": record.scan_level.name,
            "acquired_at": record.acquired_at,
        }

        tmp_path = f"{self._lock_path}.{os.getpid()}.tmp"

        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)

            os.replace(tmp_path, self._lock_path)

        except PermissionError:
            try:
                os.remove(tmp_path)

            except OSError:
                pass
