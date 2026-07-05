# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.lifecycle.daemon_registry
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-SHR_daemon_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
daemon_registry.py - unified daemon thread registry + resource guardian
=======================================================================

Implements a MAPE-K autonomic loop for desktop-grade AIOps:

  Monitor  -> snapshot CPU, memory, thread count, process count
  Analyze  -> compare against thresholds, detect pressure
  Plan     -> decide which daemons to stop/scale, what to recommend
  Execute  -> stop non-critical daemons, log warnings
  Knowledge -> accumulate pressure history for smarter decisions

Core problems solved:
  - Multiple sessions each start background threads, causing linear CPU stacking
  - No unified management for daemon threads, cannot query/stop/monitor
  - Same-type components instantiated repeatedly (e.g. multiple FLE-Schedulers)
  - No resource pressure detection -> system freezes before anyone notices

SSoT: MOD-INF-016 2.7 shared-lifecycle
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, unique
from typing import Any, ClassVar, Protocol, runtime_checkable

__all__ = [
    "DaemonEntry",
    "DaemonRegistry",
    "DaemonState",
    "PressureLevel",
    "ResourceSnapshot",
    "registry",
]

logger = logging.getLogger(__name__)


@unique
class DaemonState(StrEnum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    FAILED = "FAILED"


@unique
class PressureLevel(StrEnum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@runtime_checkable
class Stoppable(Protocol):
    def stop(self) -> None: ...


@dataclass
class DaemonEntry:
    name: str
    start_fn: Callable[[], None]
    stop_fn: Callable[[], None]
    priority: int = 0
    state: DaemonState = DaemonState.STOPPED
    started_at: float = 0.0
    error_count: int = 0
    last_error: str = ""


@dataclass
class ResourceSnapshot:
    timestamp: float = 0.0
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    process_count: int = 0
    thread_count: int = 0
    pressure: PressureLevel = PressureLevel.NORMAL

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "cpu_percent": round(self.cpu_percent, 1),
            "memory_percent": round(self.memory_percent, 1),
            "memory_used_gb": round(self.memory_used_gb, 2),
            "memory_total_gb": round(self.memory_total_gb, 2),
            "process_count": self.process_count,
            "thread_count": self.thread_count,
            "pressure": self.pressure.value,
        }


@dataclass
class _Thresholds:
    memory_warning_pct: float = 75.0
    memory_critical_pct: float = 85.0
    memory_emergency_pct: float = 95.0
    process_warning: int = 80
    process_critical: int = 150
    process_emergency: int = 250
    cpu_warning_pct: float = 80.0
    cpu_critical_pct: float = 95.0


class DaemonRegistry:
    _lock: ClassVar[threading.Lock] = threading.Lock()
    _entries: ClassVar[dict[str, DaemonEntry]] = {}
    _thresholds: ClassVar[_Thresholds] = _Thresholds()
    _pressure_history: ClassVar[list[ResourceSnapshot]] = []
    _max_history: ClassVar[int] = 60
    _monitor_thread: ClassVar[threading.Thread | None] = None
    _monitor_running: ClassVar[bool] = False
    _last_snapshot: ClassVar[ResourceSnapshot | None] = None
    _on_pressure_callbacks: ClassVar[list[Callable[[PressureLevel, ResourceSnapshot], None]]] = []

    @classmethod
    def register(
        cls,
        name: str,
        start_fn: Callable[[], None],
        stop_fn: Callable[[], None],
        priority: int = 0,
    ) -> None:
        with cls._lock:
            if name in cls._entries:
                logger.debug("DaemonRegistry: '%s' already registered, skipping", name)
                return
            cls._entries[name] = DaemonEntry(
                name=name,
                start_fn=start_fn,
                stop_fn=stop_fn,
                priority=priority,
            )
            logger.info("DaemonRegistry: registered '%s' (priority=%d)", name, priority)

    @classmethod
    def start(cls, name: str) -> bool:
        with cls._lock:
            entry = cls._entries.get(name)
            if entry is None:
                logger.warning("DaemonRegistry: '%s' not registered", name)
                return False
            if entry.state is DaemonState.RUNNING:
                logger.debug("DaemonRegistry: '%s' already running", name)
                return True
            entry.state = DaemonState.STARTING

        try:
            entry.start_fn()
            with cls._lock:
                entry.state = DaemonState.RUNNING
                entry.started_at = time.monotonic()
            logger.info("DaemonRegistry: started '%s'", name)
            return True
        except Exception as e:
            with cls._lock:
                entry.state = DaemonState.FAILED
                entry.error_count += 1
                entry.last_error = str(e)
            logger.exception("DaemonRegistry: failed to start '%s'", name)
            return False

    @classmethod
    def stop(cls, name: str) -> bool:
        with cls._lock:
            entry = cls._entries.get(name)
            if entry is None:
                return False
            if entry.state is not DaemonState.RUNNING:
                return True
            entry.state = DaemonState.STOPPING

        try:
            entry.stop_fn()
            with cls._lock:
                entry.state = DaemonState.STOPPED
            logger.info("DaemonRegistry: stopped '%s'", name)
            return True
        except Exception as e:
            with cls._lock:
                entry.state = DaemonState.FAILED
                entry.error_count += 1
                entry.last_error = str(e)
            logger.exception("DaemonRegistry: failed to stop '%s'", name)
            return False

    @classmethod
    def start_all(cls) -> dict[str, bool]:
        results: dict[str, bool] = {}
        with cls._lock:
            names = list(cls._entries.keys())
        for name in names:
            results[name] = cls.start(name)
        return results

    @classmethod
    def stop_all(cls) -> dict[str, bool]:
        results: dict[str, bool] = {}
        with cls._lock:
            names = list(cls._entries.keys())
        for name in reversed(names):
            results[name] = cls.stop(name)
        return results

    @classmethod
    def stop_low_priority(cls, min_priority: int = 0) -> list[str]:
        with cls._lock:
            candidates = [
                (name, entry)
                for name, entry in cls._entries.items()
                if entry.state is DaemonState.RUNNING and entry.priority <= min_priority
            ]
        candidates.sort(key=lambda x: x[1].priority)
        stopped: list[str] = []
        for name, _ in candidates:
            if cls.stop(name):
                stopped.append(name)
        if stopped:
            logger.warning("DaemonRegistry: stopped low-priority daemons: %s", stopped)
        return stopped

    @classmethod
    def status(cls) -> dict[str, dict[str, Any]]:
        with cls._lock:
            return {
                name: {
                    "state": entry.state.value,
                    "priority": entry.priority,
                    "started_at": entry.started_at,
                    "uptime_s": time.monotonic() - entry.started_at if entry.state is DaemonState.RUNNING else 0,
                    "error_count": entry.error_count,
                    "last_error": entry.last_error,
                }
                for name, entry in cls._entries.items()
            }

    @classmethod
    def is_running(cls, name: str) -> bool:
        with cls._lock:
            entry = cls._entries.get(name)
            return entry is not None and entry.state is DaemonState.RUNNING

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._entries.clear()

    @classmethod
    def on_pressure(cls, callback: Callable[[PressureLevel, ResourceSnapshot], None]) -> None:
        cls._on_pressure_callbacks.append(callback)

    @classmethod
    def snapshot_resources(cls) -> ResourceSnapshot:
        snap = ResourceSnapshot(timestamp=time.time())
        try:
            import psutil

            mem = psutil.virtual_memory()
            snap.memory_percent = mem.percent
            snap.memory_used_gb = mem.used / (1024**3)
            snap.memory_total_gb = mem.total / (1024**3)
            snap.cpu_percent = psutil.cpu_percent(interval=0)
            snap.process_count = len(psutil.pids())
        except ImportError:
            try:
                import os

                if os.name == "nt":
                    import ctypes

                    kernel32 = ctypes.windll.kernel32
                    MEMORYSTATUSEX = ctypes.c_ulonglong * 8
                    mem_status = MEMORYSTATUSEX()
                    kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))
                    snap.memory_total_gb = mem_status[0] / (1024**3)
                    snap.memory_used_gb = mem_status[2] / (1024**3)
                    snap.memory_percent = mem_status[4]
            except Exception as e:
                logger.warning("suppressed error in daemon_registry", exc_info=True)
        snap.pressure = cls._classify_pressure(snap)
        cls._last_snapshot = snap
        return snap

    @classmethod
    def _classify_pressure(cls, snap: ResourceSnapshot) -> PressureLevel:
        t = cls._thresholds
        if snap.memory_percent >= t.memory_emergency_pct:
            return PressureLevel.EMERGENCY
        if snap.process_count >= t.process_emergency:
            return PressureLevel.EMERGENCY
        if snap.memory_percent >= t.memory_critical_pct:
            return PressureLevel.CRITICAL
        if snap.process_count >= t.process_critical:
            return PressureLevel.CRITICAL
        if snap.cpu_percent >= t.cpu_critical_pct:
            return PressureLevel.CRITICAL
        if snap.memory_percent >= t.memory_warning_pct:
            return PressureLevel.WARNING
        if snap.process_count >= t.process_warning:
            return PressureLevel.WARNING
        if snap.cpu_percent >= t.cpu_warning_pct:
            return PressureLevel.WARNING
        return PressureLevel.NORMAL

    @classmethod
    def _monitor_loop(cls, interval: float = 30.0) -> None:
        while cls._monitor_running:
            try:
                snap = cls.snapshot_resources()
                cls._pressure_history.append(snap)
                if len(cls._pressure_history) > cls._max_history:
                    cls._pressure_history = cls._pressure_history[-cls._max_history :]

                if snap.pressure is not PressureLevel.NORMAL:
                    logger.warning(
                        "DaemonRegistry: resource pressure %s (mem=%.1f%%, procs=%d, cpu=%.1f%%)",
                        snap.pressure.value,
                        snap.memory_percent,
                        snap.process_count,
                        snap.cpu_percent,
                    )
                    for cb in cls._on_pressure_callbacks:
                        try:
                            cb(snap.pressure, snap)
                        except Exception as e:
                            logger.warning("suppressed error in daemon_registry", exc_info=True)

                if snap.pressure is PressureLevel.EMERGENCY:
                    cls.stop_low_priority(min_priority=5)
                elif snap.pressure is PressureLevel.CRITICAL:
                    cls.stop_low_priority(min_priority=2)

            except Exception:
                logger.exception("DaemonRegistry: monitor tick failed")
            time.sleep(interval)

    @classmethod
    def start_monitor(cls, interval: float = 30.0) -> None:
        if cls._monitor_running:
            return
        cls._monitor_running = True
        cls._monitor_thread = threading.Thread(
            target=cls._monitor_loop,
            args=(interval,),
            daemon=True,
            name="daemon-registry-monitor",
        )
        cls._monitor_thread.start()
        logger.info("DaemonRegistry: resource monitor started (interval=%.0fs)", interval)

    @classmethod
    def stop_monitor(cls) -> None:
        cls._monitor_running = False

    @classmethod
    def get_pressure_history(cls) -> list[dict[str, Any]]:
        return [s.to_dict() for s in cls._pressure_history]

    @classmethod
    def get_last_snapshot(cls) -> ResourceSnapshot | None:
        return cls._last_snapshot


registry = DaemonRegistry
