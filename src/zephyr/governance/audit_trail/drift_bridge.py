# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12
# [MODULE] zephyr.governance.audit_trail.drift_bridge
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] audit-orchestrator.self_monitor(自监控漂移检测)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现漂移检测逻辑; 仅桥接DriftDetector.establish_baseline()+detect()+is_drifting()
# [MODIFY-GUARD] DriftDetector API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回无漂移(false)
# [TESTS] tests/audit-orchestrator/test_drift_bridge.py
# [A_module] module_id=MOD-GOV_drift_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["DriftBridge"]


class DriftBridge:
    def __init__(self) -> None:
        self._detector = None
        self._available = False
        try:
            from zephyr.governance.drift_detection.drift_detector import DriftDetector

            self._detector = DriftDetector()
            self._available = True
        except ImportError:
            logger.warning("DriftDetector not available")
        except Exception as exc:
            logger.warning("DriftDetector init failed: %s", exc, exc_info=True)

    def establish_baseline(self, metrics: dict[str, float]) -> bool:
        if not self._available or self._detector is None:
            return False
        try:
            self._detector.establish_baseline(metrics)
            return True
        except Exception as exc:
            logger.error("DriftBridge.establish_baseline failed: %s", exc, exc_info=True)
            return False

    def check_drift(self, current: dict[str, float], threshold: float = 0.3) -> dict[str, Any]:
        if not self._available or self._detector is None:
            return {"is_drifting": False, "drift_score": 0.0, "available": False}
        try:
            score = self._detector.detect(current)
            return {
                "is_drifting": self._detector.is_drifting(current, threshold),
                "drift_score": round(score, 4),
                "available": True,
            }
        except Exception as exc:
            logger.error("DriftBridge.check_drift failed: %s", exc, exc_info=True)
            return {"is_drifting": False, "drift_score": 0.0, "available": False}

    def is_available(self) -> bool:
        return self._available


class BridgeResult:
    def __init__(self, success=True, message="", data=None):
        self.success = success
        self.message = message
        self.data = data or {}