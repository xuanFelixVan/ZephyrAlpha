# [A_module] module_id=MOD-INF_owner_health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md

# [MODULE] zephyr.infrastructure.capacity_assurance.owner_health_monitor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Owner Health Monitor — Owner 决策疲劳检测 (盲点 #22)
特性：
  - alert_dismissal_rate > 30% → 过度疲劳
  - SEV-2 自动响应规则（Owner 不在时自动降级）
"""

import time


class OwnerHealthMonitor:
    """
    Owner 健康监测 (盲点 #22)
    """

    ALERT_DISMISSAL_CRITICAL = 0.30
    RESPONSE_DELAY_CRITICAL = 1800

    def __init__(self):
        self._dismissals = 0
        self._total_alerts = 0
        self._last_active: float = time.time()

    def record_dismissal(self):
        self._dismissals += 1

    def record_alert(self):
        self._total_alerts += 1

    def check(self) -> dict:
        dismissal_rate = self._dismissals / max(self._total_alerts, 1)
        idle_time = time.time() - self._last_active

        state = "HEALTHY"
        if dismissal_rate > self.ALERT_DISMISSAL_CRITICAL:
            state = "CRITICALLY_LOW"
        elif idle_time > self.RESPONSE_DELAY_CRITICAL:
            state = "COMPLACENT"

        return {
            "dismissal_rate": round(dismissal_rate, 2),
            "idle_seconds": int(idle_time),
            "state": state,
            "auto_response_enabled": state != "HEALTHY",
        }

    def touch(self):
        self._last_active = time.time()
