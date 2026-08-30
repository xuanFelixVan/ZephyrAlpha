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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: rollback_lock.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: lock_dir 参数
#   fields: 参数 lock_dir（无注解）
#   code: rollback_lock.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RollbackLock
#   name_en: RollbackLock
#   intro: class RollbackLock 源码 L125-L542
#   desc: 公共方法（定义序）: lock_dir, lock_path, queue_path, try_steal_expired_lock, enqueue_request, count_queue, validate_fe…
#   inputs: project_root lock_dir
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: RollbackLock
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from zephyr.shared.infra.lock import SyncLockRenewer, next_fencing_token  # 5.58.2/5.58.3 fencing+续期共享助手

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
    fencing_token: int = 0  # 5.58.2：本次获取的 fencing token（0=未分配）


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
        self._fence_path = self._lock_dir / "rollback.fence"  # 5.58.2 fencing 持久计数器
        self._lock_dir.mkdir(parents=True, exist_ok=True)
        self._held_lock_id: str | None = None
        self._held_token: int = 0
        self._renewer: SyncLockRenewer | None = None

    # ── Stage 4 公共化属性 + 方法 ──

    @property
    def lock_dir(self) -> Path:
        """锁目录路径（public API, Stage 4）."""
        return self._lock_dir

    @property
    def lock_path(self) -> Path:
        """锁文件路径（public API, Stage 4）."""
        return self._lock_path

    @property
    def queue_path(self) -> Path:
        """队列文件路径（public API, Stage 4）."""
        return self._queue_path

    def try_steal_expired_lock(self) -> bool:
        """尝试抢占过期锁（public API, Stage 4）."""
        return self._try_steal_expired_lock()

    def enqueue_request(self, request: LockRequest) -> None:
        """入队等待请求（public API, Stage 4）."""
        self._enqueue_request(request)

    def count_queue(self) -> int:
        """统计队列长度（public API, Stage 4）."""
        return self._count_queue()

    def _try_create_lock(
        self,
        request: LockRequest,
        start_time: float,
        reason: str = "",
    ) -> LockAcquireResult | None:
        """5.58.6：直接 O_EXCL 原子创建锁文件；成功返回结果，锁被占用返回 None。

        5.58.2：创建成功后（已持锁）分配单调递增 fencing token 写入锁内容。
        5.58.3：创建成功后启动 TTL 自动续期 watchdog。
        """
        try:
            fd = os.open(
                str(self._lock_path),
                os.O_CREAT | os.O_EXCL | os.O_RDWR,
                0o600,  # 5.17.12 修复：锁文件权限收紧至 0o600
            )
        except OSError:
            return None
        # 5.169 修复：try/finally 确保 fd 关闭，os.write 抛异常时不泄漏
        try:
            token = next_fencing_token(self._fence_path)
            lock_data = json.dumps(
                {
                    "lock_id": request.lock_id,
                    "owner": request.owner,
                    "priority": request.priority.value,
                    "task": request.task,
                    "acquired_at": datetime.now(UTC).isoformat(),
                    "ttl_seconds": self.DEFAULT_TTL_SECONDS,
                    "fencing_token": token,
                },
                ensure_ascii=False,
            )
            os.write(fd, lock_data.encode("utf-8"))
        finally:
            os.close(fd)

        self._held_lock_id = request.lock_id
        self._held_token = token
        self._start_renewer()
        wait_time = int((time.time() - start_time) * 1000)
        return LockAcquireResult(
            acquired=True,
            lock_id=request.lock_id,
            wait_time_ms=wait_time,
            reason=reason,
            fencing_token=token,
        )

    def _start_renewer(self) -> None:
        """5.58.3：启动 TTL 自动续期 watchdog（TTL/3 周期刷新 acquired_at）。"""
        if self._renewer is not None:
            self._renewer.stop()
        self._renewer = SyncLockRenewer(
            self._refresh_lease,
            self.DEFAULT_TTL_SECONDS / 3,
            name="rollback-lock-renewer",
        )
        self._renewer.start()

    def _stop_renewer(self) -> None:
        if self._renewer is not None:
            self._renewer.stop()
            self._renewer = None

    def _refresh_lease(self) -> bool:
        """5.58.3 续约：持有者身份校验（lock_id + fencing token）通过后刷新 acquired_at。"""
        try:
            lock_data = json.loads(self._lock_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        if lock_data.get("lock_id") != self._held_lock_id or lock_data.get("fencing_token") != self._held_token:
            return False
        lock_data["acquired_at"] = datetime.now(UTC).isoformat()
        tmp_path = self._lock_path.with_name(f"{self._lock_path.name}.{os.getpid()}.tmp")
        try:
            tmp_path.write_text(json.dumps(lock_data, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp_path, self._lock_path)
        except OSError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return False
        return True

    def validate_fencing(self, lock_id: str) -> bool:
        """5.58.2 受保护操作前验证——锁文件仍由本持有者持有（lock_id + fencing token 匹配，未被取代）。"""
        if not lock_id or lock_id != self._held_lock_id:
            return False
        try:
            lock_data = json.loads(self._lock_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        return lock_data.get("lock_id") == lock_id and lock_data.get("fencing_token") == self._held_token

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

        # 5.58.6：直接 O_EXCL 尝试，失败再进入冲突处理（查 stale）
        result = self._try_create_lock(request, start_time)
        if result is not None:
            return result
        return self._handle_lock_conflict(request, start_time, timeout_ms)

    def _handle_lock_conflict(
        self,
        request: LockRequest,
        start_time: float,
        timeout_ms: int,
    ) -> LockAcquireResult:
        self._enqueue_request(request)

        stole_stale = False
        while (time.time() - start_time) * 1000 < timeout_ms:
            # 5.58.6 TOCTOU 修复：直接 O_EXCL 尝试（持有者正常释放后立即可获取），
            # 失败再查 stale——stale 则删除后下轮重试 O_EXCL，消除 os.remove->os.open 两步窗口。
            result = self._try_create_lock(
                request,
                start_time,
                reason="acquired after TTL expiry of previous holder" if stole_stale else "",
            )
            if result is not None:
                self._dequeue_request(request.lock_id)
                return result
            if self._try_steal_expired_lock():
                try:
                    os.remove(str(self._lock_path))
                    stole_stale = True
                except OSError:
                    pass
                continue
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
            # 5.58.3：释放成功后停止续期 watchdog 并清理持有状态
            if self._held_lock_id == lock_id:
                self._stop_renewer()
                self._held_lock_id = None
                self._held_token = 0
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
                # 5.58.3：强制释放后停止续期 watchdog 并清理持有状态
                self._stop_renewer()
                self._held_lock_id = None
                self._held_token = 0
                return LockAcquireResult(
                    acquired=True,
                    lock_id="",
                    wait_time_ms=0,
                    reason="Forced release",
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in rollback_lock", exc_info=True)
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in rollback_lock", exc_info=True)

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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in rollback_lock", exc_info=True)

    def _count_queue(self) -> int:
        self._cleanup_stale_queue_entries()
        if not self._queue_path.exists():
            return 0
        try:
            lines = self._queue_path.read_text(encoding="utf-8").strip().split("\n")
            return len([l for l in lines if l])
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in rollback_lock", exc_info=True)
