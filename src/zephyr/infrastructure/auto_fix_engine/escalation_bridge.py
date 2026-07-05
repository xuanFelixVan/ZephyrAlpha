# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.escalation_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.governance.__init__
# [CONSUMERS] engine.py;fix_reliability.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] MUST桥接MOD-INF-022 EscalationProtocol;升级失败MUST记录
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml escalation段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EscalationBridgeError
# [TESTS] tests/auto-fix-engine/test_escalation_bridge.py
# [A_module] module_id=MOD-INF_escalation_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import FixAction, FixStatus

logger = logging.getLogger(__name__)


class EscalationBridge:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}
        self._enabled: bool = config.get("bridge_enabled", True)
        self._auto_escalate: bool = config.get("auto_escalate_dead_letter", True)
        self._max_level: str = config.get("max_escalation_level", "L2_HUMAN_REVIEW")
        self._escalation_history: list[dict[str, Any]] = []

    def escalate(self, action: FixAction, reason: str = "") -> FixAction:
        if not self._enabled:
            action.metadata["escalation_skipped"] = True
            action.metadata["skip_reason"] = "Escalation bridge disabled"
            return action
        try:
            from zephyr.governance.services.adapter import escalate_if_needed

            result = escalate_if_needed(
                operation_type=action.action_type,
                description=f"Auto-fix escalation: {reason or action.metadata.get('error', 'unknown')}",
                owner_id="auto-fix-engine",
            )
            action.escalated = True
            action.status = FixStatus.APPROVAL_PENDING
            action.metadata["escalation_result"] = {
                "should_block": result.should_block,
                "should_escalate": result.should_escalate,
                "reason": result.reason,
            }
            self._escalation_history.append(
                {
                    "action_id": action.action_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "reason": reason,
                    "result": {"should_block": result.should_block},
                }
            )
            return action
        except ImportError:
            logger.warning("Escalation engine not available, using fallback")
            action.escalated = True
            action.status = FixStatus.APPROVAL_PENDING
            action.metadata["escalation_fallback"] = True
            action.metadata["escalation_reason"] = reason
            self._escalation_history.append(
                {
                    "action_id": action.action_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "reason": reason,
                    "result": {"fallback": True},
                }
            )
            return action
        except Exception as exc:
            logger.error("Escalation failed: %s", exc)
            action.metadata["escalation_error"] = str(exc)
            return action

    def escalate_dead_letter(self, action: FixAction, failure_reason: str) -> FixAction:
        if not self._auto_escalate:
            return action
        return self.escalate(action, f"Dead letter: {failure_reason}")

    def get_escalation_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._escalation_history[-limit:]

    @property
    def enabled(self) -> bool:
        return self._enabled
