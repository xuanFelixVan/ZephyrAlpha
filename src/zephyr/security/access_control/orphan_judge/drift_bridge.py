# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §6.1
# [MODULE] zephyr.security.access_control.orphan_judge.drift_bridge
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] orphan-judge.judge.OrphanJudge(starve/stale判定)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 不实现漂移检测; 仅桥接DriftDetector.trigger_recovery()
# [MODIFY-GUARD] DriftDetector API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回 {"status": "bridge_unavailable"}
# [TESTS] tests/orphan-judge/test_drift_bridge.py
# [A_module] module_id=MOD-SEC_drift_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["DriftBridge"]


class DriftBridge:
    def __init__(self) -> None:
        self._available = False
        try:
            from zephyr.gov_enforcement.rule_enforcement.drift_detector import trigger_recovery

            self._trigger = trigger_recovery
            self._available = True
        except ImportError:
            logger.warning("DriftDetector not available")
            self._trigger = None

    def notify_change(self, module_id: str, changed_files: list[str], message: str = "") -> dict[str, Any]:
        if not self._available or self._trigger is None:
            return {"status": "bridge_unavailable", "module_id": module_id}
        try:
            return self._trigger(
                {
                    "module_id": module_id,
                    "changed_files": changed_files,
                    "commit_message": message,
                    "scan_level": "STANDARD",
                }
            )
        except Exception as exc:
            logger.error("DriftBridge.notify_change failed: %s", exc, exc_info=True)
            return {"status": "bridge_error", "error": str(exc)}

    def is_available(self) -> bool:
        return self._available