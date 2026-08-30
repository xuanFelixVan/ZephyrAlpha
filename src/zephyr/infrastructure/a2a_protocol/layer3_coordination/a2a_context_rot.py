# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_context_rot

# [DOMAIN] D_INFRA_A2A

# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer3_coordination.__init__

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
上下文腐烂检测

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: a2a_context_rot.py
# 层: 算法
# - id: A1
#   name_zh: ① A2AContextRot
#   name_en: A2AContextRot
#   intro: class A2AContextRot 源码 L65-L68
#   desc: 公共方法（定义序）: detect_rot；源码 L65-L68
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: A2AContextRot
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class A2AContextRot:
    def detect_rot(self, context_data: dict, age_seconds: float) -> float:

        return min(1.0, age_seconds / 3600)  # 线性衰减，1小时100%腐烂
