# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.order_state_escalator

# [INVARIANTS] 订单状态机升级不可跳过;超时必须触发升级

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Order State Escalator — v0.10.0 订单状态机升级器。
"""
from __future__ import annotations

class OrderStateEscalator:
    VALID_TRANSITIONS={
        "pending":["submitted","cancelled"],
        "submitted":["filled","partial","rejected"],
        "partial":["filled","cancelled"],
    }

    def validate_transition(self, from_state:str, to_state:str)->bool:
        allowed=self.VALID_TRANSITIONS.get(from_state,[])
        return to_state in allowed

    def escalate_if_suspicious(self, state:str, duration_s:float, threshold_s:float=30.0)->bool:
        return state=="pending" and duration_s>threshold_s
