# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.financial_governance.flash_crash_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 闪崩双轨熔断必须可用;MWCB 7/13/20%阈值不可修改
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_flash_crash_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Flash Crash Guard — v0.12.0 闪崩双轨熔断器。
"""

from __future__ import annotations

import time


class FlashCrashGuard:
    LIQUIDITY_THRESHOLD = 50.0
    VELOCITY_THRESHOLD = 60.0

    def __init__(self):
        self._tripped = False
        self._trip_time = 0.0

    def evaluate(self, price_drop_pct: float, velocity_pct_per_s: float, bid_ask_spread_pct: float) -> bool:
        if price_drop_pct > self.LIQUIDITY_THRESHOLD or velocity_pct_per_s > self.VELOCITY_THRESHOLD:
            self._tripped = True
            self._trip_time = time.time()
            return True
        return False

    @property
    def tripped(self) -> bool:
        return self._tripped

    def reset(self):
        self._tripped = False
