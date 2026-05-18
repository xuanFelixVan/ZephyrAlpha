# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.decision_explainer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Decision Explainer — 结构化拒绝原因 + 规则溯源 + 自校正建议 + 因果链

MOD-INF-018 §2.28  D-018-26

每次拒绝都返回结构化解释：blocked_layer / rule_id / correction_suggestion / causal_chain.
"""

from dataclasses import dataclass, field


@dataclass
class Explanation:
    blocked_layer: str
    rule_id: str
    reason: str
    correction_suggestion: str
    causal_chain: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "blocked_layer": self.blocked_layer,
            "rule_id": self.rule_id,
            "reason": self.reason,
            "correction_suggestion": self.correction_suggestion,
            "causal_chain": self.causal_chain,
        }


class DecisionExplainer:
    def structured_rejection(
        self,
        blocked_layer: str,
        rule_id: str,
        reason: str,
        correction_suggestion: str = "",
        causal_chain: list[str] | None = None,
    ) -> Explanation:
        if not correction_suggestion:
            correction_suggestion = self._generate_suggestion(blocked_layer, reason)

        return Explanation(
            blocked_layer=blocked_layer,
            rule_id=rule_id,
            reason=reason,
            correction_suggestion=correction_suggestion,
            causal_chain=causal_chain or [blocked_layer, rule_id, reason],
        )

    def explain_auto_guard(self, operation: str, timeout: int) -> Explanation:
        return Explanation(
            blocked_layer="N/A",
            rule_id="AUTO_GUARD",
            reason=f"Operation '{operation}' allowed with auto_guard ({timeout}s timeout)",
            correction_suggestion=f"Owner review will be requested within {timeout}s. Manual approval can bypass auto_guard.",
            causal_chain=["L1 RBAC", "AUTO_GUARD", operation],
        )

    def _generate_suggestion(self, layer: str, reason: str) -> str:
        suggestions = {
            "L0": "This is a hard, immutable restriction. No workaround possible.",
            "L1": "Request owner to approve this operation or add it to your permissions.",
            "L2": "Check operation timing, sensitivity level, or TLB budget.",
            "L3": "Ensure parameters conform to schema and paths are within project scope.",
            "L4": "Avoid executing these operations in rapid sequence.",
            "L5": "Remove PII/credentials from the output before generating.",
            "L6": "Wait for cooldown period or request owner override.",
            "L7": "Run in Dry-Run mode first to understand the decision flow.",
        }
        for key, suggestion in suggestions.items():
            if key in layer or key in reason:
                return suggestion
        return "Contact the system owner for assistance."
