# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.human_factors
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 疲劳/情绪检测不可禁用;人因告警必须升级
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_human_factors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Human Factors — v0.7.0 人因工程: 通知疲劳管理+上下文简洁性+多通道notifications。
"""

from __future__ import annotations

import time


class HumanFactors:
    def __init__(self):
        self._notification_count: dict[str, int] = {}
        self._last_notified: dict[str, float] = {}
        self._min_interval_s = 300
        self._max_per_hour = 12

    def should_notify(self, owner_id: str) -> tuple[bool, str]:
        now = time.time()
        window_start = now - 3600
        recent = [
            t for t_owner, t in [(o, lt) for o, lt in self._last_notified.items() if o == owner_id] if t > window_start
        ]
        if len(recent) >= self._max_per_hour:
            return False, "Rate limited"
        if owner_id in self._last_notified and now - self._last_notified[owner_id] < self._min_interval_s:
            return False, "Too frequent"
        self._last_notified[owner_id] = now
        self._notification_count[owner_id] = self._notification_count.get(owner_id, 0) + 1
        return True, "OK"
