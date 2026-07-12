# [A_module] module_id: MOD-INF-015_profiles | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.profiles
# [INVARIANTS] start/stop/snapshot must not block; test_mode returns mock data; thread-safe using threading.Lock
# [MODIFY-GUARD] facade.py; __init__.py
# [CONSUMERS] zephyr.security.access_control
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RuntimeError
# [TESTS] tests/system-telemetry/test_profiles.py
# [TTL] permanent
"""ProfileSubsystem — 系统资源画像（MOD-INF-015 §6 · profiles）.

提供轻量级 CPU/内存/磁盘使用率采集，支持 start/stop/snapshot API。
在 test_mode=True 时返回模拟数据，不调用 psutil。
"""

from __future__ import annotations

import threading
import time


class ProfileSubsystem:
    def __init__(self, module_id: str = "", test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode
        self._active_profile: str | None = None
        self._start_time: float = 0.0
        self._lock = threading.Lock()

    def start(self, label: str = "") -> dict:
        with self._lock:
            self._active_profile = label
            self._start_time = time.perf_counter()
        return {"name": label, "action": "start", "module_id": self._module_id}

    def stop(self) -> dict:
        with self._lock:
            elapsed = time.perf_counter() - self._start_time if self._start_time > 0 else 0.0
            name = self._active_profile
            self._active_profile = None
            self._start_time = 0.0
        return {
            "name": name,
            "action": "stop",
            "elapsed_s": round(elapsed, 6),
            "module_id": self._module_id,
            "elapsed_ms": round(elapsed * 1000, 3),
        }

    def snapshot(self) -> dict:
        if self._test_mode:
            return {
                "module_id": self._module_id,
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0,
                "open_files": 0,
                "thread_count": 0,
                "test_mode": True,
            }
        try:
            import psutil

            proc = psutil.Process()
            mem = proc.memory_info()
            disk = psutil.disk_usage("/")
            return {
                "module_id": self._module_id,
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_percent": proc.memory_percent(),
                "memory_mb": round(mem.rss / (1024 * 1024), 2),
                "disk_percent": disk.percent,
                "open_files": len(proc.open_files()),
                "thread_count": proc.num_threads(),
                "test_mode": False,
            }
        except Exception:
            return {
                "module_id": self._module_id,
                "cpu_percent": -1.0,
                "memory_mb": 0.0,
                "disk_percent": -1.0,
                "error": "psutil unavailable",
            }


__all__ = ["ProfileSubsystem", "disk", "elapsed", "mem", "name", "proc", "snapshot", "start", "stop"]
