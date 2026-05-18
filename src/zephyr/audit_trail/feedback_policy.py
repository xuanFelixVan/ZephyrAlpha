# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.feedback_policy

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.feedback_policy — MOD-INF-020 · 三角闭环反馈
==========================================================
蓝图 D-020-08 · 异常模式聚合 + 策略推荐 + 反馈桥接

三角闭环
--------
  审计(Audit) → 反馈(Feedback) → 策略(Policy) → 审计(Audit)
  1. 审计系统检测异常模式
  2. 反馈桥接聚合异常，生成策略推荐
  3. 策略变更反馈到审计系统，强化检测
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_logger = logging.getLogger(__name__)


class PolicyAction(str, Enum):
    ALERT = "alert"
    THROTTLE = "throttle"
    BLOCK = "block"
    ESCALATE = "escalate"
    ADJUST_TRUST = "adjust_trust"
    UPDATE_RULE = "update_rule"


class AnomalyPattern(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pattern_id: str = ""
    anomaly_type: str = ""
    frequency: int = 0
    severity: str = "medium"
    affected_agents: list[str] = Field(default_factory=list)
    first_seen: str = ""
    last_seen: str = ""


class PolicyRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendation_id: str = ""
    pattern: AnomalyPattern | None = None
    action: PolicyAction = PolicyAction.ALERT
    rationale: str = ""
    confidence: float = 0.0
    parameters: dict[str, Any] = Field(default_factory=dict)
    created_at: str = ""


class FeedbackSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_patterns: int = 0
    total_recommendations: int = 0
    high_severity_count: int = 0
    patterns: list[AnomalyPattern] = Field(default_factory=list)
    recommendations: list[PolicyRecommendation] = Field(default_factory=list)
    summarized_at: str = ""


class PolicyFeedbackBridge:
    def __init__(self) -> None:
        self._patterns: dict[str, AnomalyPattern] = {}
        self._recommendations: list[PolicyRecommendation] = []

    def aggregate_patterns(self, anomaly_results: list[dict[str, Any]]) -> list[AnomalyPattern]:
        for result in anomaly_results:
            anomaly_type = result.get("signature", result.get("anomaly_type", "unknown"))
            severity = result.get("severity", "medium")
            agent_id = result.get("agent_id", result.get("evidence", {}).get("agent_id", ""))

            key = anomaly_type
            if key in self._patterns:
                pattern = self._patterns[key]
                pattern.frequency += 1
                pattern.last_seen = datetime.now(UTC).isoformat()
                if agent_id and agent_id not in pattern.affected_agents:
                    pattern.affected_agents.append(agent_id)
                if severity in ("critical", "high"):
                    pattern.severity = severity
            else:
                self._patterns[key] = AnomalyPattern(
                    pattern_id=f"PAT-{anomaly_type}-{len(self._patterns):04d}",
                    anomaly_type=anomaly_type,
                    frequency=1,
                    severity=severity,
                    affected_agents=[agent_id] if agent_id else [],
                    first_seen=datetime.now(UTC).isoformat(),
                    last_seen=datetime.now(UTC).isoformat(),
                )

        return list(self._patterns.values())

    def generate_recommendations(self) -> list[PolicyRecommendation]:
        self._recommendations.clear()

        for pattern in self._patterns.values():
            action, params, confidence = self._derive_action(pattern)
            rec = PolicyRecommendation(
                recommendation_id=f"REC-{pattern.pattern_id}-{len(self._recommendations):04d}",
                pattern=pattern,
                action=action,
                rationale=self._build_rationale(pattern, action),
                confidence=confidence,
                parameters=params,
                created_at=datetime.now(UTC).isoformat(),
            )
            self._recommendations.append(rec)

        return self._recommendations

    def get_summary(self) -> FeedbackSummary:
        high_severity = sum(1 for p in self._patterns.values() if p.severity in ("critical", "high"))
        return FeedbackSummary(
            total_patterns=len(self._patterns),
            total_recommendations=len(self._recommendations),
            high_severity_count=high_severity,
            patterns=list(self._patterns.values()),
            recommendations=list(self._recommendations),
            summarized_at=datetime.now(UTC).isoformat(),
        )

    def _derive_action(self, pattern: AnomalyPattern) -> tuple[PolicyAction, dict[str, Any], float]:
        confidence = min(1.0, pattern.frequency * 0.1 + 0.3)
        params: dict[str, Any] = {}

        if pattern.severity == "critical" and pattern.frequency >= 3:
            return PolicyAction.BLOCK, {"block_agents": pattern.affected_agents}, confidence
        elif pattern.severity == "critical":
            return PolicyAction.ESCALATE, {"escalate_to": "owner"}, confidence
        elif pattern.severity == "high" and pattern.frequency >= 5:
            return PolicyAction.THROTTLE, {"rate_limit": 10, "window_seconds": 60}, confidence
        elif pattern.severity == "high":
            return PolicyAction.ADJUST_TRUST, {"delta": -0.1, "agents": pattern.affected_agents}, confidence
        elif pattern.frequency >= 10:
            return PolicyAction.UPDATE_RULE, {"rule_type": pattern.anomaly_type}, confidence
        else:
            return PolicyAction.ALERT, {"message": f"Recurring {pattern.anomaly_type} detected"}, confidence

    @staticmethod
    def _build_rationale(pattern: AnomalyPattern, action: PolicyAction) -> str:
        return (
            f"Anomaly '{pattern.anomaly_type}' observed {pattern.frequency} time(s) "
            f"with severity '{pattern.severity}' affecting {len(pattern.affected_agents)} agent(s). "
            f"Recommended action: {action.value}."
        )


def feedback_to_policy(anomaly_results: list[dict[str, Any]]) -> list[PolicyRecommendation]:
    bridge = PolicyFeedbackBridge()
    bridge.aggregate_patterns(anomaly_results)
    return bridge.generate_recommendations()
