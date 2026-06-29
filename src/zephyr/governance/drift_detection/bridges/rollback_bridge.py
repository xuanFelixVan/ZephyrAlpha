# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [MODULE] zephyr.governance.drift_detection.bridges.rollback_bridge
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.drift_detection.bridges.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_rollback_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""G-CT-006 契约：Drift → Rollback 漂移触发回滚."""

from __future__ import annotations


class DriftRollbackBridge:
    """行为漂移→回滚触发."""

    def on_drift_detected(self, agent_id: str, drift_type: str, severity: str) -> dict:
        return {
            "triggered": severity in {"HIGH", "CRITICAL"},
            "agent_id": agent_id,
            "drift_type": drift_type,
            "action": "ROLLBACK" if severity in {"HIGH", "CRITICAL"} else "OBSERVE",
        }
