# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.livelock_detector

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
P2: 活锁检测器

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: cycle_limit 参数
#   fields: 参数 cycle_limit（无注解）
#   code: livelock_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LivelockDetector
#   name_en: LivelockDetector
#   intro: class LivelockDetector 源码 L65-L82
#   desc: 公共方法（定义序）: check_cycle, record_state；源码 L65-L82
#   inputs: cycle_limit
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: LivelockDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class LivelockDetector:
    def __init__(self, cycle_limit: int = 10):

        self._state_history: dict = {}

        self.cycle_limit = cycle_limit

    def check_cycle(self, agent_id: str, state_hash: str) -> bool:

        history = self._state_history.setdefault(agent_id, [])

        count = history.count(state_hash)

        return count >= self.cycle_limit

    def record_state(self, agent_id: str, state_hash: str) -> None:

        self._state_history.setdefault(agent_id, []).append(state_hash)
