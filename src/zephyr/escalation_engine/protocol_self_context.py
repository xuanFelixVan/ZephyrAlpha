# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.protocol_self_context

# [INVARIANTS] 协议自维护上下文不可丢失;session注入必须执行

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Protocol Self Context — v0.10.0 协议自维护上下文管理器。
"""
from __future__ import annotations

class ProtocolSelfContext:
    def __init__(self):
        self._context:dict={"version":"v0.10.0","active_rules":0,"last_reconcile":None}

    def update_metrics(self, active_rules:int):
        self._context["active_rules"]=active_rules

    def snapshot(self)->dict:
        return dict(self._context)
