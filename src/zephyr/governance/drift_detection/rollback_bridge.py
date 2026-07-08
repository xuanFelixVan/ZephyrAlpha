# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.rollback_bridge
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py; tests/rollback/test_rollback_bridge.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 漂移->回滚桥接不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] BridgeError;RollbackTriggerFailed
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_rollback_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-006 契约：Drift -> Rollback 漂移触发回滚."""

from __future__ import annotations


class DriftRollbackBridge:
    """行为漂移->回滚触发."""

    def on_drift_detected(self, agent_id: str, drift_type: str, severity: str) -> dict:
        return {
            "triggered": severity in {"HIGH", "CRITICAL"},
            "agent_id": agent_id,
            "drift_type": drift_type,
            "action": "ROLLBACK" if severity in {"HIGH", "CRITICAL"} else "OBSERVE",
        }
