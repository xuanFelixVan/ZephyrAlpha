# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.pipeline_lock
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.pipeline.__init__
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
# [A_module] module_id=MOD-INF-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: while True+time.sleep是pipeline锁等待循环，非周期触发

"""
Pipeline Lock — 双管线并发锁
=============================
真源：MOD-INF-009 蓝图 §施工完成标准 第 2 项
对标：K8s ResourceQuota + PodDisruptionBudget + etcd 分布式锁

防止 Line A（生产）和 Line B（审计）同时修改同一文件/层级。
v0.5.0 集成到 PipelineOrchestrator.dispatch()。
v0.8.0 新增 FileLockBackend——跨进程锁，覆盖 Trae+Cursor+RooCode 多 IDE 场景。

使用：
    from zephyr.infrastructure.pipeline.pipeline_lock import PipelineLock, FileLockBackend

    lock = PipelineLock(FileLockBackend())
    result = lock.acquire("task-001", ["src/foo.py"], timeout_s=5.0)
    if result.acquired:
        ...  # 安全执行
        lock.release("task-001")
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import os
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from zephyr.shared.infra.lock import SyncLockRenewer, next_fencing_token  # 5.58.2/5.58.3 fencing+续期共享助手


class LockStatus(str, Enum):
    ACQUIRED = "acquired"
    CONFLICT = "conflict"
    TIMEOUT = "timeout"
    DEADLOCK = "deadlock"


@dataclass
class LockResult:
    """acquire() 返回结果。"""

    acquired: bool
    status: LockStatus
    task_id: str
    locked_files: list[str] = field(default_factory=list)
    conflict_tasks: list[str] = field(default_factory=list)
    waited_ms: int = 0
    fencing_token: int = 0  # 5.58.2：本次获取的 fencing token（0=未分配）


class LockBackend(ABC):
    """锁后端抽象——Memory / SQLite / etcd。"""

    @abstractmethod
    def try_acquire(
        self,
        task_id: str,
        file_paths: list[str],
        layer_locks: list[str] | None = None,
    ) -> LockResult:
        """尝试获取文件锁。非阻塞——立即返回结果。"""
        ...

    @abstractmethod
    def release(self, task_id: str) -> list[str]:
        """释放 task_id 持有的所有锁。返回释放的文件列表。"""
        ...

    @abstractmethod
    def list_locks(self) -> dict[str, list[str]]:
        """查询当前所有锁：{task_id: [file_path, ...]}"""
        ...

    @abstractmethod
    def is_locked(self, file_path: str) -> str | None:
        """查询单文件是否被锁——返回持有者 task_id 或 None。"""
        ...

    @abstractmethod
    def reset(self) -> None:
        """清除所有锁——仅用于测试/灾难恢复。"""
        ...


def _collect_memory_conflicts(
    task_id: str,
    file_paths: list[str],
    layer_locks: list[str] | None,
    file_locks: dict[str, str],
    layer_locks_map: dict[str, str],
) -> list[str]:
    """收集 MemoryLockBackend 的层锁/文件锁冲突 owner 列表（去重，保序）。

    从 try_acquire 抽取——纯数据计算，不依赖 self。
    """
    conflicts: list[str] = []

    for lyr in layer_locks or []:
        owner = layer_locks_map.get(lyr)
        if owner and owner != task_id:
            if owner not in conflicts:
                conflicts.append(owner)

    for fp in file_paths:
        owner = file_locks.get(fp)
        if owner and owner != task_id:
            if owner not in conflicts:
                conflicts.append(owner)
            continue

        for lyr, layer_owner in layer_locks_map.items():
            if lyr in fp and layer_owner and layer_owner != task_id:
                if layer_owner not in conflicts:
                    conflicts.append(layer_owner)

    return conflicts


class MemoryLockBackend(LockBackend):
    """内存锁后端——测试 + 单进程场景。"""

    def __init__(self) -> None:
        self._file_locks: dict[str, str] = {}
        self._task_files: dict[str, set[str]] = {}
        self._layer_locks: dict[str, str] = {}
        self._lock = threading.RLock()

    def try_acquire(
        self,
        task_id: str,
        file_paths: list[str],
        layer_locks: list[str] | None = None,
    ) -> LockResult:
        with self._lock:
            conflicts = _collect_memory_conflicts(
                task_id,
                file_paths,
                layer_locks,
                self._file_locks,
                self._layer_locks,
            )

            if conflicts:
                return LockResult(
                    acquired=False,
                    status=LockStatus.CONFLICT,
                    task_id=task_id,
                    conflict_tasks=sorted(conflicts),
                )

            for fp in file_paths:
                self._file_locks[fp] = task_id
            for lyr in layer_locks or []:
                self._layer_locks[lyr] = task_id
            self._task_files.setdefault(task_id, set()).update(file_paths)

            return LockResult(
                acquired=True,
                status=LockStatus.ACQUIRED,
                task_id=task_id,
                locked_files=sorted(file_paths),
            )

    def release(self, task_id: str) -> list[str]:
        with self._lock:
            released: list[str] = []
            files = self._task_files.pop(task_id, set())
            for fp in list(files):
                if self._file_locks.get(fp) == task_id:
                    del self._file_locks[fp]
                    released.append(fp)
            layer_owners = list(self._layer_locks.items())
            for lyr, owner in layer_owners:
                if owner == task_id:
                    del self._layer_locks[lyr]
            return sorted(released)

    def list_locks(self) -> dict[str, list[str]]:
        with self._lock:
            result: dict[str, list[str]] = {}
            for fp, owner in self._file_locks.items():
                result.setdefault(owner, []).append(fp)
            return result

    def is_locked(self, file_path: str) -> str | None:
        with self._lock:
            return self._file_locks.get(file_path)

    def reset(self) -> None:
        """清除所有锁——仅限测试/紧急恢复使用，运行时调用会导致锁泄漏。"""
        with self._lock:
            self._file_locks.clear()
            self._task_files.clear()
            self._layer_locks.clear()


class FileLockBackend(LockBackend):
    """跨进程文件锁后端——覆盖 Trae+Cursor+RooCode 多 IDE 并发场景。

    基于原子目录创建（os.mkdir）实现互斥：
      - 锁目录路径 = lock_root / sanitized_file_path.lock
      - 目录内写入 owner.json（{task_id, pid, timestamp}）
      - 获取锁前检测 stale lock（PID 已死 或 TTL 过期 -> 自动清理）

    v0.9.0 B167：新增 TTL 过期自动释放——锁超过 TTL 秒自动视为 stale。

    5.58.2：owner.json 含单调递增 fencing token（.fencing_counter 持久计数器），
    validate_fencing() 供受保护操作前验证未被取代。
    5.58.3：SyncLockRenewer 按 TTL/3 周期刷新 owner.json timestamp，持有者存活期间锁不过期。
    5.58.9：两阶段锁定——冲突时回滚本次调用已获取的锁目录，杜绝部分失败泄漏。
    """

    _DEFAULT_LOCK_ROOT = ".pipeline_locks"
    _DEFAULT_LOCK_TTL_S = 300.0

    def __init__(self, lock_root: str | None = None, lock_ttl_s: float | None = None) -> None:
        self._lock_root = lock_root or os.path.join(os.getcwd(), self._DEFAULT_LOCK_ROOT)
        self._lock_ttl_s = lock_ttl_s or self._DEFAULT_LOCK_TTL_S
        self._thread_lock = threading.RLock()
        self._fence_counter = os.path.join(self._lock_root, ".fencing_counter")
        self._task_tokens: dict[str, int] = {}
        self._renewers: dict[str, SyncLockRenewer] = {}

    @staticmethod
    def _sanitize_path(path: str) -> str:
        sanitized = path.replace("\\", ".").replace("/", ".").replace("..", "_dotdot_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "._-")
        return sanitized.lower()[:120]

    @staticmethod
    def _pid_alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _lock_dir(self, file_path: str) -> str:
        return os.path.join(self._lock_root, self._sanitize_path(file_path) + ".lock")

    def _write_owner(self, lock_dir: str, task_id: str, fencing_token: int = 0) -> None:
        import json

        os.makedirs(lock_dir, exist_ok=True)
        owner_file = os.path.join(lock_dir, "owner.json")
        tmp_path = f"{owner_file}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(
                    {"task_id": task_id, "pid": os.getpid(), "timestamp": time.time(), "fencing_token": fencing_token},
                    fh,
                )
            os.replace(tmp_path, owner_file)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def _read_owner(self, lock_dir: str) -> dict | None:
        import json

        owner_file = os.path.join(lock_dir, "owner.json")
        if not os.path.isfile(owner_file):
            return None
        try:
            with open(owner_file, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:  # 5.70.4 修复：异常路径添加日志，区分"真阴性"和"异常降级"  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("_read_owner failed: %s", e, exc_info=True)
            return None

    def _is_stale(self, lock_dir: str) -> bool:
        owner = self._read_owner(lock_dir)
        if owner is None:
            return True
        ts = owner.get("timestamp", 0.0)
        if time.time() - ts > self._lock_ttl_s:
            return True
        pid = owner.get("pid", -1)
        if pid < 0:
            return False
        return not self._pid_alive(pid)

    def _cleanup_stale(self, lock_dir: str) -> bool:
        import shutil

        try:
            shutil.rmtree(lock_dir, ignore_errors=True)
            return True
        except Exception as e:  # 5.70.4 修复：异常路径添加日志，区分"真阴性"和"异常降级"  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("_cleanup_stale failed: %s", e, exc_info=True)
            return False

    def _ensure_root(self) -> None:
        os.makedirs(self._lock_root, exist_ok=True)

    def _record_conflict_from_dir(self, lock_dir: str, task_id: str, conflicts: list[str]) -> None:
        """读取锁目录 owner 并按需记录冲突任务（去重）。

        从 try_acquire 抽取——3 处重复的冲突记录逻辑。
        """
        owner = self._read_owner(lock_dir)
        conflict_task = owner.get("task_id", "unknown") if owner else "unknown"
        if conflict_task != task_id and conflict_task not in conflicts:
            conflicts.append(conflict_task)

    def _rollback_acquired(self, acquired_dirs: list[str], task_id: str) -> None:
        """5.58.9 两阶段锁定回滚——冲突时撤销本次调用已获取的锁目录。

        仅回滚 owner 仍为 task_id 的目录（防误删他人锁）。
        """
        import shutil

        for lock_dir in acquired_dirs:
            owner = self._read_owner(lock_dir)
            if owner is not None and owner.get("task_id") == task_id:
                shutil.rmtree(lock_dir, ignore_errors=True)

    def _ensure_renewer(self, task_id: str) -> None:
        """5.58.3 启动任务级续期 watchdog（已在运行则复用）。"""
        if task_id in self._renewers:
            return
        renewer = SyncLockRenewer(
            lambda: self._refresh_task_leases(task_id),
            self._lock_ttl_s / 3,
            name=f"pipeline-lock-renewer-{task_id[:16]}",
        )
        self._renewers[task_id] = renewer
        renewer.start()

    def _refresh_task_leases(self, task_id: str) -> bool:
        """5.58.3 续约——刷新本任务全部锁目录的 timestamp。

        持有者身份校验（task_id + fencing token）通过才刷新；
        本任务已无持有锁时返回 False 让 watchdog 自动停止。
        注意：watchdog 线程内运行，禁止获取 self._thread_lock
        （release() 持锁 join watchdog，互相等待会死锁）。
        """
        if not os.path.isdir(self._lock_root):
            return False
        found = False
        expected_token = self._task_tokens.get(task_id, 0)
        for entry in os.listdir(self._lock_root):
            lock_dir = os.path.join(self._lock_root, entry)
            if not os.path.isdir(lock_dir) or not entry.endswith(".lock"):
                continue
            owner = self._read_owner(lock_dir)
            if owner is None or owner.get("task_id") != task_id:
                continue
            if owner.get("fencing_token", 0) != expected_token:
                continue
            found = True
            self._write_owner(lock_dir, task_id, fencing_token=expected_token)
        return found

    def validate_fencing(self, task_id: str, fencing_token: int) -> bool:
        """5.58.2 受保护操作前验证——本任务持有的锁全部仍带有给定 fencing token（未被取代）。"""
        with self._thread_lock:
            if not os.path.isdir(self._lock_root):
                return False
            held = 0
            for entry in os.listdir(self._lock_root):
                lock_dir = os.path.join(self._lock_root, entry)
                if not os.path.isdir(lock_dir) or not entry.endswith(".lock"):
                    continue
                owner = self._read_owner(lock_dir)
                if owner is not None and owner.get("task_id") == task_id:
                    if owner.get("fencing_token", 0) != fencing_token:
                        return False
                    held += 1
            return held > 0

    def try_acquire(
        self,
        task_id: str,
        file_paths: list[str],
        layer_locks: list[str] | None = None,
    ) -> LockResult:
        with self._thread_lock:
            self._ensure_root()
            conflicts: list[str] = []

            all_targets: list[str] = list(file_paths)
            for lyr in layer_locks or []:
                all_targets.append(f"LAYER:{lyr}")

            # Phase 1（5.58.9）：只读检查全部目标——stale 先清理，活跃持有者记冲突
            for fp in all_targets:
                lock_dir = self._lock_dir(fp)
                if os.path.isdir(lock_dir):
                    if self._is_stale(lock_dir):
                        self._cleanup_stale(lock_dir)
                    else:
                        self._record_conflict_from_dir(lock_dir, task_id, conflicts)

            if conflicts:
                return LockResult(
                    acquired=False,
                    status=LockStatus.CONFLICT,
                    task_id=task_id,
                    conflict_tasks=sorted(conflicts),
                )

            # Phase 2（5.58.9）：原子创建全部锁目录；任一失败 -> 回滚已获取锁
            acquired_dirs: list[str] = []
            for fp in all_targets:
                lock_dir = self._lock_dir(fp)
                try:
                    os.makedirs(lock_dir, exist_ok=False)
                    self._write_owner(lock_dir, task_id)
                    acquired_dirs.append(lock_dir)
                    continue
                except FileExistsError:
                    pass
                # 并发竞争：他人捷足先登——若为 stale 则清理后重试一次
                if self._is_stale(lock_dir):
                    self._cleanup_stale(lock_dir)
                    try:
                        os.makedirs(lock_dir, exist_ok=False)
                        self._write_owner(lock_dir, task_id)
                        acquired_dirs.append(lock_dir)
                        continue
                    except FileExistsError:
                        pass
                self._record_conflict_from_dir(lock_dir, task_id, conflicts)

            if conflicts:
                self._rollback_acquired(acquired_dirs, task_id)
                return LockResult(
                    acquired=False,
                    status=LockStatus.CONFLICT,
                    task_id=task_id,
                    conflict_tasks=sorted(conflicts),
                )

            # 5.58.2：全部获取成功后分配单调递增 fencing token 并写回 owner.json
            token = next_fencing_token(self._fence_counter)
            for lock_dir in acquired_dirs:
                self._write_owner(lock_dir, task_id, fencing_token=token)
            self._task_tokens[task_id] = token
            # 5.58.3：持有者存活期间自动续期
            self._ensure_renewer(task_id)

            return LockResult(
                acquired=True,
                status=LockStatus.ACQUIRED,
                task_id=task_id,
                locked_files=sorted(all_targets),
                fencing_token=token,
            )

    def release(self, task_id: str) -> list[str]:
        import shutil

        with self._thread_lock:
            renewer = self._renewers.pop(task_id, None)
            if renewer is not None:
                renewer.stop()
            self._task_tokens.pop(task_id, None)

            released: list[str] = []
            if not os.path.isdir(self._lock_root):
                return released
            for entry in os.listdir(self._lock_root):
                lock_dir = os.path.join(self._lock_root, entry)
                if not os.path.isdir(lock_dir) or not entry.endswith(".lock"):
                    continue
                owner = self._read_owner(lock_dir)
                if owner is not None and owner.get("task_id") == task_id:
                    try:
                        shutil.rmtree(lock_dir, ignore_errors=True)
                        released.append(entry[:-5])  # strip ".lock"
                    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                        logger.warning("suppressed error in pipeline_lock", exc_info=True)

            return sorted(released)

    def list_locks(self) -> dict[str, list[str]]:
        with self._thread_lock:
            result: dict[str, list[str]] = {}
            if not os.path.isdir(self._lock_root):
                return result
            for entry in os.listdir(self._lock_root):
                lock_dir = os.path.join(self._lock_root, entry)
                if not os.path.isdir(lock_dir) or not entry.endswith(".lock"):
                    continue
                owner = self._read_owner(lock_dir)
                if owner is not None:
                    tid = owner.get("task_id", "unknown")
                    result.setdefault(tid, []).append(entry[:-5])
            return result

    def is_locked(self, file_path: str) -> str | None:
        with self._thread_lock:
            lock_dir = self._lock_dir(file_path)
            if not os.path.isdir(lock_dir):
                return None
            if self._is_stale(lock_dir):
                return None
            owner = self._read_owner(lock_dir)
            return owner.get("task_id") if owner else None

    def reset(self) -> None:
        """清除所有锁——仅限测试/紧急恢复使用，运行时调用会导致锁泄漏。"""
        import shutil

        with self._thread_lock:
            for renewer in self._renewers.values():
                renewer.stop()
            self._renewers.clear()
            self._task_tokens.clear()
            if os.path.isdir(self._lock_root):
                for entry in os.listdir(self._lock_root):
                    path = os.path.join(self._lock_root, entry)
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                    elif os.path.isfile(path):
                        try:
                            os.unlink(path)
                        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                            logger.debug("suppressed error in pipeline_lock", exc_info=True)


class PipelineLock:
    """双管线并发锁——Orchestrator 集成入口。

    Parameters
    ----------
    backend : LockBackend | None
        锁后端。None 时使用 MemoryLockBackend（测试/单进程）。
    """

    def __init__(self, backend: LockBackend | None = None) -> None:
        self._backend = backend or MemoryLockBackend()

    @property
    def backend(self) -> LockBackend:
        return self._backend

    def acquire(
        self,
        task_id: str,
        file_paths: list[str],
        *,
        timeout_s: float = 10.0,
        poll_interval_s: float = 0.5,
        layer_locks: list[str] | None = None,
    ) -> LockResult:
        """尝试获取文件锁——支持等待重试。

        Parameters
        ----------
        task_id : str
            请求锁的任务 ID。
        file_paths : list[str]
            需要锁定的文件路径列表。
        timeout_s : float
            最长等待时间（秒）。0 = 非阻塞。
        poll_interval_s : float
            重试间隔。
        layer_locks : list[str] | None
            层级锁——如 ["D_DATA/signals"]。锁定整个层级目录。
        """
        deadline = time.monotonic() + timeout_s
        waited_ms = 0

        while True:
            result = self._backend.try_acquire(task_id, file_paths, layer_locks=layer_locks)

            if result.acquired:
                result.waited_ms = waited_ms
                return result

            if timeout_s <= 0:
                return result

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return LockResult(
                    acquired=False,
                    status=LockStatus.TIMEOUT,
                    task_id=task_id,
                    conflict_tasks=result.conflict_tasks,
                    waited_ms=waited_ms,
                )

            sleep_ms = int(min(poll_interval_s, remaining) * 1000)
            time.sleep(sleep_ms / 1000)
            waited_ms += sleep_ms

    def release(self, task_id: str) -> list[str]:
        """释放该任务持有的所有锁。"""
        return self._backend.release(task_id)

    def conflicts(self, task_id: str, file_paths: list[str]) -> list[str]:
        """检查 file_paths 是否与其他任务冲突。"""
        conflicts: set[str] = set()
        for fp in file_paths:
            owner = self._backend.is_locked(fp)
            if owner and owner != task_id:
                conflicts.add(owner)
        return sorted(conflicts)

    def list_all(self) -> dict[str, list[str]]:
        """查询所有当前持有的锁。"""
        return self._backend.list_locks()

    def reset(self) -> None:
        self._backend.reset()
