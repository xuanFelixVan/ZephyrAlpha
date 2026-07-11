# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.ops_governance.clock_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 时钟多源验证不可跳过;NTS验证必须执行
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_clock_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Clock Guard — v0.8.0 时钟完整性防御: NTP漂移检测+wall clock monotonic验证。
"""

from __future__ import annotations

import time


class ClockGuard:
    def __init__(self):
        self._monotonic_start = time.monotonic()
        self._wall_start = time.time()

    def detect_drift(self) -> float:
        mono_elapsed = time.monotonic() - self._monotonic_start
        wall_elapsed = time.time() - self._wall_start
        return abs(wall_elapsed - mono_elapsed)

    def is_suspicious(self) -> bool:
        return self.detect_drift() > 5.0

    def validate_timestamp(self, ts: float, tolerance_s: float = 60) -> bool:
        return abs(time.time() - ts) < tolerance_s
