# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.incident_response
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md;src/zephyr/escalation-engine/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: level 参数
#   fields: 参数 level，类型注解 IncidentLevel
#   code: incident_response.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: current 参数
#   fields: 参数 current，类型注解 IncidentLevel
#   code: incident_response.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_protocol
#   name_en: get_protocol
#   intro: get_protocol(level) 源码 L136-L137
#   desc: 源码 L136-L137
#   inputs: level
#   outputs: IncidentProtocol | None
# - id: A2
#   name_zh: ② escalate
#   name_en: escalate
#   intro: escalate(current) 源码 L140-L145
#   desc: 源码 L140-L145
#   inputs: current
#   outputs: list[IncidentLevel]
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: IncidentProtocol | None
#   name_en: IncidentProtocol | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-020;MOD-INF-018
# - id: O2
#   name_zh: list[IncidentLevel]
#   name_en: list[IncidentLevel]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-020;MOD-INF-018
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final

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


INCIDENT_PROTOCOLS: Final[dict[IncidentLevel, IncidentProtocol]] = {
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


def get_protocol(level: IncidentLevel) -> IncidentProtocol | None:
    return INCIDENT_PROTOCOLS.get(level)


def escalate(current: IncidentLevel) -> list[IncidentLevel]:
    levels = list(IncidentLevel)
    idx = levels.index(current) if current in levels else -1
    if idx < 0:
        return []
    return levels[idx:] if idx < len(levels) else []
