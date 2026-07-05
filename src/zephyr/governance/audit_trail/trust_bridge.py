# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12
# [MODULE] zephyr.governance.audit_trail.trust_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.trust_engine
# [CONSUMERS] audit-orchestrator.bridge; integrity
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现信任逻辑; 仅桥接TrustEngine
# [MODIFY-GUARD] TrustEngine API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回UNKNOWN信任级别
# [TESTS] tests/audit-orchestrator/test_trust_bridge.py
# [A_module] module_id=MOD-GOV_trust_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["TrustBridge"]


class TrustBridge:
    def __init__(self) -> None:
        self._engine = None
        self._available = False
        try:
            from zephyr.governance.audit_trail.trust_engine import TrustEngine

            self._engine = TrustEngine()
            self._available = True
        except ImportError:
            logger.warning("TrustEngine not available")
        except Exception as exc:
            logger.warning("TrustEngine init failed: %s", exc, exc_info=True)

    def evaluate(self, audit_results: list[dict[str, Any]]) -> dict[str, Any]:
        if not self._available or self._engine is None:
            return {"trust_level": "UNKNOWN", "score": 0.0, "confidence": 0.0}
        try:
            return self._engine.calculate(audit_results)
        except Exception as exc:
            logger.error("TrustBridge.evaluate failed: %s", exc, exc_info=True)
            return {"trust_level": "UNKNOWN", "score": 0.0, "confidence": 0.0}

    def record(self, result: dict[str, Any]) -> bool:
        if not self._available or self._engine is None:
            return False
        try:
            self._engine.update_history(result)
            return True
        except Exception as exc:
            logger.error("TrustBridge.record failed: %s", exc, exc_info=True)
            return False

    def get_trend(self) -> dict[str, Any]:
        if not self._available or self._engine is None:
            return {"direction": "stable", "change": 0.0}
        try:
            return self._engine.trend()
        except Exception as exc:
            logger.error("TrustBridge.get_trend failed: %s", exc, exc_info=True)
            return {"direction": "stable", "change": 0.0}

    def is_available(self) -> bool:
        return self._available