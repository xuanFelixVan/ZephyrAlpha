# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.process_pool
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.shared.lifecycle.resource_optimization_models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_process_pool | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
process_pool.py - Shared process pool for MCP servers and subprocess tasks
=============================================================================

SSoT: MOD-INF-032 resource-optimization-engine/blueprint.md §7.2

Design:
  - Max process limit (default 30) to prevent resource exhaustion
  - Process reuse: same MCP server shares one subprocess across conversations
  - Zombie detection: periodic scan for dead processes
  - Graceful shutdown: terminate all pooled processes on engine stop
"""

from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field

from zephyr.shared.lifecycle.resource_optimization_models import ProcessPoolStats

__all__ = ["MCPProcessPool", "PooledProcess"]

logger = logging.getLogger(__name__)


@dataclass
class PooledProcess:
    name: str
    process: subprocess.Popen
    created_at: float = field(default_factory=time.monotonic)
    reuse_count: int = 0
    last_used_at: float = field(default_factory=time.monotonic)

    @property
    def is_alive(self) -> bool:
        return self.process.poll() is None

    @property
    def pid(self) -> int | None:
        return self.process.pid


class MCPProcessPool:
    def __init__(
        self, max_processes: int = 30, zombie_check_interval: float = 60.0, idle_timeout_s: float = 600.0
    ) -> None:
        self._max_processes = max_processes
        self._zombie_check_interval = zombie_check_interval
        self._idle_timeout_s = idle_timeout_s
        self._pool: dict[str, PooledProcess] = {}
        self._lock = threading.Lock()
        self._zombie_thread: threading.Thread | None = None
        self._zombie_running = False

    def get_or_create(
        self,
        name: str,
        cmd: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> PooledProcess | None:
        with self._lock:
            entry = self._pool.get(name)
            if entry is not None:
                if entry.is_alive:
                    entry.reuse_count += 1
                    entry.last_used_at = time.monotonic()
                    return entry
                else:
                    self._remove_entry(name)

            if len(self._pool) >= self._max_processes:
                logger.warning(
                    "MCPProcessPool: max processes (%d) reached, cannot create '%s'",
                    self._max_processes,
                    name,
                )
                return None

            if cmd is None:
                return None

            try:
                proc_env = {**os.environ, **(env or {})}
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=proc_env,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
            except Exception:
                logger.exception("MCPProcessPool: failed to create process '%s'", name)
                return None

            entry = PooledProcess(name=name, process=proc)
            self._pool[name] = entry
            logger.info("MCPProcessPool: created process '%s' (pid=%d)", name, proc.pid)
            return entry

    def terminate(self, name: str) -> bool:
        with self._lock:
            entry = self._pool.get(name)
            if entry is None:
                return False
            self._remove_entry(name)
            return True

    def terminate_all(self) -> int:
        with self._lock:
            count = len(self._pool)
            for name in list(self._pool.keys()):
                self._remove_entry(name)
            return count

    def get_stats(self) -> ProcessPoolStats:
        with self._lock:
            active = sum(1 for e in self._pool.values() if e.is_alive)
            zombies = sum(1 for e in self._pool.values() if not e.is_alive)
            reuse = sum(e.reuse_count for e in self._pool.values())
            now = time.monotonic()
            idle = sum(
                1
                for e in self._pool.values()
                if e.is_alive and self._idle_timeout_s > 0 and (now - e.last_used_at) > self._idle_timeout_s
            )
            return ProcessPoolStats(
                active_processes=active,
                max_processes=self._max_processes,
                reuse_count=reuse,
                zombie_count=zombies,
                idle_count=idle,
            )

    def start_zombie_scanner(self) -> None:
        if self._zombie_running:
            return
        self._zombie_running = True
        self._zombie_thread = threading.Thread(
            target=self._zombie_scan_loop,
            daemon=True,
            name="process-pool-zombie-scanner",
        )
        self._zombie_thread.start()

    def stop_zombie_scanner(self) -> None:
        self._zombie_running = False

    def _zombie_scan_loop(self) -> None:
        while self._zombie_running:
            try:
                self._reap_zombies()
            except Exception:
                logger.exception("MCPProcessPool: zombie scan failed")
            time.sleep(self._zombie_check_interval)

    def _reap_zombies(self) -> int:
        with self._lock:
            zombie_names = [name for name, entry in self._pool.items() if not entry.is_alive]
            now = time.monotonic()
            idle_names = [
                name
                for name, entry in self._pool.items()
                if entry.is_alive and self._idle_timeout_s > 0 and (now - entry.last_used_at) > self._idle_timeout_s
            ]
            for name in zombie_names:
                self._remove_entry(name)
                logger.info("MCPProcessPool: reaped zombie process '%s'", name)
            for name in idle_names:
                self._remove_entry(name)
                logger.info(
                    "MCPProcessPool: reaped idle process '%s' (idle_timeout=%.0fs)",
                    name,
                    self._idle_timeout_s,
                )
            return len(zombie_names) + len(idle_names)

    def _remove_entry(self, name: str) -> None:
        entry = self._pool.pop(name, None)
        if entry is not None:
            for stream in (entry.process.stdin, entry.process.stdout, entry.process.stderr):
                if stream is not None:
                    try:
                        stream.close()
                    except Exception:
                        pass
            try:
                entry.process.terminate()
                entry.process.wait(timeout=5.0)
            except Exception:
                try:
                    entry.process.kill()
                    entry.process.wait(timeout=2.0)
                except Exception:
                    pass
