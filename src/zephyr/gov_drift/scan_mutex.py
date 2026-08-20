# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.scan_mutex
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.gov_drift.drift_models
# [CONSUMERS] src/zephyr/gov_drift/_scanners.py ; tests/audit/test_scan_mutex.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 扫描互斥不可绕过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Scan Mutex — scan_mutex.py


多实例竞态控制：文件锁 + 排队/合并策略 + 优先级抢占 + stale lock 检测。

5.58.2：锁内容含单调递增 fencing token（drift_scan.fence 持久计数器），
validate_fencing() 供受保护操作前验证未被取代。
5.58.3：SyncLockRenewer 按 TTL/3 周期刷新 acquired_at，持有者存活期间锁不过期。
5.58.4：锁创建使用 os.open(O_CREAT|O_EXCL) 原子创建，禁止 os.replace 覆盖他人锁。
5.58.5：LIGHT 扫描遇 DEEP 持锁时排队等待，禁止 force_release 强抢。

对标 blueprint.md §2.15（多实例竞态控制）。"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from zephyr.shared.infra.lock import SyncLockRenewer, next_fencing_token

from .drift_models import ScanLevel


@dataclass
class ScanLockRecord:
    pid: int

    scan_id: uuid.UUID

    scan_start_time: str

    scan_level: ScanLevel

    acquired_at: str = ""

    fencing_token: int = 0  # 5.58.2：单调递增 fencing token（0=未分配/历史锁文件）


@dataclass
class QueuedScan:
    scan_id: uuid.UUID

    level: ScanLevel

    enqueued_at: float

    timeout_seconds: float = 60.0


class ScanMutex:
    LOCK_FILE: str = "drift_scan.lock"

    FENCE_FILE: str = "drift_scan.fence"  # 5.58.2 fencing 持久计数器

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

        self._fence_path = os.path.join(self._lock_dir, self.FENCE_FILE)

        self._queue: list[QueuedScan] = []

        self._held: dict[str, int] = {}  # scan_id -> fencing_token（本进程持有）

        self._renewers: dict[str, SyncLockRenewer] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def lock_dir(self):
        """只读：lock_dir（Stage 4 公共化）。"""
        return self._lock_dir

    @lock_dir.setter
    def lock_dir(self, value):
        """写入：lock_dir（Stage 4 公共化）。"""
        self._lock_dir = value

    @property
    def lock_path(self):
        """只读：lock_path（Stage 4 公共化）。"""
        return self._lock_path

    @lock_path.setter
    def lock_path(self, value):
        """写入：lock_path（Stage 4 公共化）。"""
        self._lock_path = value

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

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
                fencing_token=int(data.get("fencing_token", 0) or 0),
            )

        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def try_acquire(self, scan_id: uuid.UUID, level: ScanLevel) -> bool:
        if self.is_locked():
            lock = self.read_lock()

            if lock is not None:
                if not self._is_stale(lock):
                    return False
                # stale——仅当内容未变时移除（防误删他人新获取的锁）
                self._remove_if_unchanged(lock)
            else:
                # 锁文件损坏——按文件 mtime 判定 stale，避免损坏锁永久死锁
                if self._corrupt_lock_stale():
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

        return self._create_lock_atomic(record)

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

        # 5.58.1：持有者验证——仅 scan_id 匹配才删除
        if lock.scan_id == scan_id:
            self._stop_renewer(scan_id)
            self._held.pop(str(scan_id), None)
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

    def validate_fencing(self, scan_id: uuid.UUID) -> bool:
        """5.58.2 受保护操作前验证——锁仍由 scan_id 持有且 fencing token 未变（未被取代）。"""
        lock = self.read_lock()

        if lock is None or lock.scan_id != scan_id:
            return False

        return lock.fencing_token == self._held.get(str(scan_id), -1)

    def get_stale_locks(self) -> list[ScanLockRecord]:
        lock = self.read_lock()

        if lock and self._is_stale(lock):
            return [lock]

        return []

    def _create_lock_atomic(self, record: ScanLockRecord) -> bool:
        """5.58.4：os.open(O_CREAT|O_EXCL) 原子创建锁文件。

        修复原 tmp+os.replace 覆盖式写入——两进程同时通过 is_locked() 检查后，
        os.replace 会静默覆盖他人刚创建的锁。O_EXCL 创建失败即返回 False，
        由 acquire() 等待循环重试，绝不覆盖他人锁。
        """
        try:
            fd = os.open(self._lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except OSError:
            return False

        try:
            # 5.58.2：已持锁后分配单调递增 fencing token 写入锁内容
            record.fencing_token = next_fencing_token(self._fence_path)
            os.write(fd, json.dumps(self._record_to_dict(record), ensure_ascii=False).encode("utf-8"))
        finally:
            os.close(fd)

        self._held[str(record.scan_id)] = record.fencing_token
        self._start_renewer(record.scan_id)
        return True

    def _remove_if_unchanged(self, expected: ScanLockRecord) -> bool:
        """stale 移除防误删——仅当锁内容与预期（scan_id + acquired_at）一致时才删除。"""
        current = self.read_lock()

        if current is None:
            return True  # 已被他人移除/损坏，由 O_EXCL 创建兜底

        if current.scan_id != expected.scan_id or current.acquired_at != expected.acquired_at:
            return False  # 内容已变（他人新锁），禁止删除

        try:
            os.remove(self._lock_path)
            return True
        except OSError:
            return False

    def _corrupt_lock_stale(self) -> bool:
        """损坏锁文件的 stale 判定——无内容可解析时按文件 mtime 计算年龄。"""
        try:
            age = time.time() - os.path.getmtime(self._lock_path)
        except OSError:
            return False

        return age > 60.0 * self.SLO_MULTIPLIER

    def _start_renewer(self, scan_id: uuid.UUID) -> None:
        """5.58.3：启动 TTL 自动续期 watchdog（TTL/3 周期刷新 acquired_at）。"""
        key = str(scan_id)

        if key in self._renewers:
            return

        renewer = SyncLockRenewer(
            lambda: self._refresh_lease(scan_id),
            60.0 * self.SLO_MULTIPLIER / 3,
            name=f"scan-mutex-renewer-{key[:8]}",
        )

        self._renewers[key] = renewer

        renewer.start()

    def _stop_renewer(self, scan_id: uuid.UUID) -> None:
        renewer = self._renewers.pop(str(scan_id), None)

        if renewer is not None:
            renewer.stop()

    def _refresh_lease(self, scan_id: uuid.UUID) -> bool:
        """5.58.3 续约：持有者身份校验（scan_id + fencing token）通过后刷新 acquired_at。"""
        lock = self.read_lock()

        if lock is None or lock.scan_id != scan_id:
            return False

        if lock.fencing_token != self._held.get(str(scan_id), -1):
            return False

        lock.acquired_at = datetime.now(UTC).isoformat()

        self._write_lock(lock)  # 持有者身份已校验，tmp+replace 重写本人锁内容

        return True

    @staticmethod
    def _record_to_dict(record: ScanLockRecord) -> dict:
        return {
            "pid": record.pid,
            "scan_id": str(record.scan_id),
            "scan_start_time": record.scan_start_time,
            "scan_level": record.scan_level.name,
            "acquired_at": record.acquired_at,
            "fencing_token": record.fencing_token,
        }

    def _enqueue(self, scan_id: uuid.UUID, level: ScanLevel, timeout_seconds: float) -> None:
        """入队/更新等待队列（同 scan_id 已排队则更新）。"""
        queued = QueuedScan(
            scan_id=scan_id,
            level=level,
            enqueued_at=time.monotonic(),
            timeout_seconds=timeout_seconds,
        )

        for i, q in enumerate(self._queue):
            if q.scan_id == scan_id:
                self._queue[i] = queued
                return

        self._queue.append(queued)

    def _handle_collision(
        self,
        scan_id: uuid.UUID,
        level: ScanLevel,
        lock: ScanLockRecord,
    ) -> None:
        if level == lock.scan_level:
            self._enqueue(scan_id, level, self.MAX_WAIT_DEEP_S)

        elif level is ScanLevel.LIGHT and lock.scan_level is ScanLevel.DEEP:
            # 5.58.5 修复：LIGHT 排队等待 DEEP 完成（acquire() 等待循环按
            # MAX_WAIT_LIGHT_S 重试），禁止 force_release 强抢 DEEP 锁——
            # DEEP 扫描被中途打断会产生不完整基线。
            self._enqueue(scan_id, level, self.MAX_WAIT_LIGHT_S)

    def _is_stale(self, lock: ScanLockRecord) -> bool:
        try:
            acquired = datetime.fromisoformat(lock.acquired_at)

        except (ValueError, TypeError):
            acquired = datetime.now(UTC)

        age = datetime.now(UTC).replace(tzinfo=None) - acquired.replace(tzinfo=None)

        slo = 60.0

        return age.total_seconds() > slo * self.SLO_MULTIPLIER

    def _write_lock(self, record: ScanLockRecord) -> None:
        """重写本持有者锁内容（仅续约使用——调用前 MUST 完成持有者身份校验）。"""
        data = self._record_to_dict(record)

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
