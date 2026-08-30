# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.order_state_escalator
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 订单状态机升级不可跳过;超时必须触发升级
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Order State Escalator — v0.10.0 订单状态机升级器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: order_state_escalator.py
# 层: 算法
# - id: A1
#   name_zh: ① OrderStateEscalator
#   name_en: OrderStateEscalator
#   intro: class OrderStateEscalator 源码 L51-L63
#   desc: 公共方法（定义序）: validate_transition, escalate_if_suspicious；源码 L51-L63
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: OrderStateEscalator
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class OrderStateEscalator:
    VALID_TRANSITIONS = {
        "pending": ["submitted", "cancelled"],
        "submitted": ["filled", "partial", "rejected"],
        "partial": ["filled", "cancelled"],
    }

    def validate_transition(self, from_state: str, to_state: str) -> bool:
        allowed = self.VALID_TRANSITIONS.get(from_state, [])
        return to_state in allowed

    def escalate_if_suspicious(self, state: str, duration_s: float, threshold_s: float = 30.0) -> bool:
        return state == "pending" and duration_s > threshold_s
