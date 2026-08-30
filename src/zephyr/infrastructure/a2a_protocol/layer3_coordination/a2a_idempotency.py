# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_idempotency

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
A2A 幂等性保证

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: a2a_idempotency.py
# 层: 算法
# - id: A1
#   name_zh: ① A2AIdempotency
#   name_en: A2AIdempotency
#   intro: class A2AIdempotency 源码 L65-L79
#   desc: 公共方法（定义序）: is_duplicate；源码 L65-L79
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: A2AIdempotency
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class A2AIdempotency:
    def __init__(self):

        self._history: set = set()

    def is_duplicate(self, task_id: str, input_hash: str) -> bool:

        key = f"{task_id}:{input_hash}"

        if key in self._history:
            return True

        self._history.add(key)

        return False
