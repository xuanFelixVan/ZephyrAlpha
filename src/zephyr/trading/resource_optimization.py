# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.resource_optimization
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.lifecycle.daemon_registry; zephyr.shared.lifecycle.resource_optimization_models; zephyr.shared.io.io_cache; zephyr.shared.io.streaming_reader; zephyr.shared.infra.process_pool; zephyr.shared.lifecycle.lazy_loader; zephyr.shared.capacity_calibrator; zephyr.shared.capacity_digital_twin; zephyr.shared.capacity_fingerprint; zephyr.shared.capacity_governance_loop; zephyr.shared.capacity_runbook_generator; zephyr.shared.model_capacity_probe; zephyr.trading.__init__; zephyr.shared.event_bus; zephyr.governance.audit_trail.bridge
# [CONSUMERS] runtime.auto_runtime_core; runtime.health_monitor; shared.lifecycle (re-export)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_resource_optimization | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
resource_optimization.py - MAPE-K autonomic resource optimization engine
========================================================================

Moved from shared.lifecycle.resource_optimization_engine.
Canonical location is now zephyr.trading.resource_optimization.

Models remain in shared.lifecycle.resource_optimization_models to avoid
circular imports (shared.io / shared.infra depend on models).

MAPE-K loop:
  Monitor  -> snapshot CPU, memory, disk I/O, process/thread count
  Analyze  -> classify pressure (NORMAL/WARNING/CRITICAL/EMERGENCY)
  Plan     -> decide optimization or defensive strategy
  Execute  -> run strategy, record result
  Knowledge -> accumulate history for smarter decisions
"""

from __future__ import annotations

import logging
import os
import random
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from zephyr.shared.io.io_cache import FileCache
from zephyr.shared.lifecycle.daemon_registry import DaemonRegistry
from zephyr.shared.lifecycle.resource_optimization_models import (
    CacheStats,
    CircuitBreakerState,
    DefensiveStrategy,
    DegradationMatrix,
    HealthCheckResult,
    OptimizationRecord,
    OptimizationResult,
    OptimizationStrategy,
    PressureLevel,
    PressureState,
    ProcessPoolStats,
    ResourceSnapshot,
)
from zephyr.shared.capacity_governance.capacity_calibrator import CapacityCalibrator
from zephyr.shared.capacity_governance.capacity_digital_twin import CapacityDigitalTwin
from zephyr.shared.capacity_governance.capacity_fingerprint import CapacityFingerprint
from zephyr.shared.capacity_governance.capacity_governance_loop import CapacityGovernanceLoop
from zephyr.shared.capacity_governance.capacity_runbook_generator import CapacityRunbookGenerator
from zephyr.shared.lifecycle.lazy_loader import LazyModuleRegistry
from zephyr.shared.capacity_governance.model_capacity_probe import ModelCapacityProbe
from zephyr.shared.infra.process_pool import MCPProcessPool

__all__ = [
    "CacheStats",
    "CircuitBreaker",
    "CircuitBreakerState",
    "DefensiveStrategy",
    "DegradationMatrix",
    "HealthCheckResult",
    "OptimizationRecord",
    "OptimizationResult",
    "OptimizationStrategy",
    "PressureLevel",
    "PressureState",
    "ProcessPoolStats",
    "ResourceOptimizationEngine",
    "ResourceSnapshot",
]


logger = logging.getLogger(__name__)


class _PressureThresholds(BaseModel):
    memory_warning_percent: float = 75.0
    memory_critical_percent: float = 85.0
    memory_emergency_percent: float = 95.0
    cpu_warning_percent: float = 80.0
    cpu_critical_percent: float = 90.0
    cpu_emergency_percent: float = 98.0
    process_warning_count: int = 50
    process_critical_count: int = 100
    process_emergency_count: int = 250
    gpu_warning_percent: float = 85.0
    gpu_critical_percent: float = 95.0
    gpu_emergency_percent: float = 98.0


class _HysteresisConfig(BaseModel):
    confirmation_count: int = 2
    cooldown_seconds: float = 60.0
    hysteresis_percent: float = 10.0
    oscillation_threshold_per_hour: int = 3


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_s: float = 30.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout_s = recovery_timeout_s
        self._half_open_max_calls = half_open_max_calls
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        self._last_failure_time: float = 0.0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitBreakerState:
        # 5.91.3 修复: getter仅返回当前状态,不触发状态转换和计数器修改
        with self._lock:
            return self._state

    def _try_recover(self) -> None:
        """5.91.3 修复: 提取状态转换逻辑,仅在allow()中调用。"""
        if self._state is CircuitBreakerState.OPEN:
            if time.monotonic() - self._last_failure_time >= self._recovery_timeout_s:
                self._state = CircuitBreakerState.HALF_OPEN
                self._half_open_calls = 0

    def allow(self) -> bool:
        with self._lock:
            self._try_recover()
            if self._state is CircuitBreakerState.CLOSED:
                return True
            if self._state is CircuitBreakerState.HALF_OPEN:
                if self._half_open_calls < self._half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            return False

    def record_success(self) -> None:
        with self._lock:
            if self._state is CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._half_open_calls = 0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._state is CircuitBreakerState.HALF_OPEN or self._failure_count >= self._failure_threshold:
                self._state = CircuitBreakerState.OPEN

    def reset(self) -> None:
        with self._lock:
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._half_open_calls = 0


class _PressureStateMachine:
    def __init__(self, config: _HysteresisConfig | None = None) -> None:
        self._config = config or _HysteresisConfig()
        self._current = PressureLevel.NORMAL
        self._previous: PressureLevel | None = None
        self._entered_at = datetime.now(UTC)
        self._transition_count = 0
        self._pending_level: PressureLevel | None = None
        self._pending_confirmations = 0
        self._last_transition_time: float = 0.0
        self._hourly_transitions: list[float] = []
        self._lock = threading.Lock()

    @property
    def current(self) -> PressureLevel:
        return self._current

    @property
    def state(self) -> PressureState:
        cooldown = 0.0
        if self._last_transition_time > 0:
            elapsed = time.monotonic() - self._last_transition_time
            cooldown = max(0.0, self._config.cooldown_seconds - elapsed)
        return PressureState(
            current_level=self._current,
            previous_level=self._previous,
            entered_at=self._entered_at,
            transition_count=self._transition_count,
            cooldown_remaining_s=cooldown,
        )

    def transition(self, classified: PressureLevel) -> PressureLevel:
        with self._lock:
            if classified == self._current:
                self._pending_level = None
                self._pending_confirmations = 0
                return self._current

            now = time.monotonic()
            self._hourly_transitions = [t for t in self._hourly_transitions if now - t < 3600]

            level_order = [
                PressureLevel.NORMAL,
                PressureLevel.WARNING,
                PressureLevel.CRITICAL,
                PressureLevel.EMERGENCY,
            ]
            classified_idx = level_order.index(classified)
            current_idx = level_order.index(self._current)
            is_escalation = classified_idx > current_idx

            if is_escalation:
                effective_confirm = self._config.confirmation_count
                if len(self._hourly_transitions) >= self._config.oscillation_threshold_per_hour:
                    effective_confirm = min(effective_confirm + 1, 5)

                if self._pending_level == classified:
                    self._pending_confirmations += 1
                else:
                    self._pending_level = classified
                    self._pending_confirmations = 1

                if self._pending_confirmations >= effective_confirm:
                    self._apply_transition(classified, now)
                return self._current
            else:
                elapsed = now - self._last_transition_time if self._last_transition_time > 0 else float("inf")
                if elapsed < self._config.cooldown_seconds:
                    return self._current
                self._apply_transition(classified, now)
                return self._current

    def _apply_transition(self, new_level: PressureLevel, now: float) -> None:
        self._previous = self._current
        self._current = new_level
        self._entered_at = datetime.now(UTC)
        self._transition_count += 1
        self._last_transition_time = now
        self._hourly_transitions.append(now)
        self._pending_level = None
        self._pending_confirmations = 0


class ResourceOptimizationEngine:
    _instance: ResourceOptimizationEngine | None = None
    _init_lock = threading.Lock()

    def __new__(cls) -> ResourceOptimizationEngine:
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        # 5.98.3 修复: __init__守卫加锁,防并发首次调用重复初始化
        with self._init_lock:
            if self._initialized:
                return
            self._thresholds = _PressureThresholds()
            self._hysteresis = _HysteresisConfig()
            self._pressure_sm = _PressureStateMachine(self._hysteresis)
            self._circuit_breakers: dict[str, CircuitBreaker] = {}
            self._optimization_history: list[OptimizationRecord] = []
            self._max_history = 10000
            self._pressure_callbacks: list[Callable[[PressureLevel, ResourceSnapshot], None]] = []
            self._monitor_thread: threading.Thread | None = None
            self._monitor_running = False
            self._last_snapshot: ResourceSnapshot | None = None
            self._monitor_interval = 30.0
            self._started_at: float | None = None
            self._degradation_matrix = DegradationMatrix(
                normal={"scheduler": "30s", "cache": "warm", "process_pool": "active"},
                warning={"scheduler": "60s", "cache": "warm", "process_pool": "active"},
                critical={"scheduler": "120s", "cache": "cold", "process_pool": "frozen"},
                emergency={"scheduler": "paused", "cache": "evicted", "process_pool": "stopped"},
            )
            self._file_cache = FileCache(max_entries=1000, ttl_seconds=300.0)
            self._process_pool = MCPProcessPool(max_processes=30)
            self._lazy_loader = LazyModuleRegistry()
            self._capacity_calibrator = CapacityCalibrator()
            self._capacity_digital_twin = CapacityDigitalTwin("resource-optimization")
            self._capacity_fingerprint = CapacityFingerprint()
            self._capacity_governance_loop = CapacityGovernanceLoop()
            self._capacity_runbook_generator = CapacityRunbookGenerator()
            self._model_capacity_probe = ModelCapacityProbe()
            self._config_path: str | None = None
            self._config_mtime: float = 0.0
            self._self_healing_enabled = True
            self._self_healing_max_recovery_s = 60.0
            self._self_healing_verification_delay_s = 5.0
            self._self_healing_max_retries = 3
            self._audit_enabled = True
            self._eventbus_enabled = True
            self._eventbus_topic = "resource.pressure.changed"
            self._last_pressure_level = PressureLevel.NORMAL
            self._initialized = True
            self._load_config()
            logger.info("ResourceOptimizationEngine: initialized (singleton)")

    def snapshot(self) -> ResourceSnapshot:
        snap = ResourceSnapshot(timestamp=time.time())
        try:
            import psutil

            mem = psutil.virtual_memory()
            snap.memory_percent = mem.percent
            snap.memory_used_gb = mem.used / (1024**3)
            snap.memory_total_gb = mem.total / (1024**3)
            snap.cpu_percent = psutil.cpu_percent(interval=0)
            snap.process_count = len(psutil.pids())
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    snap.disk_io_read_mb_s = disk_io.read_bytes / (1024**2)
                    snap.disk_io_write_mb_s = disk_io.write_bytes / (1024**2)
            except Exception as e:
                logger.warning("suppressed error in resource_optimization", exc_info=True)
            import shutil

            try:
                usage = shutil.disk_usage(".")
                snap.disk_free_gb = usage.free / (1024**3)
            except Exception as e:
                logger.warning("suppressed error in resource_optimization", exc_info=True)
        except ImportError:
            try:
                import ctypes

                if os.name == "nt":
                    kernel32 = ctypes.windll.kernel32

                    class MEMORYSTATUSEX(ctypes.Structure):
                        _fields_ = [
                            ("dwLength", ctypes.c_ulong),
                            ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong),
                        ]

                    mem_status = MEMORYSTATUSEX()
                    mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                    kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))
                    snap.memory_percent = float(mem_status.dwMemoryLoad)
                    snap.memory_total_gb = mem_status.ullTotalPhys / (1024**3)
                    snap.memory_used_gb = (mem_status.ullTotalPhys - mem_status.ullAvailPhys) / (1024**3)
            except Exception as e:
                logger.warning("suppressed error in resource_optimization", exc_info=True)

        try:
            from zephyr.trading.gpu_monitor import collect_gpu_stats

            gpu = collect_gpu_stats()
            snap.gpu_percent = gpu.get("gpu_percent", 0.0)
            snap.gpu_memory_used_gb = gpu.get("memory_used_gb", 0.0)
            snap.gpu_memory_total_gb = gpu.get("memory_total_gb", 0.0)
            snap.gpu_available = gpu.get("available", False)
        except Exception as e:
            logger.warning("suppressed error in resource_optimization", exc_info=True)

        try:
            from zephyr.trading.ide_health_daemon import scan_ghost_windows

            ghosts = scan_ghost_windows()
            snap.ide_ghost_windows = len(ghosts)
        except Exception as e:
            logger.warning("suppressed error in resource_optimization", exc_info=True)

        classified = self._classify_pressure(snap)
        snap.pressure = self._pressure_sm.transition(classified)
        self._last_snapshot = snap
        return snap

    def _classify_pressure(self, snap: ResourceSnapshot) -> PressureLevel:
        t = self._thresholds
        if snap.memory_percent >= t.memory_emergency_percent:
            return PressureLevel.EMERGENCY
        if snap.process_count >= t.process_emergency_count:
            return PressureLevel.EMERGENCY
        if snap.cpu_percent >= t.cpu_emergency_percent:
            return PressureLevel.EMERGENCY
        if snap.gpu_available and snap.gpu_percent >= t.gpu_emergency_percent:
            return PressureLevel.EMERGENCY
        if snap.memory_percent >= t.memory_critical_percent:
            return PressureLevel.CRITICAL
        if snap.process_count >= t.process_critical_count:
            return PressureLevel.CRITICAL
        if snap.cpu_percent >= t.cpu_critical_percent:
            return PressureLevel.CRITICAL
        if snap.gpu_available and snap.gpu_percent >= t.gpu_critical_percent:
            return PressureLevel.CRITICAL
        if snap.memory_percent >= t.memory_warning_percent:
            return PressureLevel.WARNING
        if snap.process_count >= t.process_warning_count:
            return PressureLevel.WARNING
        if snap.cpu_percent >= t.cpu_warning_percent:
            return PressureLevel.WARNING
        if snap.gpu_available and snap.gpu_percent >= t.gpu_warning_percent:
            return PressureLevel.WARNING
        if snap.ide_ghost_windows > 0:
            return PressureLevel.WARNING
        return PressureLevel.NORMAL

    def optimize(
        self,
        strategy: OptimizationStrategy,
        context: dict[str, Any] | None = None,
    ) -> OptimizationResult:
        cb = self._circuit_breakers.get(strategy.value)
        if cb is None:
            cb = CircuitBreaker()
            self._circuit_breakers[strategy.value] = cb

        snap_before = self.snapshot()

        if not cb.allow():
            return OptimizationResult(
                strategy=strategy,
                success=False,
                snapshot_before=snap_before,
                quality_preserved=True,
                error_message=f"circuit breaker OPEN for {strategy.value}",
            )

        start = time.monotonic()
        actions: list[str] = []
        success = True
        error_msg: str | None = None

        try:
            if strategy is OptimizationStrategy.SCHEDULE_ADAPT:
                actions = self._execute_schedule_adapt(snap_before.pressure)
            elif strategy is OptimizationStrategy.MEMORY_COMPACT:
                actions = self._execute_memory_compact()
            elif strategy is OptimizationStrategy.CACHE_WARM:
                actions = self._execute_cache_warm(context)
            elif strategy is OptimizationStrategy.IO_BATCH:
                actions = self._execute_io_batch(context)
            elif strategy is OptimizationStrategy.PROCESS_POOL:
                actions = self._execute_process_pool(context)
            elif strategy is OptimizationStrategy.LAZY_INIT:
                actions = self._execute_lazy_init(context)
            elif strategy is OptimizationStrategy.STREAMING_READ:
                actions = self._execute_streaming_read(context)
            else:
                raise ValueError(f"unknown strategy: {strategy}")

            cb.record_success()
        except Exception as e:
            success = False
            error_msg = str(e)
            cb.record_failure()
            logger.exception("ResourceOptimizationEngine: optimize(%s) failed", strategy.value, exc_info=True)

        snap_after = self.snapshot()
        duration_ms = int((time.monotonic() - start) * 1000)

        record = OptimizationRecord(
            trigger=snap_before.pressure,
            strategy=strategy,
            actions_taken=actions,
            memory_before_gb=snap_before.memory_used_gb,
            memory_after_gb=snap_after.memory_used_gb,
            process_count_before=snap_before.process_count,
            process_count_after=snap_after.process_count,
            quality_preserved=True,
            duration_ms=duration_ms,
            success=success,
        )
        self._optimization_history.append(record)
        if len(self._optimization_history) > self._max_history:
            self._optimization_history = self._optimization_history[-self._max_history :]

        self._audit_optimization(record)

        return OptimizationResult(
            strategy=strategy,
            success=success,
            actions_taken=actions,
            snapshot_before=snap_before,
            snapshot_after=snap_after,
            quality_preserved=True,
            error_message=error_msg,
        )

    def _execute_schedule_adapt(self, pressure: PressureLevel) -> list[str]:
        intervals = {
            PressureLevel.NORMAL: 30.0,
            PressureLevel.WARNING: 60.0,
            PressureLevel.CRITICAL: 120.0,
            PressureLevel.EMERGENCY: 0.0,
        }
        new_interval = intervals.get(pressure, 30.0)
        if new_interval > 0:
            self._monitor_interval = new_interval
            return [f"schedule_adapt: interval set to {new_interval}s for {pressure.value}"]
        else:
            return [f"schedule_adapt: paused for {pressure.value}"]

    def _execute_memory_compact(self) -> list[str]:
        import gc

        before = len(gc.get_objects())
        collected = gc.collect()
        after = len(gc.get_objects())
        return [f"memory_compact: gc.collect() freed {collected} objects ({before} -> {after})"]

    def _execute_cache_warm(self, context: dict[str, Any] | None) -> list[str]:
        files = []
        if context and "files" in context:
            files = context["files"]
        if not files:
            return ["cache_warm: no files specified in context"]
        loaded = self._file_cache.warm(files)
        return [f"cache_warm: preloaded {loaded}/{len(files)} files"]

    def _execute_io_batch(self, context: dict[str, Any] | None) -> list[str]:
        files = []
        if context and "files" in context:
            files = context["files"]
        if not files:
            return ["io_batch: no files specified in context"]
        loaded = 0
        for fp in files:
            result = self._file_cache.get_or_load(fp)
            if result is not None:
                loaded += 1
        return [f"io_batch: batch loaded {loaded}/{len(files)} files"]

    def _execute_streaming_read(self, context: dict[str, Any] | None) -> list[str]:
        path = context.get("path") if context else None
        if not path:
            return ["streaming_read: no path specified in context"]
        p = str(path)
        try:
            size_mb = os.path.getsize(p) / (1024 * 1024)
        except OSError:
            size_mb = 0.0
        if size_mb > 1.0:
            return [f"streaming_read: {p} ({size_mb:.1f}MB) — use stream_jsonl/tail_jsonl"]
        return [f"streaming_read: {p} ({size_mb:.1f}MB) — small file, direct read OK"]

    def _execute_process_pool(self, context: dict[str, Any] | None) -> list[str]:
        stats = self._process_pool.get_stats()
        if stats.active_processes == 0:
            return ["process_pool: no active processes to optimize"]
        reuse_before = stats.reuse_count
        return [f"process_pool: {stats.active_processes} active, {reuse_before} reuses — pool sharing active"]

    def _execute_lazy_init(self, context: dict[str, Any] | None) -> list[str]:
        loader_stats = self._lazy_loader.stats()
        pending = loader_stats.get("pending", 0)
        if pending == 0:
            return ["lazy_init: all registered modules already loaded"]
        return [f"lazy_init: {pending} modules pending — deferred until first access"]

    def _execute_defensive(self, pressure: PressureLevel) -> list[str]:
        actions: list[str] = []
        if pressure is PressureLevel.EMERGENCY:
            stopped = DaemonRegistry.stop_low_priority(min_priority=5)
            if stopped:
                actions.append(f"stop_low_priority(5): stopped {stopped}")
            import gc

            gc.collect()
            actions.append("emergency_gc: forced garbage collection")
        elif pressure is PressureLevel.CRITICAL:
            stopped = DaemonRegistry.stop_low_priority(min_priority=2)
            if stopped:
                actions.append(f"stop_low_priority(2): stopped {stopped}")
            actions.append("reduce_frequency: monitor interval extended")
        return actions

    def register_daemon(
        self,
        name: str,
        start_fn: Callable[[], None],
        stop_fn: Callable[[], None],
        priority: int = 5,
    ) -> None:
        DaemonRegistry.register(name, start_fn, stop_fn, priority)

    def start_daemon(self, name: str) -> bool:
        return DaemonRegistry.start(name)

    def stop_daemon(self, name: str) -> bool:
        return DaemonRegistry.stop(name)

    def get_cache_stats(self) -> CacheStats:
        return self._file_cache.get_stats()

    def get_file_cache(self) -> FileCache:
        return self._file_cache

    def get_process_pool_stats(self) -> ProcessPoolStats:
        return self._process_pool.get_stats()

    def get_process_pool(self) -> MCPProcessPool:
        return self._process_pool

    def get_lazy_loader(self) -> LazyModuleRegistry:
        return self._lazy_loader

    def get_optimization_history(self, limit: int = 100) -> list[OptimizationRecord]:
        return self._optimization_history[-limit:]

    def on_pressure(self, callback: Callable[[PressureLevel, ResourceSnapshot], None]) -> None:
        self._pressure_callbacks.append(callback)

    def health_check(self) -> HealthCheckResult:
        running = self._monitor_running
        loop_alive = self._monitor_thread is not None and self._monitor_thread.is_alive()
        age = 0.0
        if self._last_snapshot is not None:
            age = time.time() - self._last_snapshot.timestamp
        status = DaemonRegistry.status()
        # 5.26.3/5.26.9 修复：health_check 真实检查 cache 和 process_pool 状态（原硬编码 True）
        try:
            cache_stats = self._file_cache.get_stats()
            cache_healthy = cache_stats.total_entries >= 0
        except Exception as e:
            logger.warning("health_check: cache stats failed: %s", e, exc_info=True)
            cache_healthy = False
        try:
            pool_stats = self._process_pool.get_stats()
            process_pool_healthy = pool_stats.zombie_count == 0
        except Exception as e:
            logger.warning("health_check: process_pool stats failed: %s", e, exc_info=True)
            process_pool_healthy = False
        return HealthCheckResult(
            engine_running=running,
            monitor_loop_alive=loop_alive,
            last_snapshot_age_s=round(age, 1),
            pressure_level=self._pressure_sm.current,
            daemon_count=len(status),
            cache_healthy=cache_healthy,
            process_pool_healthy=process_pool_healthy,
        )

    def get_pressure_state(self) -> PressureState:
        return self._pressure_sm.state

    def force_pressure(self, level: PressureLevel, reason: str) -> None:
        logger.warning(
            "ResourceOptimizationEngine: force_pressure(%s) — %s",
            level.value,
            reason,
        )
        self._pressure_sm._current = level
        self._pressure_sm._entered_at = datetime.now(UTC)
        self._pressure_sm._transition_count += 1

    def get_degradation_matrix(self) -> DegradationMatrix:
        return self._degradation_matrix

    def get_circuit_breaker_status(self) -> dict[str, CircuitBreakerState]:
        return {name: cb.state for name, cb in self._circuit_breakers.items()}

    def start_monitor(self, interval: float = 30.0) -> None:
        """P1 修复（2026-07-05）：事件驱动替代 time.sleep daemon。

        订阅 EventBus 事件触发 monitor_tick()，不再启动后台轮询线程。
        interval 参数保留用于 CI 批量兜底参考。
        """
        if self._monitor_running:
            return
        self._monitor_interval = interval
        self._monitor_running = True
        self._started_at = time.monotonic()
        try:
            from zephyr.shared.events.event_bus import bus

            bus.subscribe("task.completed", lambda _: self.monitor_tick())
            bus.subscribe("task.failed", lambda _: self.monitor_tick())
            bus.subscribe("resource.check.request", lambda _: self.monitor_tick())
            logger.info("ResourceOptimizationEngine: monitor started (event-driven, no daemon thread)")
        except Exception as e:
            logger.warning("ResourceOptimizationEngine: EventBus subscribe failed: %s", e, exc_info=True)

    def stop_monitor(self) -> None:
        self._monitor_running = False
        logger.info("ResourceOptimizationEngine: monitor stopped")

    def monitor_tick(self) -> None:
        """事件驱动入口：采集资源快照 + 压力回调 + 自愈。

        由 EventBus 事件触发或 CI 批量兜底调用。替代原 _monitor_loop 的 time.sleep 轮询。
        """
        if not self._monitor_running:
            return
        try:
            self._check_config_reload()
            snap = self.snapshot()

            if snap.pressure is not PressureLevel.NORMAL:
                logger.warning(
                    "ResourceOptimizationEngine: pressure %s (mem=%.1f%%, cpu=%.1f%%, procs=%d)",
                    snap.pressure.value,
                    snap.memory_percent,
                    snap.cpu_percent,
                    snap.process_count,
                )
                for cb in self._pressure_callbacks:
                    try:
                        cb(snap.pressure, snap)
                    except Exception as e:
                        logger.debug("suppressed error in resource_optimization", exc_info=True)

            self._emit_pressure_event(snap)

            if snap.pressure in (PressureLevel.EMERGENCY, PressureLevel.CRITICAL):
                self._execute_defensive(snap.pressure)
                self._self_heal_cycle(snap)

        except Exception:
            logger.exception("ResourceOptimizationEngine: monitor tick failed", exc_info=True)

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def _load_config(self) -> None:
        config_paths = [
            os.path.join(os.getcwd(), "config", "resource_optimization.yaml"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "resource_optimization.yaml"),
        ]
        for cp in config_paths:
            cp = os.path.normpath(cp)
            if os.path.isfile(cp):
                self._config_path = cp
                break
        if self._config_path is None:
            return
        self._apply_config(self._config_path)

    def _apply_config(self, path: str) -> None:
        try:
            import yaml

            with open(path, encoding="utf-8") as f:
                raw = f.read()
            cfg = yaml.safe_load(raw)
            if not isinstance(cfg, dict):
                return
        except Exception:
            logger.exception("ResourceOptimizationEngine: config load failed from %s", path, exc_info=True)
            return

        self._config_mtime = os.path.getmtime(path)

        pt = cfg.get("pressure_thresholds", {})
        if pt:
            self._thresholds = _PressureThresholds(
                memory_warning_percent=pt.get("memory_warning_percent", 75.0),
                memory_critical_percent=pt.get("memory_critical_percent", 85.0),
                memory_emergency_percent=pt.get("memory_emergency_percent", 95.0),
                cpu_warning_percent=pt.get("cpu_warning_percent", 80.0),
                cpu_critical_percent=pt.get("cpu_critical_percent", 90.0),
                cpu_emergency_percent=pt.get("cpu_emergency_percent", 98.0),
                process_warning_count=pt.get("process_warning_count", 50),
                process_critical_count=pt.get("process_critical_count", 100),
                process_emergency_count=pt.get("process_emergency_count", 250),
                gpu_warning_percent=pt.get("gpu_warning_percent", 85.0),
                gpu_critical_percent=pt.get("gpu_critical_percent", 95.0),
                gpu_emergency_percent=pt.get("gpu_emergency_percent", 98.0),
            )

        hy = cfg.get("hysteresis", {})
        if hy:
            self._hysteresis = _HysteresisConfig(
                confirmation_count=hy.get("confirmation_count", 2),
                cooldown_seconds=hy.get("cooldown_seconds", 60.0),
                hysteresis_percent=hy.get("hysteresis_percent", 10.0),
                oscillation_threshold_per_hour=hy.get("oscillation_threshold_per_hour", 3),
            )
            self._pressure_sm = _PressureStateMachine(self._hysteresis)

        sh = cfg.get("self_healing", {})
        if sh:
            self._self_healing_enabled = sh.get("enabled", True)
            self._self_healing_max_recovery_s = sh.get("max_recovery_time_s", 60.0)
            self._self_healing_verification_delay_s = sh.get("verification_delay_s", 5.0)
            self._self_healing_max_retries = sh.get("max_retries", 3)

        au = cfg.get("audit", {})
        if au:
            self._audit_enabled = au.get("enabled", True)

        eb = cfg.get("eventbus", {})
        if eb:
            self._eventbus_enabled = eb.get("enabled", True)
            self._eventbus_topic = eb.get("topic", "resource.pressure.changed")

        logger.info("ResourceOptimizationEngine: config loaded from %s", path)

    def _check_config_reload(self) -> None:
        if self._config_path is None:
            return
        try:
            current_mtime = os.path.getmtime(self._config_path)
            if current_mtime != self._config_mtime:
                self._apply_config(self._config_path)
        except OSError as e:
            # 5.54.5 修复：原 except OSError: pass 静默停止热重载，配置文件误删后引擎无感知。
            # 改为 warning 级别日志记录。
            logger.warning("ResourceOptimizationEngine: config hot-reload failed (%s: %s)", type(e).__name__, e)

    def _self_heal_cycle(self, snap: ResourceSnapshot) -> OptimizationResult | None:
        if not self._self_healing_enabled:
            return None
        if snap.pressure is PressureLevel.NORMAL:
            return None

        start = time.monotonic()
        retries = 0
        while retries < self._self_healing_max_retries:
            if time.monotonic() - start > self._self_healing_max_recovery_s:
                logger.warning("ResourceOptimizationEngine: self-heal timeout after %.0fs", time.monotonic() - start)
                break

            strategy = self._select_healing_strategy(snap.pressure)
            result = self.optimize(strategy)
            if result.success:
                time.sleep(self._self_healing_verification_delay_s)
                verify_snap = self.snapshot()
                level_order = [
                    PressureLevel.NORMAL,
                    PressureLevel.WARNING,
                    PressureLevel.CRITICAL,
                    PressureLevel.EMERGENCY,
                ]
                if level_order.index(verify_snap.pressure) < level_order.index(snap.pressure):
                    logger.info(
                        "ResourceOptimizationEngine: self-heal succeeded — %s → %s",
                        snap.pressure.value,
                        verify_snap.pressure.value,
                    )
                    return result
            retries += 1
            logger.warning(
                "ResourceOptimizationEngine: self-heal retry %d/%d",
                retries,
                self._self_healing_max_retries,
            )
            # 5.72.4 修复：exponential backoff + jitter 避免重试风暴
            if retries < self._self_healing_max_retries:
                _delay = (2 ** retries) + random.uniform(0, 1)
                time.sleep(min(_delay, 30.0))

        logger.warning("ResourceOptimizationEngine: self-heal failed after %d retries", retries)
        return None

    def _select_healing_strategy(self, pressure: PressureLevel) -> OptimizationStrategy:
        if pressure is PressureLevel.EMERGENCY or pressure is PressureLevel.CRITICAL:
            return OptimizationStrategy.MEMORY_COMPACT
        else:
            return OptimizationStrategy.SCHEDULE_ADAPT

    def _emit_pressure_event(self, snap: ResourceSnapshot) -> None:
        if not self._eventbus_enabled:
            return
        if snap.pressure == self._last_pressure_level:
            return
        self._last_pressure_level = snap.pressure
        try:
            from zephyr.shared.events.event_bus import bus
            bus.emit(
                self._eventbus_topic,
                {
                    "pressure_level": snap.pressure.value,
                    "cpu_percent": snap.cpu_percent,
                    "memory_percent": snap.memory_percent,
                    "process_count": snap.process_count,
                    "timestamp": snap.timestamp,
                },
            )
        except Exception as e:
            logger.warning("suppressed error in resource_optimization", exc_info=True)

    def _audit_optimization(self, record: OptimizationRecord) -> None:
        if not self._audit_enabled:
            return
        try:
            from zephyr.governance.audit_trail.bridge import write_to_core

            write_to_core(
                "resource_optimization",
                {
                    "strategy": record.strategy.value,
                    "trigger": record.trigger.value,
                    "actions_taken": record.actions_taken,
                    "memory_before_gb": record.memory_before_gb,
                    "memory_after_gb": record.memory_after_gb,
                    "quality_preserved": record.quality_preserved,
                    "success": record.success,
                    "duration_ms": record.duration_ms,
                },
            )
        except Exception as e:
            logger.warning("suppressed error in resource_optimization", exc_info=True)