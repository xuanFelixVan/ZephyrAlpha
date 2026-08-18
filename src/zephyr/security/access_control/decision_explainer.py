# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.decision_explainer
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.agent_rbac.test_decision_explainer_agent_rbac
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Explanation.to_dict returns all 5 fields; structured_rejection auto-generates correction_suggestion when empty
# [MODIFY-GUARD] blueprint.md §
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/decision/test_decision_explainer_root.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DecisionExplainer — 拒绝决策的结构化解释器.

依据蓝图 MOD-INF-018:
- Explanation: 拒绝原因的结构化载体（blocked_layer/rule_id/reason/correction_suggestion/causal_chain）
- DecisionExplainer: 生成结构化拒绝解释，包含自动建议生成
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Explanation:
    """拒绝解释 — 结构化载体.

    Attributes:
        blocked_layer: 阻塞层（L0/L1/L2/L3/L5/N/A 等）
        rule_id: 触发的规则 ID
        reason: 拒绝原因
        correction_suggestion: 修正建议（空时由 DecisionExplainer 自动生成）
        causal_chain: 因果链（默认 [blocked_layer, rule_id, reason]）
    """

    blocked_layer: str = ""
    rule_id: str = ""
    reason: str = ""
    correction_suggestion: str = ""
    causal_chain: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """返回所有字段的字典表示."""
        return {
            "blocked_layer": self.blocked_layer,
            "rule_id": self.rule_id,
            "reason": self.reason,
            "correction_suggestion": self.correction_suggestion,
            "causal_chain": self.causal_chain,
        }


# 治本（2026-07-18）：层级 → 自动建议映射表。
# 每个层级有对应的修正建议模板，未知层级回退到通用建议。
_LAYER_SUGGESTIONS: dict[str, str] = {
    "L0": "No workaround for immutable L0 layer — immutability is a hard constraint.",
    "L1": "Contact the resource owner for L1 RBAC permission elevation.",
    "L2": "Retry with exponential backoff (L2 timeout).",
    "L3": "Fix schema error and retry (L3 contract validation).",
    "L4": "Review gateway policy and adjust request (L4 gateway).",
    "L5": "Sanitize PII data before retry (L5 data protection).",
}

_FALLBACK_SUGGESTION = "Contact the system owner for assistance."


class DecisionExplainer:
    """拒绝决策解释器 — 生成结构化拒绝解释."""

    def structured_rejection(
        self,
        blocked_layer: str,
        rule_id: str,
        reason: str,
        correction_suggestion: str = "",
        causal_chain: list[str] | None = None,
    ) -> Explanation:
        """生成结构化拒绝解释.

        Args:
            blocked_layer: 阻塞层
            rule_id: 规则 ID
            reason: 拒绝原因
            correction_suggestion: 修正建议（空时自动生成）
            causal_chain: 因果链（None 时默认 [blocked_layer, rule_id, reason]）

        Returns:
            Explanation 实例
        """
        if causal_chain is None:
            causal_chain = [blocked_layer, rule_id, reason]
        if not correction_suggestion:
            correction_suggestion = self._auto_suggestion(blocked_layer, reason)
        return Explanation(
            blocked_layer=blocked_layer,
            rule_id=rule_id,
            reason=reason,
            correction_suggestion=correction_suggestion,
            causal_chain=list(causal_chain),
        )

    def explain_auto_guard(self, operation: str, timeout: int) -> Explanation:
        """生成自动守卫的解释.

        Args:
            operation: 被守卫的操作
            timeout: 守卫超时（秒）

        Returns:
            Explanation 实例（blocked_layer="N/A", rule_id="AUTO_GUARD"）
        """
        return Explanation(
            blocked_layer="N/A",
            rule_id="AUTO_GUARD",
            reason=f"auto-guard for {operation} (timeout={timeout}s)",
            correction_suggestion=(
                f"Wait {timeout}s for auto-guard to release, or contact owner for manual override."
            ),
            causal_chain=["L1 RBAC", "AUTO_GUARD", operation],
        )

    @staticmethod
    def _auto_suggestion(blocked_layer: str, reason: str) -> str:
        """根据阻塞层自动生成修正建议."""
        suggestion = _LAYER_SUGGESTIONS.get(blocked_layer.upper())
        if suggestion:
            return suggestion
        return _FALLBACK_SUGGESTION


__all__ = [
    "DecisionExplainer",
    "Explanation",
]
