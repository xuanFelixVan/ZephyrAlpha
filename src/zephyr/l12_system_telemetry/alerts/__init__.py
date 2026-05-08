"""alerts subsystem — 告警触发与级别管理（最小可用骨架）."""

from enum import Enum


class AlertLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertSubsystem:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode

    def fire(self, level: AlertLevel, message: str, labels: dict | None = None) -> dict:
        alert = {
            "module_id": self._module_id,
            "level": level.value,
            "message": message,
            "labels": labels or {},
            "fired": not self._test_mode,
        }
        return alert

    def health(self) -> dict:
        return {"module_id": self._module_id, "pending_alerts": 0}
