# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.trigger_monitor
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
触发监控器

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: trigger_monitor.py
# 层: 算法
# - id: A1
#   name_zh: ① TriggerMonitor
#   name_en: TriggerMonitor
#   intro: class TriggerMonitor 源码 L49-L69
#   desc: 公共方法（定义序）: triggers, watch, check；源码 L49-L69
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: TriggerMonitor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class TriggerMonitor:
    def __init__(self):
        self._triggers: dict = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def triggers(self) -> dict:
        """只读：triggers（Stage 4 公共化）。"""
        return self._triggers

    @triggers.setter
    def triggers(self, value):
        """写入：triggers（Stage 4 公共化）。"""
        self._triggers = value

    def watch(self, trigger_id: str, condition: callable) -> None:
        self._triggers[trigger_id] = condition

    def check(self, trigger_id: str, context: dict) -> bool:
        fn = self._triggers.get(trigger_id)
        return fn(context) if fn else False
