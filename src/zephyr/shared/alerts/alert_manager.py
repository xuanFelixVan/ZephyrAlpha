# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.alerts.alert_manager
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__; zephyr.feedback_loop.auto_evolution; zephyr.security.llm_defense.llm_security.layers.l6_observability; tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    alert_id: str
    title: str
    severity: AlertSeverity
    source: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


class AlertManager:
    def __init__(self, max_alerts: int = 1000):
        self._alerts: list[Alert] = []
        self._max_alerts = max_alerts

    def create(self, title: str, severity: AlertSeverity, source: str, message: str, **metadata: Any) -> Alert:
        alert = Alert(
            alert_id=str(uuid.uuid4())[:8],
            title=title,
            severity=severity,
            source=source,
            message=message,
            metadata=metadata,
        )
        self._alerts.append(alert)
        if len(self._alerts) > self._max_alerts:
            self._alerts = self._alerts[-self._max_alerts :]
        return alert

    def raise_alert(self, title: str, severity: AlertSeverity, source: str, message: str, **metadata: Any) -> Alert:
        return self.create(title, severity, source, message, **metadata)

    def acknowledge(self, alert_id: str) -> bool:
        for a in self._alerts:
            if a.alert_id == alert_id:
                a.acknowledged = True
                return True
        return False

    def get_active(self) -> list[Alert]:
        return [a for a in self._alerts if not a.acknowledged]

    def get_by_severity(self, severity: AlertSeverity) -> list[Alert]:
        return [a for a in self._alerts if a.severity == severity]
