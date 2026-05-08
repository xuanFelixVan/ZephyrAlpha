"""
Alert Escalation — 告警升级与闭环确认 (盲点 #50)
特性：
  - SEV-2 → SEV-1 升级规则
  - 闭环确认机制：Owner 确认 / AI 自动确认
"""
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional


class AlertSeverity(IntEnum):
    INFO = 0
    SEV_3 = 1
    SEV_2 = 2
    SEV_1 = 3


@dataclass
class EscalationState:
    alert_id: str
    current_severity: AlertSeverity
    escalated: bool = False
    escalated_to: Optional[AlertSeverity] = None
    escalated_at: float = 0.0
    acknowledged: bool = False
    acknowledged_at: float = 0.0


class AlertEscalation:
    """
    告警升级与闭环确认 (盲点 #50)
    """

    ACK_TIMEOUT_SECONDS = 600

    def __init__(self):
        self._states: dict[str, EscalationState] = {}
        self._escalation_rules = {
            (AlertSeverity.SEV_3, AlertSeverity.SEV_2): 1800,
            (AlertSeverity.SEV_2, AlertSeverity.SEV_1): 900,
        }

    def register_alert(self, alert_id: str, severity: AlertSeverity):
        self._states[alert_id] = EscalationState(
            alert_id=alert_id, current_severity=severity
        )

    def check(self, alert_id: str) -> EscalationState:
        state = self._states.get(alert_id)
        if state is None or state.acknowledged:
            return state or EscalationState(alert_id=alert_id,
                                             current_severity=AlertSeverity.INFO)

        elapsed = time.time() - max(state.escalated_at, time.time())
        for (from_sev, to_sev), timeout in self._escalation_rules.items():
            if state.current_severity == from_sev and elapsed > timeout:
                state.escalated = True
                state.escalated_to = to_sev
                state.escalated_at = time.time()
                state.current_severity = to_sev

        return state

    def acknowledge(self, alert_id: str):
        state = self._states.get(alert_id)
        if state:
            state.acknowledged = True
            state.acknowledged_at = time.time()
