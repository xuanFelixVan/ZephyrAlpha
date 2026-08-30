# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_idle_guard

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
A2A 空闲守卫

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: idle_timeout 参数
#   fields: 参数 idle_timeout（无注解）
#   code: a2a_idle_guard.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① A2AIdleGuard
#   name_en: A2AIdleGuard
#   intro: class A2AIdleGuard 源码 L65-L72
#   desc: 公共方法（定义序）: check_idle；源码 L65-L72
#   inputs: idle_timeout
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: A2AIdleGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class A2AIdleGuard:
    def __init__(self, idle_timeout: float = 300):

        self.idle_timeout = idle_timeout

    def check_idle(self, agent_id: str, last_active: float, now: float) -> bool:

        return (now - last_active) > self.idle_timeout
