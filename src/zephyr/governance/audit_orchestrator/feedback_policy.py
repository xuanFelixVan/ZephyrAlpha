# [A_module] module_id=MOD-GOV_feedback_policy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md | §5.1
# [MODULE] zephyr.governance.audit_trail.feedback_policy
# [INVARIANTS] 反馈策略自动从审计发现中提取规则进化建议
# [MODIFY-GUARD] FeedbackBridge API变更时同步此策略
# [CONSUMERS] audit-orchestrator.integrity(完整性校验后触发策略评估)
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 策略评估失败返回保守策略
# [TESTS] tests/audit-orchestrator/test_feedback_policy.py

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["FeedbackPolicy", "PolicyDecision"]

class PolicyDecision:
    def __init__(
        self,
        action: str,
        confidence: float = 0.0,
        detail: str = "",
    ) -> None:
        self.action = action
        self.confidence = confidence
        self.detail = detail

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "confidence": self.confidence,
            "detail": self.detail,
        }

class FeedbackPolicy:
    SEVERITY_WEIGHTS: dict[str, float] = {
        "RED": 1.0,
        "YELLOW": 0.5,
        "GREEN": 0.0,
    }

    AUTO_APPLY_THRESHOLD: float = 0.7

    def __init__(self) -> None:
        self._bridge = None
        self._available = False
        try:
            from zephyr.governance.audit_trail.feedback_bridge import FeedbackBridge
            self._bridge = FeedbackBridge()
            self._available = self._bridge.is_available()
        except ImportError:
            logger.warning("FeedbackBridge not available")
        except Exception as exc:
            logger.warning("FeedbackBridge init failed: %s", exc)

    def evaluate(self, findings: list[dict[str, Any]]) -> PolicyDecision:
        if not findings:
            return PolicyDecision(action="skip", detail="No findings to evaluate")

        red_count = sum(1 for f in findings if f.get("severity") == "RED")
        yellow_count = sum(1 for f in findings if f.get("severity") == "YELLOW")
        total_count = len(findings)

        weighted_score = sum(
            self.SEVERITY_WEIGHTS.get(f.get("severity", "GREEN"), 0.0)
            for f in findings
        ) / max(1, total_count)

        if not self._available or self._bridge is None:
            if weighted_score > 0.5:
                return PolicyDecision(
                    action="alert",
                    confidence=weighted_score,
                    detail=f"FeedbackBridge unavailable: {red_count} RED, {yellow_count} YELLOW, {total_count} total",
                )
            return PolicyDecision(action="skip", detail="FeedbackBridge unavailable, low severity")

        proposals = self._bridge.analyze_audit_findings(findings)

        if not proposals:
            return PolicyDecision(
                action="log",
                confidence=weighted_score,
                detail=f"No proposals generated: {red_count} RED, {yellow_count} YELLOW",
            )

        high_conf = [p for p in proposals if p.get("confidence", 0) >= self.AUTO_APPLY_THRESHOLD]
        if high_conf:
            return PolicyDecision(
                action="auto_apply",
                confidence=max(p.get("confidence", 0) for p in high_conf),
                detail=f"Auto-applying {len(high_conf)}/{len(proposals)} proposals (threshold={self.AUTO_APPLY_THRESHOLD})",
            )

        return PolicyDecision(
            action="suggest",
            confidence=max(p.get("confidence", 0) for p in proposals),
            detail=f"Suggesting {len(proposals)} proposals for review",
        )

    def apply_high_confidence(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        decision = self.evaluate(findings)
        if decision.action != "auto_apply":
            return []

        applied: list[dict[str, Any]] = []
        if self._bridge:
            proposals = self._bridge.analyze_audit_findings(findings)
            for p in proposals:
                if p.get("confidence", 0) >= self.AUTO_APPLY_THRESHOLD:
                    success = self._bridge.apply(p)
                    p["applied"] = success
                    applied.append(p)
        return applied

    def is_available(self) -> bool:
        return self._available