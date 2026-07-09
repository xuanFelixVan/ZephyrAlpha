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


class DaemonRegistry:
    _lock: ClassVar[threading.Lock] = threading.Lock()
    _entries: ClassVar[dict[str, DaemonEntry]] = {}

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
            logger.exception("DaemonRegistry: failed to start '%s'", name, exc_info=True)
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
            logger.exception("DaemonRegistry: failed to stop '%s'", name, exc_info=True)
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


registry = DaemonRegistry