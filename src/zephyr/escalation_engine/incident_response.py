# [BLUEPRINT] MOD-INF-022 | docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md
# [MODULE] zephyr.escalation_engine
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md;src/zephyr/escalation_engine/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IncidentLevel(str, Enum):
    L1_INSTANT = "L1_INSTANT"
    L2_DEGRADED = "L2_DEGRADED"
    L3_PARTIAL = "L3_PARTIAL"
    L4_TOTAL = "L4_TOTAL"
    L5_CATASTROPHIC = "L5_CATASTROPHIC"


class IncidentProtocol(BaseModel):
    level: IncidentLevel
    label: str
    response_time_minutes: int
    escalation_chain: list[str] = Field(default_factory=list)
    notification_channel: str = "log"
    postmortem_required: bool = False


INCIDENT_PROTOCOLS: dict[IncidentLevel, IncidentProtocol] = {
    IncidentLevel.L1_INSTANT: IncidentProtocol(
        level=IncidentLevel.L1_INSTANT,
        label="瞬时故障 (<5min)",
        response_time_minutes=5,
        escalation_chain=["AI自修复"],
        notification_channel="log",
        postmortem_required=False,
    ),
    IncidentLevel.L2_DEGRADED: IncidentProtocol(
        level=IncidentLevel.L2_DEGRADED,
        label="持续降级 (<30min)",
        response_time_minutes=30,
        escalation_chain=["AI自修复", "告警通知"],
        notification_channel="telemetry",
        postmortem_required=False,
    ),
    IncidentLevel.L3_PARTIAL: IncidentProtocol(
        level=IncidentLevel.L3_PARTIAL,
        label="部分功能丧失 (<2h)",
        response_time_minutes=120,
        escalation_chain=["AI自修复", "告警通知", "Owner通知"],
        notification_channel="email",
        postmortem_required=True,
    ),
    IncidentLevel.L4_TOTAL: IncidentProtocol(
        level=IncidentLevel.L4_TOTAL,
        label="全系统故障 (<8h)",
        response_time_minutes=480,
        escalation_chain=["AI自修复", "告警通知", "Owner通知", "全部Stop"],
        notification_channel="sms+email",
        postmortem_required=True,
    ),
    IncidentLevel.L5_CATASTROPHIC: IncidentProtocol(
        level=IncidentLevel.L5_CATASTROPHIC,
        label="灾难级",
        response_time_minutes=9999,
        escalation_chain=["立即Stop", "Rollback", "Owner直连", "法律/合规通知"],
        notification_channel="all_channels",
        postmortem_required=True,
    ),
}


def get_protocol(level: IncidentLevel) -> Optional[IncidentProtocol]:
    return INCIDENT_PROTOCOLS.get(level)


def escalate(current: IncidentLevel) -> list[IncidentLevel]:
    levels = list(IncidentLevel)
    idx = levels.index(current) if current in levels else -1
    if idx < 0:
        return []
    return levels[idx:] if idx < len(levels) else []
