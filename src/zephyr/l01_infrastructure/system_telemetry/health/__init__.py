# [BLUEPRINT] MOD-INF-015 | docs/03_modules/l01_infrastructure/system-telemetry/blueprint.md | §3
# [MODULE] zephyr.l01_infrastructure.system_telemetry.health
# [INVARIANTS] HEALTHY/DEGRADED/DOWN triple-state; register before use; thread-safe status transitions
# [MODIFY-GUARD] facade.py; health_probes.py; health_aggregator.py
# [CONSUMERS] zephyr.agent_rbac
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError; RuntimeError
# [TESTS] tests/system_telemetry/test_health.py
"""health subsystem — 模块健康注册与 LifecycleManager 对接."""

from __future__ import annotations

import threading
import time


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

    def heartbeat(self) -> None:
        with self._lock:
            self._last_check = time.time()

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

    def set_healthy(self) -> dict:
        with self._lock:
            self._status = self.STATUS_HEALTHY
            self._reason = ""
            self._last_check = time.time()
        return {
            "action": "set_healthy",
            "module_id": self._module_id,
            "status": self._status,
            "ts": self._last_check,
        }

    def status(self) -> dict:
        with self._lock:
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
