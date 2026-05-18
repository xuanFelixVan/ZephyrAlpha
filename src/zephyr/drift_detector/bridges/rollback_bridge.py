# [BLUEPRINT] MOD-INF-023 | 03_modules/l01_infrastructure/drift-detector/blueprint.md | §

# [MODULE] zephyr.drift_detector.bridges.rollback_bridge

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-006 契约：Drift → Rollback 漂移触发回滚."""

from __future__ import annotations


class DriftRollbackBridge:
    """行为漂移→回滚触发."""

    def on_drift_detected(
        self, agent_id: str, drift_type: str, severity: str
    ) -> dict:
        return {
            "triggered": severity in {"HIGH", "CRITICAL"},
            "agent_id": agent_id,
            "drift_type": drift_type,
            "action": "ROLLBACK" if severity in {"HIGH", "CRITICAL"} else "OBSERVE",
        }
