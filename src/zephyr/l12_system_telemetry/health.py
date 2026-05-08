"""HealthSubsystem — 系统健康检查注册表（MOD-INF-015 §7 · health）.

提供 register/set_unhealthy/shutdown API。
注册后，在 Dashboard 中显示为绿色 HEALTHY 块；set_unhealthy → 变红 DEGRADED。
"""

from __future__ import annotations

import time
import threading


class HealthSubsystem:
    STATUS_HEALTHY = "HEALTHY"
    STATUS_DEGRADED = "DEGRADED"
    STATUS_DOWN = "DOWN"

    def __init__(self, module_id: str = "", test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode
        self._status = self.STATUS_HEALTHY
        self._last_check: float = 0.0
        self._reason: str = ""
        self._lock = threading.Lock()

    def register(self) -> dict:
        with self._lock:
            self._last_check = time.time()
            self._status = self.STATUS_HEALTHY
        return {
            "action": "register",
            "module_id": self._module_id,
            "status": self._status,
            "ts": self._last_check,
        }

    def set_unhealthy(self, reason: str = "") -> dict:
        with self._lock:
            self._status = self.STATUS_DEGRADED
            self._reason = reason
            self._last_check = time.time()
        return {
            "action": "set_unhealthy",
            "module_id": self._module_id,
            "status": self._status,
            "reason": reason,
            "ts": self._last_check,
        }

    def status(self) -> dict:
        return {
            "module_id": self._module_id,
            "status": self._status,
            "reason": self._reason,
            "last_check": self._last_check,
            "test_mode": self._test_mode,
        }

    def shutdown(self) -> dict:
        with self._lock:
            self._status = self.STATUS_DOWN
            self._last_check = time.time()
        return {
            "action": "shutdown",
            "module_id": self._module_id,
            "status": self._status,
            "ts": self._last_check,
        }
