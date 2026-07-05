# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_switch_governor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 上下文切换预算不可超限;daily_capacity=16不可修改
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_context_switch_governor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Context Switch Governor — v0.11.0 Owner上下文切换预算管理器。
"""

from __future__ import annotations


class ContextSwitchGovernor:
    def __init__(self):
        self._daily_switches: dict[str, int] = {}
        self._max_switches_per_owner = 12

    def can_switch(self, owner_id: str) -> bool:
        current = self._daily_switches.get(owner_id, 0)
        return current < self._max_switches_per_owner

    def record_switch(self, owner_id: str):
        self._daily_switches[owner_id] = self._daily_switches.get(owner_id, 0) + 1
