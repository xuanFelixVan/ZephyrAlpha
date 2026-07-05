# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.error_budget_burst_limiter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Error Budget Burst限制不可绕过;daily≤20%/hourly≤5%
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_error_budget_burst_limiter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Error Budget Burst Limiter — v0.11.0 错误预算Burst限流器。
"""

from __future__ import annotations

import time


class BurstLimiter:
    def __init__(self):
        self._burst_window_s = 60
        self._max_burst = 10
        self._requests: list[float] = []

    def allow(self) -> bool:
        now = time.time()
        self._requests = [t for t in self._requests if now - t < self._burst_window_s]
        if len(self._requests) >= self._max_burst:
            return False
        self._requests.append(now)
        return True
