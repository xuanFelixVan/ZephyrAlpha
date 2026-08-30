# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_forgetting

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
A2A 遗忘机制

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_memory 参数
#   fields: 参数 max_memory（无注解）
#   code: a2a_forgetting.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① A2AForgetting
#   name_en: A2AForgetting
#   intro: class A2AForgetting 源码 L65-L81
#   desc: 公共方法（定义序）: remember；源码 L65-L81
#   inputs: max_memory
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: A2AForgetting
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class A2AForgetting:
    def __init__(self, max_memory: int = 100):

        self._memory: list = []

        self.max_memory = max_memory

    def remember(self, item: dict) -> None:

        self._memory.append(item)

        self._forget()

    def _forget(self) -> None:

        while len(self._memory) > self.max_memory:
            self._memory.pop(0)
