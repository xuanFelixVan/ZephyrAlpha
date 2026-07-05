# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.governance.audit_trail.bridges.audit_trust_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [A_module] module_id=MOD-GOV_trust_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Audit ↔ ContinuousTrust 信任分数桥接.

蓝图 §2.3 D-020-17 — 渐进信任分数(0.0~1.0) + 时间衰减。
集成 rollback/continuous_trust.py 的 TrustScore 到审计条目。
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

_logger = logging.getLogger(__name__)


class AuditTrustBridge:
    """审计↔信任分数桥接器.

    从 ContinuousTrust 引擎读取 Agent 信任分数，
    注入审计条目的 trust-score 字段，
    并在信任分数剧烈变化时触发 TRUST_SCORE_CHANGE 异常。
    """

    _TRUST_SCORE_CHANGE_THRESHOLD = 0.3

    def get_trust_score(self, agent_id: str) -> float | None:
        """查询 Agent 当前信任分数.

        Args:
            agent_id: Agent 标识

        Returns:
            信任分数 (0.0~1.0)，或 None 如果引擎不可用
        """
        try:
            from zephyr.governance.intelligence_governance.continuous_trust import ContinuousTrust

            engine = ContinuousTrust()
            score_obj = engine.get_score()
            return score_obj.score if hasattr(score_obj, "score") else None
        except ImportError:
            _logger.debug("ContinuousTrust not available for agent %s", agent_id)
            return None
        except Exception:
            _logger.exception("Failed to get trust score for agent %s", agent_id)
            return None

    def enrich_event_with_trust(self, event: dict[str, Any]) -> dict[str, Any]:
        """为审计事件注入信任分数.

        Args:
            event: 审计事件字典

        Returns:
            注入 trust-score 字段的事件字典
        """
        agent_id = event.get("agent_id", "")
        if not agent_id:
            return event

        trust_score = self.get_trust_score(agent_id)
        if trust_score is not None:
            event["trust-score"] = round(trust_score, 4)
            event["trust_tier"] = self._classify_tier(trust_score)

        return event

    def detect_trust_score_change(
        self,
        agent_id: str,
        previous_score: float | None = None,
    ) -> dict[str, Any] | None:
        """检测信任分数剧烈变化.

        Args:
            agent_id: Agent 标识
            previous_score: 上一次记录的信任分数

        Returns:
            异常事件字典，或 None 如果无异常
        """
        current = self.get_trust_score(agent_id)
        if current is None or previous_score is None:
            return None

        delta = abs(current - previous_score)
        if delta >= self._TRUST_SCORE_CHANGE_THRESHOLD:
            return {
                "signature_id": "TRUST_SCORE_CHANGE",
                "severity": "CRITICAL" if delta >= 0.5 else "HIGH",
                "agent_id": agent_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": {
                    "previous_score": previous_score,
                    "current_score": current,
                    "delta": round(delta, 4),
                    "direction": "drop" if current < previous_score else "rise",
                },
            }

        return None

    def batch_enrich(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """批量注入信任分数.

        Args:
            events: 审计事件列表

        Returns:
            注入信任分数后的事件列表
        """
        return [self.enrich_event_with_trust(e) for e in events]

    @staticmethod
    def _classify_tier(score: float) -> str:
        if score >= 0.8:
            return "TIER_2_AUTO_REVERT"
        if score >= 0.5:
            return "TIER_1_PROPOSE_ONLY"
        return "TIER_0_READ_ONLY"
