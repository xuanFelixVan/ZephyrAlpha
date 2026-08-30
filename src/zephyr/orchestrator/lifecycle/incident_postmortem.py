# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle.incident_postmortem
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
事件复盘管理器（CT-INCIDENT）——incident记录+timeline+action_items+postmortem。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: incident_postmortem.py
# 层: 算法
# - id: A1
#   name_zh: ① IncidentManager
#   name_en: IncidentManager
#   intro: class IncidentManager 源码 L64-L89
#   desc: 公共方法（定义序）: incidents, create, add_action_item；源码 L64-L89
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: IncidentManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Incident(BaseModel):
    incident_id: str
    severity: str = "P2"
    description: str = ""
    timeline: list[dict] = Field(default_factory=list)
    root_cause: str = ""
    action_items: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IncidentManager:
    def __init__(self):
        self._incidents: dict[str, Incident] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def incidents(self) -> dict[str, Incident]:
        """只读：incidents（Stage 4 公共化）。"""
        return self._incidents

    @incidents.setter
    def incidents(self, value):
        """写入：incidents（Stage 4 公共化）。"""
        self._incidents = value

    def create(self, incident_id: str, description: str, severity: str = "P2") -> Incident:
        inc = Incident(incident_id=incident_id, description=description, severity=severity)
        self._incidents[incident_id] = inc
        return inc

    def add_action_item(self, incident_id: str, action: str) -> bool:
        inc = self._incidents.get(incident_id)
        if inc is None:
            return False
        inc.action_items.append(action)
        return True
