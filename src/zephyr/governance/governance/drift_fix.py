# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.governance.drift_fix
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.drift_detection.events
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
# [A_module] module_id=MOD-GOV_drift_fix | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""G-CT-005 消费端 — Rollback.on_drift_fix() 消费漂移事件执行自动修复.

SRC-0038: 副本文件 — 保持独立实现，待后续审核。
  此文件是 drift-detector 真源的**rollback 消费者**，
  包含专属的 DriftFixHandler.on_drift_fix() 回滚兜底逻辑，不可简化为纯 shim。
  已从 governance.drift_detector.events 导入 DriftEvent（此模块本身也需后续合并审核）。
"""

from __future__ import annotations

from typing import Any

from zephyr.governance.drift_detection.events import DriftEvent


class DriftFixHandler:
    """漂移自动修复处理器 — G-CT-005 消费端."""

    def on_drift_fix(self, event: DriftEvent) -> dict[str, Any]:
        if not event.auto_fixable:
            event.mark_manual_required()
            return {
                "drift_id": event.drift_id,
                "fixed": False,
                "action": "MANUAL_REQUIRED",
                "reason": "auto_fixable=False",
                "drift_type": event.drift_type.value,
            }

        event.mark_fixed()
        return {
            "drift_id": event.drift_id,
            "fixed": True,
            "action": "AUTO_FIXED",
            "target": event.target,
            "fix_suggestion": event.fix_suggestion,
            "drift_type": event.drift_type.value,
        }
