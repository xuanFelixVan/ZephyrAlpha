# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.protocol_self_context
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 协议自维护上下文不可丢失;session注入必须执行
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_protocol_self_context | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Protocol Self Context — v0.10.0 协议自维护上下文管理器。
"""

from __future__ import annotations


class ProtocolSelfContext:
    def __init__(self):
        self._context: dict = {"version": "v0.10.0", "active_rules": 0, "last_reconcile": None}

    def update_metrics(self, active_rules: int):
        self._context["active_rules"] = active_rules

    def snapshot(self) -> dict:
        return dict(self._context)
