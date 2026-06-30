# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.rollback_bridge
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] drift_engine;detector_dispatcher;alert_router
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 漂移→回滚桥接不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] BridgeError;RollbackTriggerFailed
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_rollback_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
G-CT-006 契约：Drift → Rollback 漂移触发回滚."""

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
