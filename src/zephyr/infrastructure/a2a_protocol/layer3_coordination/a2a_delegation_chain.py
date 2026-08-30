# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_delegation_chain

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
委托链

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: a2a_delegation_chain.py
# 层: 算法
# - id: A1
#   name_zh: ① A2ADelegationChain
#   name_en: A2ADelegationChain
#   intro: class A2ADelegationChain 源码 L65-L83
#   desc: 公共方法（定义序）: delegate；源码 L65-L83
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: A2ADelegationChain
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class A2ADelegationChain:
    MAX_DEPTH = 5

    def __init__(self):

        self._chains: dict = {}

    def delegate(self, task_id: str, from_agent: str, to_agent: str) -> dict:

        chain = self._chains.get(task_id, [])

        if len(chain) >= self.MAX_DEPTH:
            return {"task_id": task_id, "error": "max_depth_exceeded"}

        chain.append({"from": from_agent, "to": to_agent})

        self._chains[task_id] = chain

        return {"task_id": task_id, "depth": len(chain)}
