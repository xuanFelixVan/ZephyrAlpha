# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.escalation_fatigue_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 升级疲劳管理不可禁用;adaptive阈值不可手动覆盖
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_escalation_fatigue_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Escalation Fatigue Manager — v0.11.0 升级疲劳管理器。
"""

from __future__ import annotations

import time


class EscalationFatigueManager:
    def __init__(self):
        self._owner_escalations: dict[str, list[float]] = {}
        self._cooldown_h = 4
        self._max_daily = 6

    def record_escalation(self, owner_id: str) -> bool:
        now = time.time()
        recent = [t for t in self._owner_escalations.get(owner_id, []) if now - t < 86400]
        if len(recent) >= self._max_daily:
            return False
        last = [t for t in self._owner_escalations.get(owner_id, []) if now - t < self._cooldown_h * 3600]
        if last:
            return False
        self._owner_escalations.setdefault(owner_id, []).append(now)
        return True
