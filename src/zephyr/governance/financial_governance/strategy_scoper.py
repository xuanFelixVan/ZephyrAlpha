# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.financial_governance.strategy_scoper
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 策略范围隔离不可绕过;跨策略操作必须显式授权
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_strategy_scoper | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Strategy Scoper — v0.6.0 策略范围隔离器: SIG/Strat/Capital多层策略隔离。
"""

from __future__ import annotations

from enum import Enum


class ScopeLevel(Enum):
    SIG = "sig"
    STRATEGY = "strategy"
    CAPITAL = "capital"


class StrategyScoper:
    def __init__(self):
        self._scopes: dict[str, ScopeLevel] = {}

    def assign_scope(self, agent_id: str, scope: ScopeLevel):
        self._scopes[agent_id] = scope

    def can_access(self, agent_id: str, target_scope: ScopeLevel) -> bool:
        agent_scope = self._scopes.get(agent_id)
        if agent_scope is None:
            return False
        order = [ScopeLevel.SIG, ScopeLevel.STRATEGY, ScopeLevel.CAPITAL]
        return order.index(agent_scope) <= order.index(target_scope)
