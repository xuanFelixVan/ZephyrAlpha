# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.account_isolator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 多账户隔离不可绕过;per-account熔断必须独立
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_account_isolator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Account Isolator — v0.10.0 多账户升级隔离器。
"""

from __future__ import annotations


class AccountIsolator:
    def __init__(self):
        self._bindings: dict[str, str] = {}

    def bind(self, account_id: str, escalation_policy: str):
        self._bindings[account_id] = escalation_policy

    def get_policy(self, account_id: str) -> str:
        return self._bindings.get(account_id, "default_blocked")

    def isolate_account(self, account_id: str) -> bool:
        return account_id in self._bindings
