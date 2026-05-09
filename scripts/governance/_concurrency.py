"""
_concurrency.py — ZCL 并发基础设施（Phase 3a → 3b → 3c）
==========================================================
真源：MOD-INF-005 §5.7-§5.10 + §35 ZCL 并发架构
对标：Netflix Hystrix Bulkhead / K8s APF / SQLite WAL / MongoDB Sharding / Google SRE Throttling
Phase: 3b+3c 完整版

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


模块职责：
  ProcessLock          — L0 全局进程锁
  DimensionLock        — L1 维度级锁
  FileLock             — L2 文件级锁
  LockManager          — 统一 L0/L1/L2 锁管理
  BulkheadExecutor     — 四池隔离执行器（完整路由 + Circuit Breaker）
  ScanCache            — 文件级 LRU 扫描缓存
  TieredTimeout        — S0-S3 分级超时
  TokenBucket          — 令牌桶限流器
  AdmissionController  — P0/P1/P2 优先级准入控制
  ShardRouter          — 模块级分片路由 (hash(module_id) % N)
  CircuitBreaker       — 完整三级状态机 (CLOSED→OPEN→HALF_OPEN)

使用：
  from _concurrency import BulkheadExecutor, ProcessLock, LockManager, ...
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
_DEFAULT_LOCK_DIR = Path(__file__).resolve().parent.parent.parent / "meta"
_LOCK_FILE = "run_all.lock"

L0_LOCK_TIMEOUT_SECONDS = 30
L0_LOCK_POLL_INTERVAL_SECONDS = 0.5
L0_LOCK_STALE_SECONDS = 120

# Phase 3b+3c: 四池完整分离，各自独立 worker + 超时 + 熔断
POOL_CONFIGS: dict[str, dict[str, Any]] = {
    "quick": {
        "max_workers": 12,
        "dimensions": frozenset({"D1", "D2", "D3", "D4", "D8"}),
        "tags": frozenset({"Quick"}),
        "circuit_breaker_threshold": 3,
        "circuit_breaker_ttl_s": 30,
    },
    "content_analysis": {
        "max_workers": 6,
        "dimensions": frozenset({"D5", "D6", "D7", "D11"}),
        "tags": frozenset({"Security", "Critical", "Periodic"}),
        "circuit_breaker_threshold": 5,
        "circuit_breaker_ttl_s": 60,
    },
    "ai_generated": {
        "max_workers": 4,
        "dimensions": frozenset({"D9", "D10", "D12"}),
        "tags": frozenset({"AI-Generated"}),
        "circuit_breaker_threshold": 2,
        "circuit_breaker_ttl_s": 120,
    },
    "disruptive": {
        "max_workers": 2,
        "dimensions": frozenset(),
        "tags": frozenset({"Disruptive"}),
        "circuit_breaker_threshold": 1,
        "circuit_breaker_ttl_s": 60,
    },
}


class TimeoutTier(str, Enum):
    """S0-S3 分级超时——对齐 K8s QoS Classes。"""
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"


# 维度 → 超时级别映射（蓝图 §5.8）
_DIMENSION_TIMEOUT_TIER: dict[str, TimeoutTier] = {
    "D1": TimeoutTier.S0,   # Quick
    "D2": TimeoutTier.S0,   # Quick
    "D3": TimeoutTier.S0,   # Quick
    "D4": TimeoutTier.S0,   # Quick
    "D8": TimeoutTier.S0,   # Quick
    "D5": TimeoutTier.S1,   # Content Analysis
    "D6": TimeoutTier.S1,   # Content Analysis
    "D7": TimeoutTier.S1,   # Content Analysis
    "D11": TimeoutTier.S1,  # Content Analysis
    "D9": TimeoutTier.S2,   # AI-Generated
    "D10": TimeoutTier.S2,  # AI-Generated
    "D12": TimeoutTier.S2,  # AI-Generated
}

# 池 → 默认超时级别
TAG_TIER_MAP: dict[str, TimeoutTier] = {
    "Quick": TimeoutTier.S0,
    "Security": TimeoutTier.S1,
    "Critical": TimeoutTier.S1,
    "Periodic": TimeoutTier.S1,
    "AI-Generated": TimeoutTier.S2,
    "Disruptive": TimeoutTier.S3,
}

# 分级超时上限（蓝图 §5.8）
TIER_TIMEOUT_SECONDS: dict[TimeoutTier, int] = {
    TimeoutTier.S0: 10,
    TimeoutTier.S1: 60,
    TimeoutTier.S2: 180,
    TimeoutTier.S3: 120,
}

TIER_DIMENSION_TOTAL_TIMEOUT: dict[TimeoutTier, int] = {
    TimeoutTier.S0: 120,
    TimeoutTier.S1: 300,
    TimeoutTier.S2: 600,
    TimeoutTier.S3: 240,
}

GLOBAL_HARD_TIMEOUT_SECONDS = 900

# ---------------------------------------------------------------------------
# ProcessLock — L0 全局进程锁
# ---------------------------------------------------------------------------

@dataclass
class LockAcquireResult:
    acquired: bool
    waited_s: float = 0.0
    holder_pid: int | None = None
    holder_agent_id: str | None = None
    reason: str = ""


class ProcessLock:
    """L0 全局进程锁——基于 PID 文件的跨进程互斥锁。

    保证同一时间只有一个 run_all.py 实例在运行。
    对标：K8s ConfigMap-based leader election。

    锁文件格式（JSON）：
        {"pid": 12345, "agent_id": "trae-session-01",
         "acquired_at": "2026-05-09T14:30:45+08:00"}

    使用：
        lock = ProcessLock(agent_id="trae-session-01")
        result = lock.acquire()
        if result.acquired:
            try:
                ...  # 安全执行
            finally:
                lock.release()
        else:
            print(f"被 {result.holder_agent_id} (PID {result.holder_pid}) 占用")
    """

    def __init__(self, lock_dir: Path | None = None, agent_id: str = "unknown"):
        self._lock_dir = lock_dir or _DEFAULT_LOCK_DIR
        self._lock_path = self._lock_dir / _LOCK_FILE
        self._agent_id = agent_id
        self._acquired = False

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def acquire(self, timeout_s: float = L0_LOCK_TIMEOUT_SECONDS) -> LockAcquireResult:
        """尝试获取全局锁。

        Args:
            timeout_s: 最长等待时间（秒），超时返回未获取

        Returns:
            LockAcquireResult: 获取结果
        """
        self._lock_dir.mkdir(parents=True, exist_ok=True)
        start = time.monotonic()

        while True:
            elapsed = time.monotonic() - start
            if elapsed >= timeout_s:
                holder = self._read_lock()
                return LockAcquireResult(
                    acquired=False,
                    waited_s=round(elapsed, 1),
                    holder_pid=holder.get("pid"),
                    holder_agent_id=holder.get("agent_id"),
                    reason="timeout",
                )

            if self._try_write_lock():
                self._acquired = True
                return LockAcquireResult(
                    acquired=True,
                    waited_s=round(elapsed, 1),
                )

            holder = self._read_lock()
            if not holder:
                self._clear_stale_lock()
                continue

            pid = holder.get("pid")
            if pid is not None and not _is_pid_alive(pid):
                self._clear_stale_lock()
                continue

            time.sleep(L0_LOCK_POLL_INTERVAL_SECONDS)

    def release(self) -> None:
        if self._acquired and self._lock_path.exists():
            try:
                holder = self._read_lock()
                if holder and holder.get("pid") == os.getpid():
                    self._lock_path.unlink()
            except OSError:
                pass
            self._acquired = False

    def _try_write_lock(self) -> bool:
        try:
            fd = os.open(
                str(self._lock_path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o644,
            )
            data = json.dumps({
                "pid": os.getpid(),
                "agent_id": self._agent_id,
                "acquired_at": datetime.now(UTC).isoformat(),
            })
            os.write(fd, data.encode("utf-8"))
            os.close(fd)
            return True
        except FileExistsError:
            return False
        except OSError:
            return False

    def _read_lock(self) -> dict[str, Any] | None:
        if not self._lock_path.exists():
            return None
        try:
            content = self._lock_path.read_text(encoding="utf-8")
            return json.loads(content)
        except (json.JSONDecodeError, OSError):
            return None

    def _clear_stale_lock(self) -> None:
        try:
            self._lock_path.unlink()
        except OSError:
            pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()


def _is_pid_alive(pid: int) -> bool:
    """检查 PID 是否存活（跨平台）。"""
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x0400, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        else:
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError):
        return False


# ---------------------------------------------------------------------------
# BulkheadExecutor — 四池隔离执行器
# ---------------------------------------------------------------------------

class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class _PoolState:
    config: dict
    executor: ThreadPoolExecutor
    circuit_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    circuit_open_since: float = 0.0
    total_submitted: int = 0
    total_completed: int = 0
    total_failed: int = 0


class BulkheadExecutor:
    """四池隔离执行器——Quick / ContentAnalysis / AI-Generated / Disruptive。

    池间完全隔离：Quick Pool 的 worker 永不执行 AI-Generated 脚本。
    对标 Netflix Hystrix Bulkhead Pattern。

    使用：
        executor = BulkheadExecutor()
        results = executor.dispatch(script_tasks)
    """

    def __init__(self, pool_override: dict[str, dict] | None = None):
        self._pools: dict[str, _PoolState] = {}
        configs = pool_override or POOL_CONFIGS

        for pool_name, config in configs.items():
            self._pools[pool_name] = _PoolState(
                config=config,
                executor=ThreadPoolExecutor(
                    max_workers=config["max_workers"],
                    thread_name_prefix=f"zcl-{pool_name}",
                ),
            )

    def _route_to_pool(self, script_name: str, dimensions: set[str], tags: set[str]) -> str:
        """根据维度 + 标签 + 脚本名前缀路由到正确的执行池。

        优先级：tags > dimensions > 脚本名前缀
        """
        sn_lower = script_name.lower()
        is_writable = any(
            sn_lower.startswith(p) or f"/{p}" in sn_lower
            for p in ("fix_", "generate_", "register_")
        )

        if is_writable:
            return "disruptive"

        for pool_name in ("ai_generated", "content_analysis", "quick"):
            pool_config = self._pools[pool_name].config
            if tags & pool_config["tags"]:
                return pool_name
            if dimensions & pool_config["dimensions"]:
                return pool_name

        return "content_analysis"

    def _check_circuit(self, pool_name: str) -> bool:
        """检查池的熔断器状态。返回 True 表示允许提交。"""
        state = self._pools[pool_name]
        if state.circuit_state == CircuitState.CLOSED:
            return True
        if state.circuit_state == CircuitState.OPEN:
            ttl = state.config["circuit_breaker_ttl_s"]
            if time.monotonic() - state.circuit_open_since >= ttl:
                state.circuit_state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def _record_result(self, pool_name: str, success: bool) -> None:
        state = self._pools[pool_name]
        if success:
            if state.circuit_state == CircuitState.HALF_OPEN:
                state.consecutive_failures = 0
                state.circuit_state = CircuitState.CLOSED
            else:
                state.consecutive_failures = 0
        else:
            state.consecutive_failures += 1
            threshold = state.config["circuit_breaker_threshold"]
            if state.consecutive_failures >= threshold:
                state.circuit_state = CircuitState.OPEN
                state.circuit_open_since = time.monotonic()

    def dispatch(
        self,
        script_tasks: list[tuple[str, dict, Callable]],
        on_complete: Callable | None = None,
    ) -> dict[str, Any]:
        """分发脚本到对应的 Bulkhead 池并行执行。

        Args:
            script_tasks: [(script_name, meta, execute_fn), ...]
                          execute_fn: (script_name, meta) -> result dict
            on_complete: 可选——每个脚本完成时的回调

        Returns:
            dict: {"results": [...], "pools": {...}, "skipped": [...]}
        """
        results: list[dict] = []
        skipped: list[dict] = []
        futures: dict[Future, tuple[str, str]] = {}
        pool_submits: dict[str, int] = {pn: 0 for pn in self._pools}

        for script_name, meta, execute_fn in script_tasks:
            dimensions = {d.value for d in meta.get("dimensions", [])}
            tags = frozenset(meta.get("tags", []))

            pool_name = self._route_to_pool(script_name, dimensions, tags)

            if not self._check_circuit(pool_name):
                skipped.append({
                    "script_name": script_name,
                    "pool": pool_name,
                    "reason": "circuit_open",
                })
                continue

            pool = self._pools[pool_name]
            future = pool.executor.submit(execute_fn, script_name, meta)
            futures[future] = (script_name, pool_name)
            pool.total_submitted += 1
            pool_submits[pool_name] += 1

        for future in as_completed(futures):
            script_name, pool_name = futures[future]
            try:
                result = future.result()
                success = not result.get("is_failed", False)
                self._record_result(pool_name, success)
                self._pools[pool_name].total_completed += 1
                results.append(result)
                if on_complete:
                    on_complete(result)
            except Exception:
                self._record_result(pool_name, False)
                self._pools[pool_name].total_failed += 1
                results.append({
                    "script_name": script_name,
                    "exit_code": 2,
                    "findings": [],
                    "is_failed": True,
                    "pool": pool_name,
                })

        pool_stats = {}
        for pn, ps in self._pools.items():
            pool_stats[pn] = {
                "submitted": pool_submits[pn],
                "total_completed": ps.total_completed,
                "total_failed": ps.total_failed,
                "circuit_state": ps.circuit_state.value,
            }

        return {
            "results": results,
            "pools": pool_stats,
            "skipped": skipped,
        }

    def shutdown(self) -> None:
        for pool_state in self._pools.values():
            pool_state.executor.shutdown(wait=True)


# ---------------------------------------------------------------------------
# ScanCache — 文件级 LRU 扫描缓存
# ---------------------------------------------------------------------------

class ScanCache:
    """文件内容解析的 LRU 缓存——减少重复 subprocess 调用和文件 I/O。

    缓存 Key: (file_path, mtime_ns, sha256_prefix)
    缓存 Value: parsed result (dict or str)

    跨 agent 缓存共享时通过 mtime 竞态检查保证一致性。

    使用：
        cache = ScanCache(max_entries=500)
        result = cache.get_or_compute("src/foo.py", lambda: expensive_parse("src/foo.py"))
    """

    def __init__(self, max_entries: int = 500):
        self._max_entries = max_entries
        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.Lock()
        self._hits: int = 0
        self._misses: int = 0

    def _make_key(self, file_path: str | Path) -> str:
        fp = Path(file_path)
        if not fp.exists():
            return str(fp)
        stat = fp.stat()
        return f"{fp}:{stat.st_mtime_ns}"

    def get(self, file_path: str | Path) -> Any | None:
        key = self._make_key(file_path)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._hits += 1
                return deepcopy(self._cache[key])
            self._misses += 1
            return None

    def set(self, file_path: str | Path, value: Any) -> None:
        key = self._make_key(file_path)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = deepcopy(value)
            while len(self._cache) > self._max_entries:
                self._cache.popitem(last=False)

    def get_or_compute(self, file_path: str | Path, compute_fn: Callable[[], Any]) -> Any:
        cached = self.get(file_path)
        if cached is not None:
            return cached
        value = compute_fn()
        self.set(file_path, value)
        return value

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def stats(self) -> dict:
        with self._lock:
            return {
                "entries": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self.hit_rate, 3),
            }

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0


# ---------------------------------------------------------------------------
# TieredTimeout — S0-S3 分级超时
# ---------------------------------------------------------------------------

class TieredTimeout:
    """S0-S3 分级超时计算器。

    根据维度/标签确定超时级别，返回对应的单脚本超时 + 维度总超时。

    使用：
        tt = TieredTimeout()
        tier = tt.classify(dimensions={"D1"}, tags={"Quick"})
        script_timeout = tt.script_timeout(tier)
        total_timeout = tt.dimension_total_timeout(tier)
    """

    @staticmethod
    def classify(dimensions: set[str], tags: set[str]) -> TimeoutTier:
        highest_tier = TimeoutTier.S2

        for tag in tags:
            tier = TAG_TIER_MAP.get(tag)
            if tier is not None and tier.value < highest_tier.value:
                highest_tier = tier

        for dim in dimensions:
            tier = _DIMENSION_TIMEOUT_TIER.get(dim)
            if tier is not None and tier.value < highest_tier.value:
                highest_tier = tier

        return highest_tier

    @staticmethod
    def script_timeout(tier: TimeoutTier) -> int:
        return TIER_TIMEOUT_SECONDS.get(tier, 60)

    @staticmethod
    def dimension_total_timeout(tier: TimeoutTier) -> int:
        return TIER_DIMENSION_TOTAL_TIMEOUT.get(tier, 300)


# ---------------------------------------------------------------------------
# Checkpoint — 扫描断点续传
# ---------------------------------------------------------------------------

@dataclass
class ScanCheckpoint:
    session_id: str
    completed_dimensions: list[str] = field(default_factory=list)
    current_dimension: str = ""
    findings_count: int = 0
    elapsed_seconds: float = 0.0
    timestamp: str = ""
    agent_id: str = "unknown"
    file_snapshots: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "completed_dimensions": self.completed_dimensions,
            "current_dimension": self.current_dimension,
            "findings_count": self.findings_count,
            "elapsed_seconds": round(self.elapsed_seconds, 1),
            "timestamp": self.timestamp or datetime.now(UTC).isoformat(),
            "agent_id": self.agent_id,
            "file_snapshots": self.file_snapshots,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScanCheckpoint":
        return cls(
            session_id=data.get("session_id", ""),
            completed_dimensions=data.get("completed_dimensions", []),
            current_dimension=data.get("current_dimension", ""),
            findings_count=data.get("findings_count", 0),
            elapsed_seconds=data.get("elapsed_seconds", 0.0),
            timestamp=data.get("timestamp", ""),
            agent_id=data.get("agent_id", "unknown"),
            file_snapshots=data.get("file_snapshots", {}),
        )


def load_checkpoint(checkpoint_path: Path) -> ScanCheckpoint | None:
    if not checkpoint_path.exists():
        return None
    try:
        data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        return ScanCheckpoint.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return None


def save_checkpoint(checkpoint: ScanCheckpoint, checkpoint_path: Path) -> None:
    checkpoint.timestamp = datetime.now(UTC).isoformat()
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps(checkpoint.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_checkpoint_stale(checkpoint: ScanCheckpoint, max_age_days: int = 30) -> bool:
    if not checkpoint.timestamp:
        return True
    try:
        ts = datetime.fromisoformat(checkpoint.timestamp)
        age = datetime.now(UTC) - ts.replace(tzinfo=UTC) if ts.tzinfo is None else datetime.now(UTC) - ts
        return age.days > max_age_days
    except ValueError:
        return True


# ===========================================================================
# Phase 3b: L1 维度锁 + L2 文件锁 + LockManager
# ===========================================================================

@dataclass
class LockResult:
    acquired: bool
    level: str = ""
    key: str = ""
    waited_s: float = 0.0
    reason: str = ""

    def __bool__(self) -> bool:
        return self.acquired


class DimensionLock:
    """L1 维度级锁——SQLite WAL advisory lock per dimension。

    同维度串行执行，不同维度可完全并行。
    锁文件：meta/locks/dim_{D1}.lock (JSON: {pid, agent_id, dimension, acquired_at})
    """

    _LOCK_TIMEOUT_S = 10
    _POLL_INTERVAL_S = 0.2
    _STALE_S = 60

    def __init__(self, lock_dir: Path | None = None):
        self._lock_dir = (lock_dir or _DEFAULT_LOCK_DIR) / "locks"
        self._lock_dir.mkdir(parents=True, exist_ok=True)

    def acquire(self, dimension: str, agent_id: str = "unknown", timeout_s: float | None = None) -> LockResult:
        timeout = timeout_s if timeout_s is not None else self._LOCK_TIMEOUT_S
        lock_path = self._lock_dir / f"dim_{dimension}.lock"
        start = time.monotonic()

        while True:
            elapsed = time.monotonic() - start
            if elapsed >= timeout:
                holder = self._read_lock(lock_path)
                return LockResult(False, level="L1", key=dimension, waited_s=round(elapsed, 1),
                                  reason=f"timeout ({timeout}s), holder={holder}")

            if self._try_write_lock(lock_path, dimension, agent_id):
                return LockResult(True, level="L1", key=dimension, waited_s=round(elapsed, 1))

            holder = self._read_lock(lock_path)
            if holder and not _is_pid_alive(holder.get("pid", -1)):
                lock_path.unlink(missing_ok=True)
                continue

            time.sleep(self._POLL_INTERVAL_S)

    def release(self, dimension: str) -> None:
        lock_path = self._lock_dir / f"dim_{dimension}.lock"
        lock_path.unlink(missing_ok=True)

    def _try_write_lock(self, lock_path: Path, dimension: str, agent_id: str) -> bool:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            data = json.dumps({"pid": os.getpid(), "agent_id": agent_id, "dimension": dimension,
                               "acquired_at": datetime.now(UTC).isoformat()})
            os.write(fd, data.encode("utf-8"))
            os.close(fd)
            return True
        except (FileExistsError, OSError):
            return False

    def _read_lock(self, lock_path: Path) -> dict[str, Any] | None:
        if not lock_path.exists():
            return None
        try:
            return json.loads(lock_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None


class FileLock:
    """L2 文件级锁——按 file_path 哈希为 key 的 PID 文件锁。

    同一文件读写互斥，不同文件完全并行。
    锁文件：meta/locks/file_{hash}.lock
    """

    _LOCK_TIMEOUT_S = 5
    _POLL_INTERVAL_S = 0.1
    _STALE_S = 30

    def __init__(self, lock_dir: Path | None = None):
        self._lock_dir = (lock_dir or _DEFAULT_LOCK_DIR) / "locks"
        self._lock_dir.mkdir(parents=True, exist_ok=True)

    def _file_key(self, file_path: str | Path) -> str:
        return hashlib.sha256(str(file_path).encode()).hexdigest()[:12]

    def acquire(self, file_path: str | Path, agent_id: str = "unknown", timeout_s: float | None = None) -> LockResult:
        timeout = timeout_s if timeout_s is not None else self._LOCK_TIMEOUT_S
        key = self._file_key(file_path)
        lock_path = self._lock_dir / f"file_{key}.lock"
        start = time.monotonic()

        while True:
            elapsed = time.monotonic() - start
            if elapsed >= timeout:
                holder = self._read_lock(lock_path)
                return LockResult(False, level="L2", key=key, waited_s=round(elapsed, 1),
                                  reason=f"timeout ({timeout}s), holder={holder}")

            if self._try_write_lock(lock_path, str(file_path), agent_id):
                return LockResult(True, level="L2", key=key, waited_s=round(elapsed, 1))

            holder = self._read_lock(lock_path)
            if holder and not _is_pid_alive(holder.get("pid", -1)):
                lock_path.unlink(missing_ok=True)
                continue

            time.sleep(self._POLL_INTERVAL_S)

    def release(self, file_path: str | Path) -> None:
        key = self._file_key(file_path)
        lock_path = self._lock_dir / f"file_{key}.lock"
        lock_path.unlink(missing_ok=True)

    def _try_write_lock(self, lock_path: Path, file_path: str, agent_id: str) -> bool:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            data = json.dumps({"pid": os.getpid(), "agent_id": agent_id, "file": file_path,
                               "acquired_at": datetime.now(UTC).isoformat()})
            os.write(fd, data.encode("utf-8"))
            os.close(fd)
            return True
        except (FileExistsError, OSError):
            return False

    def _read_lock(self, lock_path: Path) -> dict[str, Any] | None:
        if not lock_path.exists():
            return None
        try:
            return json.loads(lock_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None


class LockManager:
    """L0/L1/L2 三级锁统一管理器。

    使用：
        mgr = LockManager(agent_id="trae-01")
        if not mgr.acquire_L0():
            sys.exit(3)
        try:
            with mgr.dim_lock("D5"):
                with mgr.file_lock("src/foo.py"):
                    ...  # 安全执行
        finally:
            mgr.release_all()
    """

    def __init__(self, agent_id: str = "unknown", lock_dir: Path | None = None):
        self._agent_id = agent_id
        self._lock_dir = lock_dir or _DEFAULT_LOCK_DIR
        self._L0 = ProcessLock(self._lock_dir, agent_id)
        self._L1 = DimensionLock(self._lock_dir)
        self._L2 = FileLock(self._lock_dir)
        self._acquired: dict[str, str] = {}

    def acquire_L0(self, timeout_s: float = L0_LOCK_TIMEOUT_SECONDS) -> LockResult:
        result = self._L0.acquire(timeout_s)
        if result.acquired:
            self._acquired["L0"] = "global"
        return LockResult(result.acquired, level="L0", key="global",
                          waited_s=result.waited_s, reason=result.reason)

    def acquire_dim(self, dimension: str, timeout_s: float | None = None) -> LockResult:
        result = self._L1.acquire(dimension, self._agent_id, timeout_s)
        if result.acquired:
            self._acquired[f"L1_{dimension}"] = dimension
        return result

    def acquire_file(self, file_path: str | Path, timeout_s: float | None = None) -> LockResult:
        result = self._L2.acquire(file_path, self._agent_id, timeout_s)
        if result.acquired:
            self._acquired[f"L2_{str(file_path)}"] = str(file_path)
        return result

    def release_dim(self, dimension: str) -> None:
        self._L1.release(dimension)
        self._acquired.pop(f"L1_{dimension}", None)

    def release_file(self, file_path: str | Path) -> None:
        self._L2.release(file_path)
        self._acquired.pop(f"L2_{str(file_path)}", None)

    def release_all(self) -> None:
        self._L0.release()
        for key in list(self._acquired):
            if key.startswith("L1_"):
                self._L1.release(self._acquired[key])
            elif key.startswith("L2_"):
                self._L2.release(self._acquired[key])
        self._acquired.clear()

    def dim_lock(self, dimension: str, timeout_s: float | None = None):
        """上下文管理器：with mgr.dim_lock('D5'): ..."""
        return _LockContext(self, "dim", dimension, timeout_s)

    def file_lock(self, file_path: str | Path, timeout_s: float | None = None):
        """上下文管理器：with mgr.file_lock('src/foo.py'): ..."""
        return _LockContext(self, "file", file_path, timeout_s)


class _LockContext:
    def __init__(self, mgr: LockManager, mode: str, key: str | Path, timeout_s: float | None):
        self._mgr = mgr
        self._mode = mode
        self._key = key
        self._timeout = timeout_s

    def __enter__(self):
        if self._mode == "dim":
            self._mgr.acquire_dim(str(self._key), self._timeout)
        else:
            self._mgr.acquire_file(self._key, self._timeout)
        return self

    def __exit__(self, *args):
        if self._mode == "dim":
            self._mgr.release_dim(str(self._key))
        else:
            self._mgr.release_file(self._key)


# ===========================================================================
# Phase 3c: TokenBucket + AdmissionController + ShardRouter + CircuitBreaker
# ===========================================================================

class TokenBucket:
    """令牌桶限流器——对标 K8s APF + Google SRE client-side throttling。

    参数：refill_rate (tokens/s), burst_size (max tokens)
    使用：
        bucket = TokenBucket(refill_rate=10, burst_size=50)
        if bucket.consume():
            execute_script()
        else:
            reject_or_queue()
    """

    def __init__(self, refill_rate: float = 10.0, burst_size: int = 50):
        self._rate = refill_rate
        self._burst = burst_size
        self._tokens = float(burst_size)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(float(self._burst), self._tokens + elapsed * self._rate)
        self._last_refill = now

    @property
    def available(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens


class AdmissionController:
    """P0/P1/P2 三级优先级准入控制。

    使用：
        adm = AdmissionController(concurrency_limit=4)
        if adm.admit(Priority.P0): ...
        elif adm.admit(Priority.P1): ...
        else: queue_or_reject()
    """

    def __init__(self, concurrency_limit: int = 4, token_bucket: TokenBucket | None = None):
        self._concurrency_limit = concurrency_limit
        self._active: int = 0
        self._token_bucket = token_bucket or TokenBucket()
        self._lock = threading.Lock()
        self._queues: dict[str, list] = {"P0": [], "P1": [], "P2": []}
        self._total_admitted: int = 0
        self._total_rejected: int = 0

    def admit(self, priority: str) -> bool:
        with self._lock:
            if priority == "P0":
                self._active += 1
                self._total_admitted += 1
                return True
            if self._active >= self._concurrency_limit:
                self._queues.setdefault(priority, []).append(time.monotonic())
                self._total_rejected += 1
                return False
            if not self._token_bucket.consume():
                self._total_rejected += 1
                return False
            self._active += 1
            self._total_admitted += 1
            return True

    def release(self) -> None:
        with self._lock:
            if self._active > 0:
                self._active -= 1

    @property
    def stats(self) -> dict:
        with self._lock:
            return {"active": self._active, "admitted": self._total_admitted,
                    "rejected": self._total_rejected, "limit": self._concurrency_limit}


class ShardRouter:
    """模块级分片路由器——hash(module_id) % N → Shard DB。

    1500 模块按哈希均匀分到 4 个独立 SQLite，每片零锁竞争。
    对标 MongoDB Sharding + Vitess Keyspace。

    使用：
        router = ShardRouter(shard_count=4, db_dir=Path("data/shards"))
        db_path = router.route(module_id="MOD-RISK-012.k8s")
    """

    def __init__(self, shard_count: int = 4, db_dir: Path | None = None):
        self._shard_count = shard_count
        self._db_dir = db_dir or _DEFAULT_LOCK_DIR / "shards"
        self._db_dir.mkdir(parents=True, exist_ok=True)

    def route(self, module_id: str) -> Path:
        shard_idx = hash(module_id) % self._shard_count
        return self._db_dir / f"shard_{shard_idx}.db"

    def all_shards(self) -> list[Path]:
        return [self._db_dir / f"shard_{i}.db" for i in range(self._shard_count)]


class CircuitBreaker:
    """完整三级状态机：CLOSED → OPEN → HALF_OPEN。

    对标 Resilience4j CircuitBreaker。

    使用：
        cb = CircuitBreaker("quick_pool", failure_threshold=3, open_ttl_s=30, half_open_probe_count=2)
        if cb.allow_request():
            try:
                result = risky_call()
                cb.on_success()
            except Exception:
                cb.on_failure()
                raise
    """

    def __init__(self, name: str, failure_threshold: int = 3, open_ttl_s: float = 30, half_open_probe_count: int = 2):
        self.name = name
        self._failure_threshold = failure_threshold
        self._open_ttl_s = open_ttl_s
        self._half_open_probe_count = half_open_probe_count
        self._state: CircuitState = CircuitState.CLOSED
        self._failure_count: int = 0
        self._success_count: int = 0
        self._opened_at: float = 0.0
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            if self._state == CircuitState.OPEN:
                if time.monotonic() - self._opened_at >= self._open_ttl_s:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    return True
                return False
            if self._state == CircuitState.HALF_OPEN:
                return self._success_count < self._half_open_probe_count
            return False

    def on_success(self) -> None:
        with self._lock:
            if self._state == CircuitState.CLOSED:
                self._failure_count = 0
            elif self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._half_open_probe_count:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0

    def on_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            if self._state == CircuitState.CLOSED and self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()
            elif self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._state

    @property
    def stats(self) -> dict:
        with self._lock:
            return {"name": self.name, "state": self._state.value, "failures": self._failure_count,
                    "successes": self._success_count}


# ===========================================================================
# Phase 3b+3c: BulkheadExecutor 增强——集成 L1/L2 锁 + Circuit Breaker
# ===========================================================================

class BulkheadExecutorV2(BulkheadExecutor):
    """增强版 BulkheadExecutor——Phase 3b+3c 完整版。

    新增：
    - full L1 维度锁：同维度串行，不同维度并行
    - full L2 文件锁：同文件读写互斥
    - 完整 CircuitBreaker：每池独立三级状态机
    - 脚本级安全控制：维度锁 + 文件锁仅在 Disruptive/可写脚本时获取
    """

    def __init__(self, pool_override: dict[str, dict] | None = None, lock_dir: Path | None = None,
                 agent_id: str = "unknown"):
        super().__init__(pool_override)
        self._lock_mgr = LockManager(agent_id, lock_dir)
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        for pool_name, config in (pool_override or POOL_CONFIGS).items():
            self._circuit_breakers[pool_name] = CircuitBreaker(
                name=f"{pool_name}_pool",
                failure_threshold=config["circuit_breaker_threshold"],
                open_ttl_s=config["circuit_breaker_ttl_s"],
            )

    def _check_circuit(self, pool_name: str) -> bool:
        return self._circuit_breakers[pool_name].allow_request()

    def _record_result(self, pool_name: str, success: bool) -> None:
        cb = self._circuit_breakers[pool_name]
        if success:
            cb.on_success()
        else:
            cb.on_failure()

    def dispatch_with_locks(
        self,
        script_tasks: list[tuple[str, dict, Callable, set[str] | None]],
        on_complete: Callable | None = None,
    ) -> dict[str, Any]:
        """分发脚本并自动管理 L1 维度锁 + L2 文件锁。

        与 BulkheadExecutor.dispatch() 的区别：
        - 额外接收每个脚本的 affected_files: set[str]（被该脚本读写的文件列表）
        - Disruptive 脚本自动获取对应文件的 L2 锁
        - 写操作脚本获取 L1 维度锁（同维度串行）
        """
        results: list[dict] = []
        skipped: list[dict] = []
        futures: dict[Future, tuple[str, str]] = {}

        for script_name, meta, execute_fn, affected_files in script_tasks:
            dimensions = {d.value for d in meta.get("dimensions", [])}
            tags = frozenset(meta.get("tags", []))
            pool_name = self._route_to_pool(script_name, dimensions, tags)

            if not self._check_circuit(pool_name):
                skipped.append({"script_name": script_name, "pool": pool_name, "reason": "circuit_open"})
                continue

            sn_lower = script_name.lower()
            is_writable = any(sn_lower.startswith(p) or f"/{p}" in sn_lower
                              for p in ("fix_", "generate_", "register_"))

            def _wrapped_execute(sn: str, m: dict, writable: bool = is_writable,
                                 files: set[str] | None = affected_files) -> dict:
                acquired_dims: list[str] = []
                acquired_files: list[str] = []

                if writable:
                    for dim in {d.value for d in m.get("dimensions", [])}:
                        lock_res = self._lock_mgr.acquire_dim(dim)
                        if not lock_res:
                            return {"script_name": sn, "exit_code": 2, "findings": [], "is_failed": True,
                                    "error": f"L1 dimension lock failed: {dim}"}
                        acquired_dims.append(dim)

                if files:
                    for fp in files:
                        lock_res = self._lock_mgr.acquire_file(fp)
                        if not lock_res:
                            return {"script_name": sn, "exit_code": 2, "findings": [], "is_failed": True,
                                    "error": f"L2 file lock failed: {fp}"}
                        acquired_files.append(str(fp))

                try:
                    return execute_fn(sn, m)
                finally:
                    for dim in acquired_dims:
                        self._lock_mgr.release_dim(dim)
                    for fp in acquired_files:
                        self._lock_mgr.release_file(fp)

            pool = self._pools[pool_name]
            future = pool.executor.submit(_wrapped_execute, script_name, meta)
            futures[future] = (script_name, pool_name)
            pool.total_submitted += 1

        for future in as_completed(futures):
            script_name, pool_name = futures[future]
            try:
                result = future.result()
                success = not result.get("is_failed", False)
                self._record_result(pool_name, success)
                self._pools[pool_name].total_completed += 1
                results.append(result)
                if on_complete:
                    on_complete(result)
            except Exception:
                self._record_result(pool_name, False)
                self._pools[pool_name].total_failed += 1
                results.append({"script_name": script_name, "exit_code": 2, "findings": [], "is_failed": True})

        pool_stats = {}
        for pn, ps in self._pools.items():
            pool_stats[pn] = {"circuit_state": self._circuit_breakers[pn].state.value,
                              "submitted": ps.total_submitted - ps.total_completed - ps.total_failed + ps.total_completed + ps.total_failed,
                              "completed": ps.total_completed, "failed": ps.total_failed}

        return {"results": results, "pools": pool_stats, "skipped": skipped}

    @property
    def circuit_breaker_states(self) -> dict[str, dict]:
        return {name: cb.stats for name, cb in self._circuit_breakers.items()}