# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.alerts.alert_escalation
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] tests.unit.shared.test_orphan_integration
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
"""AlertEscalation — re-homed to eliminate shared->infrastructure circular import."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from zephyr.shared.utils.time_utils import now_utc

__all__ = ["AlertEscalation", "EscalationLevel"]


class EscalationLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AlertEscalation(BaseModel):
    """告警触达——触发->分级->行动->超时->自动升级。

    Re-homed from infrastructure_runtime_integration.pipeline.pipeline_roadmap.AlertEscalationTracker
    to eliminate shared->infrastructure circular import.
    """

    alert_id: str = Field(default="")
    title: str = Field(default="")
    level: EscalationLevel = Field(default=EscalationLevel.WARNING)
    source: str = Field(default="")
    triggered_at: str = Field(default_factory=lambda: now_utc().isoformat())
    acknowledged_at: str | None = None
    resolved_at: str | None = None
    escalation_chain: list[str] = Field(default_factory=list)
    auto_escalate_after_seconds: int = 300
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_resolved(self) -> bool:
        return self.resolved_at is not None

    @property
    def is_acknowledged(self) -> bool:
        return self.acknowledged_at is not None
