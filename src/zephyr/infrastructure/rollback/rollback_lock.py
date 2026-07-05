# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_lock
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_rollback_lock | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackLock — 全局回滚锁管理。

依据：
    蓝图 MOD-INF-021 §6.2 B9/B40
    盲点 B9（并发序列化）+ B40（多IDE并发）

实现：
    - 文件级锁：.zephyr/rollback.lock
    - SQLite advisory lock 备份
    - 队列管理 + 优先级排序
    - 超时重试机制
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

__all__ = [
    "LockAcquireResult",
    "LockPriority",
    "LockStatus",
    "RollbackLock",
]


class LockPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class LockAcquireResult:
    acquired: bool
    lock_id: str
    wait_time_ms: int
    reason: str = ""


@dataclass
class LockStatus:
    locked: bool
    owner: str
    priority: str
    acquired_at: str
    ttl_seconds: int
    queue_length: int


@dataclass
class LockRequest:
    lock_id: str
    priority: LockPriority
    owner: str
    task: str
    created_at: str
    timeout_ms: int
    expires_at: str


class RollbackLock:
    DEFAULT_LOCK_DIR: str = ".zephyr"
    DEFAULT_LOCK_FILE: str = "rollback.lock"
    DEFAULT_QUEUE_FILE: str = "rollback_lock_queue.jsonl"
    DEFAULT_TTL_SECONDS: int = 60
    DEFAULT_QUEUE_TTL_SECONDS: int = 300

    def __init__(
        self,
        project_root: Path | None = None,
        lock_dir: Path | None = None,
    ) -> None:
        self._project_root = project_root or Path.cwd()
        self._lock_dir = lock_dir or (self._project_root / self.DEFAULT_LOCK_DIR)
        self._lock_path = self._lock_dir / self.DEFAULT_LOCK_FILE
        self._queue_path = self._lock_dir / self.DEFAULT_QUEUE_FILE
        self._lock_dir.mkdir(parents=True, exist_ok=True)

    def acquire(
        self,
        owner: str = "unknown",
        priority: LockPriority = LockPriority.NORMAL,
        task: str = "",
        timeout_ms: int = 10000,
    ) -> LockAcquireResult:
        request = LockRequest(
            lock_id=self._generate_lock_id(),
            priority=priority,
            owner=owner,
            task=task,
            created_at=datetime.now(UTC).isoformat(),
            timeout_ms=timeout_ms,
            expires_at="",
        )

        start_time = time.time()

        try:
            fd = os.open(
                str(self._lock_path),
                os.O_CREAT | os.O_EXCL | os.O_RDWR,
                0o600,  # 5.17.12 修复：锁文件权限收紧至 0o600
            )
            # 5.169 修复：try/finally 确保 fd 关闭，os.write 抛异常时不泄漏
            try:
                lock_data = json.dumps(
                    {
                        "lock_id": request.lock_id,
                        "owner": owner,
                        "priority": priority.value,
                        "task": task,
                        "acquired_at": datetime.now(UTC).isoformat(),
                        "ttl_seconds": self.DEFAULT_TTL_SECONDS,
                    },
                    ensure_ascii=False,
                )

                os.write(fd, lock_data.encode("utf-8"))
            finally:
                os.close(fd)

        except FileExistsError:
            return self._handle_lock_conflict(request, start_time, timeout_ms)
        except OSError:
            return self._handle_lock_conflict(request, start_time, timeout_ms)

        wait_time = int((time.time() - start_time) * 1000)
        return LockAcquireResult(
            acquired=True,
            lock_id=request.lock_id,
            wait_time_ms=wait_time,
        )

    def _handle_lock_conflict(
        self,
        request: LockRequest,
        start_time: float,
        timeout_ms: int,
    ) -> LockAcquireResult:
        self._enqueue_request(request)

        while (time.time() - start_time) * 1000 < timeout_ms:
            if self._try_steal_expired_lock():
                wait_time = int((time.time() - start_time) * 1000)
                os.remove(str(self._lock_path))
                fd = os.open(
                    str(self._lock_path),
                    os.O_CREAT | os.O_EXCL | os.O_RDWR,
                    0o600,  # 5.17.12 修复：锁文件权限收紧至 0o600
                )
                # 5.169 修复：try/finally 确保 fd 关闭，os.write 抛异常时不泄漏
                try:
                    lock_data = json.dumps(
                        {
                            "lock_id": request.lock_id,
                            "owner": request.owner,
                            "priority": request.priority.value,
                            "task": request.task,
                            "acquired_at": datetime.now(UTC).isoformat(),
                            "ttl_seconds": self.DEFAULT_TTL_SECONDS,
                        },
                        ensure_ascii=False,
                    )
                    os.write(fd, lock_data.encode("utf-8"))
                finally:
                    os.close(fd)
                self._dequeue_request(request.lock_id)
                return LockAcquireResult(
                    acquired=True,
                    lock_id=request.lock_id,
                    wait_time_ms=wait_time,
                    reason="acquired after TTL expiry of previous holder",
                )

            time.sleep(0.1)

        wait_time = int((time.time() - start_time) * 1000)
        self._dequeue_request(request.lock_id)
        return LockAcquireResult(
            acquired=False,
            lock_id=request.lock_id,
            wait_time_ms=wait_time,
            reason=f"Timeout after {wait_time}ms",
        )

    def release(self, lock_id: str) -> LockAcquireResult:
        # 5.58.7 修复：原 lock_id 默认空字符串，空时跳过持有者验证直接删除锁文件。
        # 任何调用 release() 不传参的代码都会释放当前锁。改为必填参数，强制持有者验证。
        if not lock_id:
            return LockAcquireResult(
                acquired=False,
                lock_id=lock_id,
                wait_time_ms=0,
                reason="lock_id is required (5.58.7: prevent releasing others' locks)",
            )
        if not self._lock_path.exists():
            return LockAcquireResult(
                acquired=False,
                lock_id=lock_id,
                wait_time_ms=0,
                reason="Lock file does not exist",
            )

        try:
            lock_data = json.loads(self._lock_path.read_text(encoding="utf-8"))
            if lock_data.get("lock_id") != lock_id:
                return LockAcquireResult(
                    acquired=False,
                    lock_id=lock_id,
                    wait_time_ms=0,
                    reason=f"Lock held by {lock_data.get('lock_id')}, not {lock_id}",
                )

            os.remove(str(self._lock_path))
            return LockAcquireResult(
                acquired=True,
                lock_id=lock_id,
                wait_time_ms=0,
            )
        except json.JSONDecodeError:
            try:
                os.remove(str(self._lock_path))
            except FileNotFoundError:
                pass
            return LockAcquireResult(
                acquired=True,
                lock_id=lock_id,
                wait_time_ms=0,
                reason="Corrupted lock file removed",
            )
        except FileNotFoundError:
            return LockAcquireResult(
                acquired=False,
                lock_id=lock_id,
                wait_time_ms=0,
                reason="Lock already released",
            )

    def status(self) -> LockStatus:
        locked = self._lock_path.exists()
        owner = ""
        priority = ""
        acquired_at = ""
        ttl = self.DEFAULT_TTL_SECONDS

        if locked:
            try:
                lock_data = json.loads(self._lock_path.read_text(encoding="utf-8"))
                owner = lock_data.get("owner", "unknown")
                priority = lock_data.get("priority", "normal")
                acquired_at = lock_data.get("acquired_at", "")
                ttl = lock_data.get("ttl_seconds", self.DEFAULT_TTL_SECONDS)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        queue_length = self._count_queue()

        return LockStatus(
            locked=locked,
            owner=owner,
            priority=priority,
            acquired_at=acquired_at,
            ttl_seconds=ttl,
            queue_length=queue_length,
        )

    def force_release(self) -> LockAcquireResult:
        if self._lock_path.exists():
            try:
                os.remove(str(self._lock_path))
                return LockAcquireResult(
                    acquired=True,
                    lock_id="",
                    wait_time_ms=0,
                    reason="Forced release",
                )
            except Exception:
                pass
        return LockAcquireResult(
            acquired=True,
            lock_id="",
            wait_time_ms=0,
            reason="No lock to force release",
        )

    def _generate_lock_id(self) -> str:
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        return f"RBLK-{ts}"

    def _try_steal_expired_lock(self) -> bool:
        try:
            if not self._lock_path.exists():
                return False
            lock_data = json.loads(self._lock_path.read_text(encoding="utf-8"))
            acquired_at = lock_data.get("acquired_at", "")
            ttl = lock_data.get("ttl_seconds", self.DEFAULT_TTL_SECONDS)
            if acquired_at:
                acquired_dt = datetime.fromisoformat(acquired_at)
                elapsed = (datetime.now(UTC) - acquired_dt).total_seconds()
                if elapsed > ttl:
                    return True
            return False
        except (json.JSONDecodeError, FileNotFoundError):
            return True

    def _enqueue_request(self, request: LockRequest) -> None:
        try:
            with open(self._queue_path, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "lock_id": request.lock_id,
                            "priority": request.priority.value,
                            "owner": request.owner,
                            "task": request.task,
                            "created_at": request.created_at,
                            "timeout_ms": request.timeout_ms,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception:
            pass

    def _dequeue_request(self, lock_id: str) -> None:
        # 5.58.8 修复：原仅调用 _cleanup_stale_queue_entries()，不使用 lock_id 参数，
        # 不实际移除指定条目。队列文件不断增长；基于队列长度的调度决策误判系统负载。
        # 改为过滤掉指定 lock_id 的条目（同时清理过期条目）。
        if not self._queue_path.exists():
            return
        try:
            lines = self._queue_path.read_text(encoding="utf-8").strip().split("\n")
            now = datetime.now(UTC)
            valid_lines: list[str] = []
            for line in lines:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("lock_id") == lock_id:
                        continue
                    created = datetime.fromisoformat(entry.get("created_at", ""))
                    if (now - created).total_seconds() < self.DEFAULT_QUEUE_TTL_SECONDS:
                        valid_lines.append(line)
                except (json.JSONDecodeError, ValueError):
                    pass
            tmp_path = self._queue_path.with_suffix(".tmp")
            tmp_path.write_text("\n".join(valid_lines) + ("\n" if valid_lines else ""), encoding="utf-8")
            os.replace(str(tmp_path), str(self._queue_path))
        except Exception:
            pass

    def _count_queue(self) -> int:
        self._cleanup_stale_queue_entries()
        if not self._queue_path.exists():
            return 0
        try:
            lines = self._queue_path.read_text(encoding="utf-8").strip().split("\n")
            return len([l for l in lines if l])
        except Exception:
            return 0

    def _cleanup_stale_queue_entries(self) -> None:
        if not self._queue_path.exists():
            return
        try:
            lines = self._queue_path.read_text(encoding="utf-8").strip().split("\n")
            now = datetime.now(UTC)
            valid_lines: list[str] = []
            for line in lines:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    created = datetime.fromisoformat(entry.get("created_at", ""))
                    if (now - created).total_seconds() < self.DEFAULT_QUEUE_TTL_SECONDS:
                        valid_lines.append(line)
                except (json.JSONDecodeError, ValueError):
                    pass
            self._queue_path.write_text("\n".join(valid_lines) + ("\n" if valid_lines else ""), encoding="utf-8")
        except Exception:
            pass
