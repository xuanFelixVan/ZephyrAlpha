# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.cascade_guard

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
级联守卫——防止失败在Agent间级联

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: threshold 参数
#   fields: 参数 threshold（无注解）
#   code: cascade_guard.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CascadeGuard
#   name_en: CascadeGuard
#   intro: class CascadeGuard 源码 L65-L80
#   desc: 公共方法（定义序）: check, record_failure；源码 L65-L80
#   inputs: threshold
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CascadeGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class CascadeGuard:
    def __init__(self, threshold: int = 5):

        self.threshold = threshold

        self._failure_count: dict = {}

    def check(self, agent_id: str) -> bool:

        return self._failure_count.get(agent_id, 0) < self.threshold

    def record_failure(self, agent_id: str) -> int:

        self._failure_count[agent_id] = self._failure_count.get(agent_id, 0) + 1

        return self._failure_count[agent_id]
