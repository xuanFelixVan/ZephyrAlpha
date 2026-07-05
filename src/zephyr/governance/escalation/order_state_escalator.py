# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.order_state_escalator
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 订单状态机升级不可跳过;超时必须触发升级
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_order_state_escalator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Order State Escalator — v0.10.0 订单状态机升级器。
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
