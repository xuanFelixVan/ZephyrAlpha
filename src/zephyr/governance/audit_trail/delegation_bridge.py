# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12
# [MODULE] zephyr.governance.audit_trail.delegation_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] audit-orchestrator.delegation_auditor(委托审计时上报)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现委托逻辑; 仅桥接EscalationEngine.evaluate()/escalate()
# [MODIFY-GUARD] EscalationEngine API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回空事件列表
# [TESTS] tests/audit-orchestrator/test_delegation_bridge.py
# [A_module] module_id=MOD-GOV_delegation_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["DelegationBridge"]


class DelegationBridge:
    def __init__(self) -> None:
        self._engine = None
        self._available = False
        try:
            from zephyr.governance.escalation.escalation_engine import EscalationEngine

            self._engine = EscalationEngine(name="audit-orchestrator", hooks_enabled=False)
            self._available = True
        except ImportError:
            logger.warning("EscalationEngine not available")
        except Exception as exc:
            logger.warning("EscalationEngine init failed: %s", exc, exc_info=True)

    def report_delegation_failure(self, target: str, reason: str) -> dict[str, Any] | None:
        if not self._available or self._engine is None:
            return None
        try:
            from zephyr.governance.escalation.escalation_engine import RuleCategory

            event = self._engine.evaluate(
                category=RuleCategory.CASCADE_FAILURE,
                description=f"Delegation to {target} failed: {reason}",
            )
            return {
                "event_id": event.event_id,
                "state": event.state.value if hasattr(event.state, "value") else str(event.state),
                "description": event.description,
            }
        except Exception as exc:
            logger.error("DelegationBridge.report_delegation_failure failed: %s", exc, exc_info=True)
            return None

    def report_delegation_timeout(self, target: str) -> dict[str, Any] | None:
        if not self._available or self._engine is None:
            return None
        try:
            from zephyr.governance.escalation.escalation_engine import RuleCategory

            event = self._engine.evaluate(
                category=RuleCategory.TIMEOUT,
                description=f"Delegation to {target} timed out",
            )
            return {
                "event_id": event.event_id,
                "state": event.state.value if hasattr(event.state, "value") else str(event.state),
                "description": event.description,
            }
        except Exception as exc:
            logger.error("DelegationBridge.report_delegation_timeout failed: %s", exc, exc_info=True)
            return None

    def is_available(self) -> bool:
        return self._available