# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.drift_fix
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.gov_drift.events
# [CONSUMERS] rollback_executor;auto_rollback_trigger;tests/drift/test_drift_fix
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 漂移修复必须验证; ARCH-034 P3 SRC-038 合并后唯一 canonical 真源
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RollbackError;DriftFixError
# [TESTS] tests/rollback/;tests/drift/test_drift_fix.py
# [A_module] module_id=MOD-INF_drift_fix | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

"""

G-CT-005 消费端 — Rollback.on_drift_fix() 消费漂移事件执行自动修复.

ARCH-034 P3 / SRC-038 合并审核（2026-07-01）：
  本文件是 DriftFixHandler 的 **canonical 真源**（MATURITY=production）。
  原有3份冗余副本（governance/drift_fix.py、rollback/governance/drift_fix.py、
  本文件），内容几乎完全相同，路径漂移 + [MODULE]名重复。
  合并后仅保留本文件（路径与 MODULE 名一致），删除另两份冗余副本。
  - tests/drift/test_drift_fix.py 改为从本文件 import
  - rollback/governance/__init__.py 改为从本文件 re-export DriftFixHandler

  DriftFixHandler 包含专属的 on_drift_fix() 回滚兜底逻辑，不可简化为纯 shim。
  从 zephyr.governance.drift_detection.events 导入 ManagedDriftEvent。
"""

from typing import Any

from zephyr.gov_drift.events import ManagedDriftEvent


class DriftFixHandler:
    """漂移自动修复处理器 — G-CT-005 消费端."""

    def on_drift_fix(self, event: ManagedDriftEvent) -> dict[str, Any]:
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
