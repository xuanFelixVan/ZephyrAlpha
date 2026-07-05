# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.evolution.graduated_activation_protocol
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_graduated_activation_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Graduated Activation Protocol — v0.38.0 R485

Blindspot: New FLE rules, automated actions, and ML models are deployed directly
to production with no canary/beta/stable progression. A bad rule or overfitted
model immediately affects all decisions.

Risk: R485 — Single bad deployment breaks entire automated repair pipeline.
No progressive confidence gating. No auto-rollback on regression detection.

Mitigation: Canary → Beta → Stable activation pipeline. Each stage gates on
increasing confidence thresholds. AUTO_PROMOTE on sustained success, AUTO_ROLLBACK
on any regression signal. Configurable stage durations and success criteria.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ActivationStage(str, Enum):
    CANARY = "CANARY"
    BETA = "BETA"
    STABLE = "STABLE"
    ROLLED_BACK = "ROLLED_BACK"


class PromotionDecision(str, Enum):
    PROMOTE = "PROMOTE"
    HOLD = "HOLD"
    ROLLBACK = "ROLLBACK"


@dataclass
class GraduatedActivationProtocol:
    canary_duration: float = 86400.0
    beta_duration: float = 604800.0
    canary_success_threshold: float = 0.95
    beta_success_threshold: float = 0.90
    min_samples_per_stage: int = 100

    rules: dict[str, dict] = field(default_factory=dict)
    promotion_history: list[dict] = field(default_factory=list)
    rollback_history: list[dict] = field(default_factory=list)

    def register_rule(self, rule_id: str) -> dict:
        entry = {
            "stage": ActivationStage.CANARY,
            "activated_at": time.time(),
            "success_count": 0,
            "failure_count": 0,
            "total_applications": 0,
            "promoted_at": None,
        }
        self.rules[rule_id] = entry
        return {"rule_id": rule_id, "stage": entry["stage"].value, "action": "monitor_canary_only"}

    def record_outcome(self, rule_id: str, success: bool) -> None:
        rule = self.rules.get(rule_id)
        if not rule:
            return
        rule["total_applications"] += 1
        if success:
            rule["success_count"] += 1
        else:
            rule["failure_count"] += 1
            if rule["stage"] != ActivationStage.CANARY:
                rule["stage"] = ActivationStage.ROLLED_BACK
                self.rollback_history.append(
                    {
                        "ts": time.time(),
                        "rule_id": rule_id,
                        "from_stage": rule["stage"].value,
                        "reason": "failure_in_production",
                    }
                )

    def evaluate_promotion(self, rule_id: str) -> dict:
        rule = self.rules.get(rule_id)
        if not rule:
            return {"decision": PromotionDecision.HOLD.value, "reason": "unknown_rule"}

        total = rule["total_applications"]
        if total < self.min_samples_per_stage:
            return {
                "decision": PromotionDecision.HOLD.value,
                "reason": f"insufficient_samples:{total}<{self.min_samples_per_stage}",
            }

        success_rate = rule["success_count"] / max(total, 1)
        elapsed = time.time() - rule["activated_at"]

        decision = PromotionDecision.HOLD
        stage = rule["stage"]

        if stage is ActivationStage.CANARY:
            if success_rate >= self.canary_success_threshold and elapsed >= self.canary_duration:
                decision = PromotionDecision.PROMOTE
                rule["stage"] = ActivationStage.BETA
                rule["promoted_at"] = time.time()
                self.promotion_history.append(
                    {
                        "ts": time.time(),
                        "rule_id": rule_id,
                        "from": ActivationStage.CANARY.value,
                        "to": ActivationStage.BETA.value,
                        "success_rate": round(success_rate, 3),
                    }
                )
            elif success_rate < 0.80 and total >= self.min_samples_per_stage:
                decision = PromotionDecision.ROLLBACK
                rule["stage"] = ActivationStage.ROLLED_BACK

        elif stage is ActivationStage.BETA:
            if success_rate >= self.beta_success_threshold and elapsed >= self.beta_duration:
                decision = PromotionDecision.PROMOTE
                rule["stage"] = ActivationStage.STABLE
                rule["promoted_at"] = time.time()
                self.promotion_history.append(
                    {
                        "ts": time.time(),
                        "rule_id": rule_id,
                        "from": ActivationStage.BETA.value,
                        "to": ActivationStage.STABLE.value,
                        "success_rate": round(success_rate, 3),
                    }
                )
            elif success_rate < self.canary_success_threshold:
                decision = PromotionDecision.ROLLBACK
                rule["stage"] = ActivationStage.ROLLED_BACK

        elif stage is ActivationStage.STABLE:
            if success_rate < self.beta_success_threshold:
                decision = PromotionDecision.ROLLBACK
                rule["stage"] = ActivationStage.ROLLED_BACK

        return {
            "rule_id": rule_id,
            "current_stage": rule["stage"].value,
            "decision": decision.value,
            "success_rate": round(success_rate, 3),
            "total_samples": total,
            "elapsed_days": round(elapsed / 86400.0, 1),
        }

    def get_active_canary_rules(self) -> list[str]:
        return [rid for rid, r in self.rules.items() if r["stage"] == ActivationStage.CANARY]

    def get_stable_rules(self) -> list[str]:
        return [rid for rid, r in self.rules.items() if r["stage"] == ActivationStage.STABLE]

    def get_rollback_count(self) -> int:
        return len(self.rollback_history)
