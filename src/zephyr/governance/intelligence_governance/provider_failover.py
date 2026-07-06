# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.provider_failover
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 降级链顺序不可逆;ALL_STOP必须可触发
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_provider_failover | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Provider Failover — v0.7.0 多LLM Provider容灾: deepseek→claude→gpt fallback链。
"""

from __future__ import annotations

from typing import Final
FALLBACK_CHAIN: Final[list] = ["deepseek", "claude", "gpt"]


class ProviderFailover:
    def __init__(self):
        self._healthy: dict[str, bool] = {p: True for p in FALLBACK_CHAIN}

    def mark_unhealthy(self, provider: str):
        self._healthy[provider] = False

    def mark_healthy(self, provider: str):
        self._healthy[provider] = True

    def get_available(self) -> str:
        for p in FALLBACK_CHAIN:
            if self._healthy.get(p, False):
                return p
        return "none"

    def is_degraded(self) -> bool:
        return self.get_available() != FALLBACK_CHAIN[0]
