# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.1
# [MODULE] zephyr.governance.audit_trail.feedback_policy
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.feedback_bridge
# [CONSUMERS] audit-orchestrator.integrity(完整性校验后触发策略评估)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 反馈策略自动从审计发现中提取规则进化建议
# [MODIFY-GUARD] FeedbackBridge API变更时同步此策略
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 策略评估失败返回保守策略
# [TESTS] tests/audit-orchestrator/test_feedback_policy.py
# [A_module] module_id=MOD-GOV_feedback_policy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
            logger.warning("FeedbackBridge init failed: %s", exc, exc_info=True)

    def evaluate(self, findings: list[dict[str, Any]]) -> PolicyDecision:
        if not findings:
            return PolicyDecision(action="skip", detail="No findings to evaluate")

        red_count = sum(1 for f in findings if f.get("severity") == "RED")
        yellow_count = sum(1 for f in findings if f.get("severity") == "YELLOW")
        total_count = len(findings)

        weighted_score = sum(self.SEVERITY_WEIGHTS.get(f.get("severity", "GREEN"), 0.0) for f in findings) / max(
            1, total_count
        )

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


class AnomalyPattern:
    def __init__(self, pattern_id="", name="", description="", threshold=0.0, enabled=True):
        self.pattern_id = pattern_id
        self.name = name
        self.description = description
        self.threshold = threshold
        self.enabled = enabled


class FeedbackSummary:
    def __init__(self, total_feedback=0, by_channel=None, by_severity=None, period=""):
        self.total_feedback = total_feedback
        self.by_channel = by_channel or {}
        self.by_severity = by_severity or {}
        self.period = period


class PolicyAction:
    def __init__(self, action="", target="", reason="", priority="medium"):
        self.action = action
        self.target = target
        self.reason = reason
        self.priority = priority


class PolicyFeedbackBridge:
    def __init__(self, config=None):
        self.config = config or {}

    def apply_policy(self, feedback):
        return PolicyAction()

    def get_policy(self, policy_id):
        return None


class PolicyRecommendation:
    def __init__(self, policy_id: str = "", action: str = "", target: str = "", reason: str = "", confidence: float = 0.0) -> None:
        self.policy_id = policy_id
        self.action = action
        self.target = target
        self.reason = reason
        self.confidence = confidence


def feedback_to_policy(feedback: dict[str, Any], policies: list[str] | None = None) -> PolicyRecommendation:
    return PolicyRecommendation()