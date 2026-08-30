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
# [A_module] module_id=MOD-INF-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: escalation_bridge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① EscalationBridge
#   name_en: EscalationBridge
#   intro: class EscalationBridge 源码 L59-L126
#   desc: 公共方法（定义序）: escalate, escalate_dead_letter, get_escalation_history, enabled；源码 L59-L126
#   inputs: config
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: EscalationBridge
#   downstream: engine.py;fix_reliability.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("Escalation failed: %s", exc, exc_info=True)
            action.metadata["escalation_error"] = str(exc)
            return action

    def escalate_dead_letter(self, action: FixAction, failure_reason: str) -> FixAction:
        if not self._auto_escalate:
            return action
        return self.escalate(action, f"Dead letter: {failure_reason}")

    def get_escalation_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._escalation_history[-limit:]

    @property
    def enabled(self) -> bool:  # noqa: m03-duplicate  M03豁免: 平凡一行属性getter(return self._enabled)，AI趋同演化非复制粘贴
        return self._enabled
