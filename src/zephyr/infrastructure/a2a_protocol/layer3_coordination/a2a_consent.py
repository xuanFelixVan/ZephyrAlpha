# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_consent

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
P2: Agent同意管理

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: a2a_consent.py
# 层: 算法
# - id: A1
#   name_zh: ① A2AConsent
#   name_en: A2AConsent
#   intro: class A2AConsent 源码 L65-L83
#   desc: 公共方法（定义序）: grant, revoke；源码 L65-L83
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: A2AConsent
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class A2AConsent:
    def __init__(self):

        self._consents: dict = {}

    def grant(self, agent_id: str, scope: str, granted_by: str) -> dict:

        self._consents.setdefault(agent_id, {})

        self._consents[agent_id][scope] = {"granted": True, "by": granted_by}

        return {"agent": agent_id, "scope": scope, "consent": True}

    def revoke(self, agent_id: str, scope: str) -> dict:

        if agent_id in self._consents:
            self._consents[agent_id].pop(scope, None)

        return {"agent": agent_id, "scope": scope, "revoked": True}
