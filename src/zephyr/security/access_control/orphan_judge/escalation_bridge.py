# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §6.2
# [MODULE] zephyr.security.access_control.orphan_judge.escalation_bridge
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] orphan-judge.judge.OrphanJudge(ESCALATE判决)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 不实现升级逻辑; 仅桥接EscalationEngine.evaluate()+escalate()
# [MODIFY-GUARD] EscalationEngine API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回 {"status": "bridge_unavailable"}
# [TESTS] tests/orphan-judge/test_escalation_bridge.py
# [A_module] module_id=MOD-SEC_escalation_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["EscalationBridge"]


class EscalationBridge:
    def __init__(self) -> None:
        self._engine = None
        self._available = False
        try:
            from zephyr.governance.escalation.escalation_engine import EscalationEngine

            self._engine = EscalationEngine(name="orphan-judge", hooks_enabled=True)
            self._available = True
        except ImportError:
            logger.warning("EscalationEngine not available")
        except Exception as exc:
            logger.warning("EscalationEngine init failed: %s", exc)

    def escalate_judgment(self, file_path: str, verdict: str, reason: str) -> dict[str, Any]:
        if not self._available or self._engine is None:
            return {"status": "bridge_unavailable", "file": file_path}
        try:
            event = self._engine.escalate(
                category="CUSTOM",
                description=f"OrphanJudge ESCALATE: {file_path} — {reason}",
                source="orphan-judge",
                metadata={"file": file_path, "verdict": verdict},
            )
            return {"status": "escalated", "event_id": getattr(event, "id", "unknown")}
        except Exception as exc:
            logger.error("EscalationBridge.escalate_judgment failed: %s", exc)
            return {"status": "bridge_error", "error": str(exc)}

    def evaluate_risk(self, file_path: str, reason: str) -> dict[str, Any]:
        if not self._available or self._engine is None:
            return {"status": "bridge_unavailable", "file": file_path}
        try:
            result = self._engine.evaluate(
                category="CUSTOM",
                description=f"OrphanJudge risk evaluation: {file_path}",
                source="orphan-judge",
            )
            return {"status": "evaluated", "result": str(result) if result else "no_result"}
        except Exception as exc:
            logger.error("EscalationBridge.evaluate_risk failed: %s", exc)
            return {"status": "bridge_error", "error": str(exc)}

    def is_available(self) -> bool:
        return self._available
