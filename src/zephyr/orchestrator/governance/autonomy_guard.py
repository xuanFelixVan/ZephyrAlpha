# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.autonomy_guard
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Owner 缺位分级自治（CT-AUTONOMY）——Owner离线->自动降级->最小安全运行。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: autonomy_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① AutonomyGuard
#   name_en: AutonomyGuard
#   intro: class AutonomyGuard 源码 L49-L60
#   desc: 公共方法（定义序）: get_allowed_actions, can_autonomously；源码 L49-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AutonomyGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class AutonomyGuard:
    AUTONOMY_LEVELS: dict[str, list[str]] = {
        "level1": ["health_check", "metrics_collect", "dlq_replay"],
        "level2": ["auto_mitigate_p2", "restart_unhealthy"],
        "level3": ["rollback_deploy", "repartition_data"],
    }

    def get_allowed_actions(self, level: str) -> list[str]:
        return self.AUTONOMY_LEVELS.get(level, [])

    def can_autonomously(self, action: str, level: str) -> bool:
        return action in self.get_allowed_actions(level)
