# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.alerts.dual_channel_alert
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__; zephyr.feedback_loop.auto_evolution; tests.unit.shared.test_orphan_integration
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

from dataclasses import dataclass
from enum import Enum


class Channel(Enum):
    DASHBOARD = "dashboard"
    MESSAGING = "messaging"


@dataclass
class DualAlert:
    title: str
    message: str
    dashboard_sent: bool = False
    messaging_sent: bool = False


class DualChannelAlert:
    def __init__(self):
        self._alerts: list[DualAlert] = []

    def send(
        self, title: str, message: str, channels: tuple[Channel, ...] = (Channel.DASHBOARD, Channel.MESSAGING)
    ) -> DualAlert:
        alert = DualAlert(
            title=title,
            message=message,
            dashboard_sent=Channel.DASHBOARD in channels,
            messaging_sent=Channel.MESSAGING in channels,
        )
        self._alerts.append(alert)
        return alert

    def get_failed_channels(self) -> list[tuple[DualAlert, list[Channel]]]:
        result = []
        for a in self._alerts:
            failed = []
            if not a.dashboard_sent:
                failed.append(Channel.DASHBOARD)
            if not a.messaging_sent:
                failed.append(Channel.MESSAGING)
            if failed:
                result.append((a, failed))
        return result
