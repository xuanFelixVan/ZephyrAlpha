"""health subsystem — 模块健康注册与 LifecycleManager 对接（最小可用骨架）."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class HealthStatus:
    module_id: str
    status: str = "UNKNOWN"
    last_heartbeat: str = ""
    registered_at: str = ""

    def __post_init__(self):
        self.registered_at = datetime.now(timezone.utc).isoformat()


class HealthSubsystem:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode
        self._status = HealthStatus(module_id=module_id)

    def register(self) -> HealthStatus:
        if self._test_mode:
            return self._status
        self._status.status = "HEALTHY"
        self._status.last_heartbeat = datetime.now(timezone.utc).isoformat()
        return self._status

    def heartbeat(self) -> None:
        if not self._test_mode:
            self._status.last_heartbeat = datetime.now(timezone.utc).isoformat()

    def set_unhealthy(self, reason: str = "") -> None:
        self._status.status = f"UNHEALTHY: {reason}" if reason else "UNHEALTHY"

    def shutdown(self) -> None:
        self._status.status = "SHUTDOWN"
