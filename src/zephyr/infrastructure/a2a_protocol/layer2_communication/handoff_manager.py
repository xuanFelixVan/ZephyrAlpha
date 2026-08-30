# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.handoff_manager
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] core types imported from zephyr.shared.protocols.a2a; no duplicate definitions
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Handoff Manager — Agent 间任务交接

Core type (HandoffRecord) is imported from
zephyr.shared.protocols.a2a.a2a_schemas.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: handoff_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① HandoffManager
#   name_en: HandoffManager
#   intro: class HandoffManager 源码 L54-L71
#   desc: 公共方法（定义序）: handoff, acknowledge, get_active_handoffs；源码 L54-L71
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: HandoffManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.protocols.a2a.a2a_schemas import HandoffRecord


class HandoffManager:
    def __init__(self):
        self._history: list = []

    def handoff(self, from_agent: str, to_agent: str, task_id: str, reason: str) -> HandoffRecord:
        record = HandoffRecord(from_agent, to_agent, task_id, reason)
        self._history.append(record)
        return record

    def acknowledge(self, to_agent: str, task_id: str) -> bool:
        for record in reversed(self._history):
            if record.to_agent == to_agent and record.task_id == task_id:
                record.acknowledged = True
                return True
        return False

    def get_active_handoffs(self) -> list:
        return [r for r in self._history if not r.acknowledged]
