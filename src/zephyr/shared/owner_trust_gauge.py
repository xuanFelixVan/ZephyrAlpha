"""
Owner Trust Gauge — Owner 信任度量仪 (盲点 #64)
特性：
  - alert_dismissal_rate > 30% → CRITICALLY_LOW
  - idle > 30min → COMPLACENT
"""
import time
from enum import Enum
from typing import Any, Optional


class TrustLevel(Enum):
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    COMPLACENT = "COMPLACENT"
    CRITICALLY_LOW = "CRITICALLY_LOW"


class OwnerTrustGauge:
    """
    Owner 信任度量 (盲点 #64)
    """

    DISMISSAL_CRITICAL_RATE = 0.30
    IDLE_COMPLACENT_SECONDS = 1800

    def __init__(self):
        self._dismissal_count = 0
        self._total_alerts = 0
        self._last_active = time.time()

    def record_dismissal(self):
        self._dismissal_count += 1
        self._last_active = time.time()

    def record_alert(self):
        self._total_alerts += 1

    def evaluate(self) -> TrustLevel:
        dismissal_rate = self._dismissal_count / max(self._total_alerts, 1)
        idle_time = time.time() - self._last_active

        if dismissal_rate > self.DISMISSAL_CRITICAL_RATE:
            return TrustLevel.CRITICALLY_LOW
        if idle_time > self.IDLE_COMPLACENT_SECONDS:
            return TrustLevel.COMPLACENT
        if dismissal_rate > 0.1:
            return TrustLevel.NORMAL
        return TrustLevel.HIGH

    def report(self) -> dict:
        return {
            "trust_level": self.evaluate().value,
            "dismissal_rate": round(
                self._dismissal_count / max(self._total_alerts, 1), 2
            ),
            "total_alerts": self._total_alerts,
            "total_dismissals": self._dismissal_count,
            "idle_seconds": int(time.time() - self._last_active),
        }
