# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.last_resort_watchdog
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] (none — stdlib only)
# [CONSUMERS] zephyr.governance.escalation.escalation_engine(写方：L4 且重试耗尽时 activate 点亮旗标);
#   zephyr.governance.resilience_governance.emergency_track_guardian(读方：旗标作一条失效判据腿,
#   BRK-005 治本——旗标此前只写不读=静默兜底)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 终极逃生舱必须可用;ALL_STOP必须可触发;本件不自我触发（activate 只点亮旗标，
#   emergency_shutdown 须由人或显式授权链调用——裁定#254 口径,本批未改）
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/governance/resilience/test_last_resort_watchdog.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Last Resort Watchdog — v0.8.0 终极逃生舱: 所有escalation失败后的final fallback+shutdown。

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/resilience_governance/last_resort_watchdog.yaml
"""

from __future__ import annotations


class LastResortWatchdog:
    def __init__(self):
        self._activated = False

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def activated(self):
        """只读：activated（Stage 4 公共化）。"""
        return self._activated

    @activated.setter
    def activated(self, value):
        """写入：activated（Stage 4 公共化）。"""
        self._activated = value

    def activate(self) -> None:
        self._activated = True

    @property
    def active(self) -> bool:
        return self._activated

    def emergency_shutdown(self) -> dict:
        self._activated = True
        return {"action": "EMERGENCY_SHUTDOWN", "reason": "last_resort_activated", "safe_mode": True}


_last_resort_instance: LastResortWatchdog | None = None


def get_last_resort_watchdog() -> LastResortWatchdog:
    """获取终极逃生舱单例（A4 接线，裁定#254：activate 仅点亮旗标，
    emergency_shutdown 不得由升级协议自动调用）。"""
    global _last_resort_instance
    if _last_resort_instance is None:
        _last_resort_instance = LastResortWatchdog()
    return _last_resort_instance
