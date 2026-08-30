# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.1
# [MODULE] zephyr.gov_audit.feedback_policy
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.feedback_bridge
# [CONSUMERS] audit-orchestrator.integrity(完整性校验后触发策略评估)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 反馈策略自动从审计发现中提取规则进化建议
# [MODIFY-GUARD] FeedbackBridge API变更时同步此策略
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 策略评估失败返回保守策略
# [TESTS] tests/feedback/test_feedback_policy.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



feedback_policy.py — Audit-findings → policy recommendation bridge.

Two parallel APIs coexist in this module:
  1. `FeedbackPolicy` (legacy): audit-findings evaluator that delegates to
     `FeedbackBridge` and returns a single `PolicyDecision`.
  2. `PolicyFeedbackBridge` (newer): aggregates anomaly patterns across
     audit runs and generates `PolicyRecommendation` lists per pattern.
     `feedback_to_policy(results)` is the functional entry point that
     delegates to `PolicyFeedbackBridge`.

The two APIs serve different consumers — both are kept to avoid breaking
existing audit-orchestrator integrations.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: feedback 参数
#   fields: 参数 feedback，类型注解 list[dict[str, Any]]
#   code: feedback_policy.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: policies 参数
#   fields: 参数 policies，类型注解 list[str] | None
#   code: feedback_policy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PolicyDecision
#   name_en: PolicyDecision
#   intro: class PolicyDecision 源码 L140-L156
#   desc: 公共方法（定义序）: to_dict；源码 L140-L156
#   inputs: action confidence detail
#   outputs: 返回值
# - id: A2
#   name_zh: ② FeedbackPolicy
#   name_en: FeedbackPolicy
#   intro: class FeedbackPolicy 源码 L159-L241
#   desc: 公共方法（定义序）: evaluate, apply_high_confidence, is_available；源码 L159-L241
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ AnomalyPattern
#   name_en: AnomalyPattern
#   intro: Aggregated anomaly pattern — tracks frequency, severity, af…
#   desc: Aggregated anomaly pattern — tracks frequency, severity, affected agents.；公共方法（定义序）: upgrade_severity, add_ag…
#   inputs: anomaly_type severity frequency affected_agents
#   outputs: 返回值
# - id: A4
#   name_zh: ④ PolicyFeedbackBridge
#   name_en: PolicyFeedbackBridge
#   intro: Aggregates anomaly patterns and generates policy recommenda…
#   desc: Aggregates anomaly patterns and generates policy recommendations. Stateful bridge: `aggre…；公共方法（定义序）: pattern…
#   inputs: config
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ feedback_to_policy
#   name_en: feedback_to_policy
#   intro: Functional entry point — aggregate feedback and return reco…
#   desc: Functional entry point — aggregate feedback and return recommendations. Args: feedback: l…；源码 L453-L472
#   inputs: feedback policies
#   outputs: list[PolicyRecommendation]
#   （注：A5 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[PolicyRecommendation]
#   name_en: list[PolicyRecommendation]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: audit-orchestrator.integrity(完整性校验后触发策略评估)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

import logging
from enum import Enum, unique
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "AnomalyPattern",
    "FeedbackPolicy",
    "FeedbackSummary",
    "PolicyAction",
    "PolicyDecision",
    "PolicyFeedbackBridge",
    "PolicyRecommendation",
    "feedback_to_policy",
]


# Severity ordering — higher index = more severe. Used to upgrade pattern
# severity when the same signature is observed at multiple severities.
_SEVERITY_ORDER: dict[str, int] = {
    "info": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

# Severities counted as "high severity" in FeedbackSummary.high_severity_count.
_HIGH_SEVERITIES = frozenset({"high", "critical"})


def _severity_rank(sev: str) -> int:
    """Return integer rank for a severity string (unknown → 0)."""
    return _SEVERITY_ORDER.get(str(sev).lower(), 0)


# ---------------------------------------------------------------------------
# Legacy FeedbackPolicy / PolicyDecision (audit-orchestrator consumer)
# ---------------------------------------------------------------------------


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
            from zephyr.gov_audit.feedback_bridge import FeedbackBridge

            self._bridge = FeedbackBridge()
            self._available = self._bridge.is_available()
        except ImportError:
            logger.warning("FeedbackBridge not available")
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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


# ---------------------------------------------------------------------------
# Newer PolicyFeedbackBridge API (anomaly pattern aggregation)
# ---------------------------------------------------------------------------


@unique
class PolicyAction(str, Enum):
    """Enum of policy actions that can be recommended for an anomaly pattern."""

    ALERT = "alert"
    BLOCK = "block"
    ESCALATE = "escalate"
    THROTTLE = "throttle"


class AnomalyPattern:
    """Aggregated anomaly pattern — tracks frequency, severity, affected agents."""

    def __init__(
        self,
        anomaly_type: str = "",
        severity: str = "low",
        frequency: int = 0,
        affected_agents: list[str] | None = None,
    ) -> None:
        self.anomaly_type = anomaly_type
        self.severity = severity
        self.frequency = frequency
        self.affected_agents: list[str] = list(affected_agents) if affected_agents else []

    def upgrade_severity(self, new_severity: str) -> None:
        """Upgrade severity if `new_severity` is more severe than current."""
        if _severity_rank(new_severity) > _severity_rank(self.severity):
            self.severity = new_severity

    def add_agent(self, agent_id: str) -> None:
        """Add agent_id to affected_agents (dedup, skip empty)."""
        if agent_id and agent_id not in self.affected_agents:
            self.affected_agents.append(agent_id)


class FeedbackSummary:
    """Summary of PolicyFeedbackBridge state."""

    def __init__(
        self,
        total_patterns: int = 0,
        total_recommendations: int = 0,
        high_severity_count: int = 0,
    ) -> None:
        self.total_patterns = total_patterns
        self.total_recommendations = total_recommendations
        self.high_severity_count = high_severity_count


class PolicyRecommendation:
    """A single policy recommendation for an anomaly pattern."""

    def __init__(
        self,
        policy_id: str = "",
        action: PolicyAction | str = PolicyAction.ALERT,
        target: str = "",
        reason: str = "",
        confidence: float = 0.0,
    ) -> None:
        self.policy_id = policy_id
        self.action = action
        self.target = target
        self.reason = reason
        self.confidence = confidence


# Frequency thresholds for action escalation.
_BLOCK_FREQ_THRESHOLD = 3  # critical severity + freq >= 3 → BLOCK
_THROTTLE_FREQ_THRESHOLD = 5  # high severity + freq >= 5 → THROTTLE


class PolicyFeedbackBridge:
    """Aggregates anomaly patterns and generates policy recommendations.

    Stateful bridge: `aggregate_patterns(results)` accumulates patterns across
    calls (so multiple audit runs build up frequency). `generate_recommendations()`
    reads the accumulated state and produces one recommendation per pattern.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._patterns: dict[str, AnomalyPattern] = {}
        self._recommendations: list[PolicyRecommendation] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def patterns(self) -> dict[str, AnomalyPattern]:
        """只读：patterns（Stage 4 公共化）。"""
        return self._patterns

    @patterns.setter
    def patterns(self, value):
        """写入：patterns（Stage 4 公共化）。"""
        self._patterns = value

    @property
    def recommendations(self) -> list[PolicyRecommendation]:
        """只读：recommendations（Stage 4 公共化）。"""
        return self._recommendations

    @recommendations.setter
    def recommendations(self, value):
        """写入：recommendations（Stage 4 公共化）。"""
        self._recommendations = value

    def aggregate_patterns(self, results: list[dict[str, Any]]) -> list[AnomalyPattern]:
        """Aggregate anomaly results into patterns.

        Each result dict should have:
          - signature OR anomaly_type (string, used as pattern key)
          - severity (string: info/low/medium/high/critical)
          - agent_id (string, may be empty)

        Patterns are accumulated in `self._patterns` across calls (stateful).
        Returns the list of patterns touched by THIS call (not all patterns).
        """
        if not results:
            return []
        touched: list[AnomalyPattern] = []
        for r in results:
            anomaly_type = r.get("signature") or r.get("anomaly_type") or ""
            if not anomaly_type:
                continue
            severity = str(r.get("severity", "low")).lower()
            agent_id = str(r.get("agent_id", "") or "")
            pattern = self._patterns.get(anomaly_type)
            if pattern is None:
                pattern = AnomalyPattern(
                    anomaly_type=anomaly_type,
                    severity=severity,
                    frequency=0,
                )
                self._patterns[anomaly_type] = pattern
            pattern.frequency += 1
            pattern.upgrade_severity(severity)
            pattern.add_agent(agent_id)
            if pattern not in touched:
                touched.append(pattern)
        # Invalidate cached recommendations since patterns changed.
        self._recommendations = []
        return touched

    def generate_recommendations(self) -> list[PolicyRecommendation]:
        """Generate one PolicyRecommendation per accumulated pattern.

        Action mapping:
          - critical, freq >= 3 → BLOCK
          - critical, freq < 3  → ESCALATE
          - high,    freq >= 5 → THROTTLE
          - high,    freq < 5  → ALERT
          - medium/low/info     → ALERT
        """
        recs: list[PolicyRecommendation] = []
        for pattern in self._patterns.values():
            action = self._decide_action(pattern)
            recs.append(
                PolicyRecommendation(
                    policy_id=f"POL-{pattern.anomaly_type}",
                    action=action,
                    target=pattern.anomaly_type,
                    reason=f"severity={pattern.severity}, frequency={pattern.frequency}, agents={len(pattern.affected_agents)}",
                    confidence=_pattern_confidence(pattern),
                )
            )
        self._recommendations = recs
        return recs

    @staticmethod
    def _decide_action(pattern: AnomalyPattern) -> PolicyAction:
        sev = pattern.severity.lower()
        freq = pattern.frequency
        if sev == "critical":
            return PolicyAction.BLOCK if freq >= _BLOCK_FREQ_THRESHOLD else PolicyAction.ESCALATE
        if sev == "high":
            return PolicyAction.THROTTLE if freq >= _THROTTLE_FREQ_THRESHOLD else PolicyAction.ALERT
        return PolicyAction.ALERT

    def get_summary(self) -> FeedbackSummary:
        """Return FeedbackSummary reflecting current bridge state.

        Note: `total_recommendations` reflects the cached recommendations from
        the last `generate_recommendations()` call. If patterns changed since,
        call `generate_recommendations()` first to refresh.
        """
        total_patterns = len(self._patterns)
        high_severity_count = sum(1 for p in self._patterns.values() if p.severity.lower() in _HIGH_SEVERITIES)
        return FeedbackSummary(
            total_patterns=total_patterns,
            total_recommendations=len(self._recommendations),
            high_severity_count=high_severity_count,
        )


def _pattern_confidence(pattern: AnomalyPattern) -> float:
    """Heuristic confidence in [0.0, 1.0] based on severity and frequency."""
    sev_rank = _severity_rank(pattern.severity)
    # severity contributes up to 0.6, frequency up to 0.4 (capped at freq=10)
    sev_component = min(sev_rank / 4.0, 1.0) * 0.6
    freq_component = min(pattern.frequency / 10.0, 1.0) * 0.4
    return round(sev_component + freq_component, 3)


def feedback_to_policy(
    feedback: list[dict[str, Any]],
    policies: list[str] | None = None,
) -> list[PolicyRecommendation]:
    """Functional entry point — aggregate feedback and return recommendations.

    Args:
        feedback: list of anomaly result dicts (same shape as
            `PolicyFeedbackBridge.aggregate_patterns` input).
        policies: optional list of policy IDs to filter by (currently unused;
            reserved for future policy-filtering logic).

    Returns:
        List of PolicyRecommendation (empty if feedback is empty).
    """
    if not feedback:
        return []
    bridge = PolicyFeedbackBridge()
    bridge.aggregate_patterns(feedback)
    return bridge.generate_recommendations()
