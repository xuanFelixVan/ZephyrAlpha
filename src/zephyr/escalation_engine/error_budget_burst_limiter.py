# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.error_budget_burst_limiter

# [INVARIANTS] Error Budget Burst限制不可绕过;daily≤20%/hourly≤5%

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Error Budget Burst Limiter — v0.11.0 错误预算Burst限流器。
"""
from __future__ import annotations
import time

class BurstLimiter:
    def __init__(self):
        self._burst_window_s=60
        self._max_burst=10
        self._requests:list[float]=[]

    def allow(self)->bool:
        now=time.time()
        self._requests=[t for t in self._requests if now-t<self._burst_window_s]
        if len(self._requests)>=self._max_burst:
            return False
        self._requests.append(now)
        return True
