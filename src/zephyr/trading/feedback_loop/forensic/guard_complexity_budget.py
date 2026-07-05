# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.forensic.guard_complexity_budget
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
# [A_module] module_id=MOD-UNK_guard_complexity_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R523: GuardComplexityBudget
守卫数量边际收益递减追踪 — 1人团队可维护上限告警
"""

from dataclasses import dataclass, field


@dataclass
class GuardComplexityBudget:
    active_guard_count: int = 0
    guard_complexity_history: list[dict] = field(default_factory=list)
    max_history: int = 100
    maintainability_threshold: int = 120
    marginal_value_threshold: float = 0.005

    def register_guard_addition(self, guard_id: str, marginal_value: float) -> dict:
        self.active_guard_count += 1
        entry = {
            "guard_id": guard_id,
            "total_count": self.active_guard_count,
            "marginal_value": round(marginal_value, 4),
        }
        self.guard_complexity_history.append(entry)
        if len(self.guard_complexity_history) > self.max_history:
            self.guard_complexity_history = self.guard_complexity_history[-self.max_history :]

        return self._evaluate_budget(entry)

    def _evaluate_budget(self, entry: dict) -> dict:
        status = "healthy"
        warnings = []

        if self.active_guard_count > self.maintainability_threshold:
            status = "critical"
            warnings.append(
                f"Guard count ({self.active_guard_count}) exceeds maintainability threshold ({self.maintainability_threshold})"
            )
        elif self.active_guard_count > self.maintainability_threshold * 0.8:
            status = "warning"
            warnings.append("Approaching maintainability limit")

        if entry["marginal_value"] < self.marginal_value_threshold:
            if status == "healthy":
                status = "warning"
            warnings.append(f"Marginal value ({entry['marginal_value']}) below threshold")

        recent_values = [e["marginal_value"] for e in self.guard_complexity_history[-8:] if "marginal_value" in e]
        if len(recent_values) >= 4 and all(v < self.marginal_value_threshold * 3 for v in recent_values):
            warnings.append("Persistent low marginal value — consider guard consolidation")

        return {
            "status": status,
            "total_guards": self.active_guard_count,
            "maintainability_threshold": self.maintainability_threshold,
            "warnings": warnings,
            "recommendation": (
                "STOP_ADDING"
                if status == "critical"
                else "CONSOLIDATE"
                if "consolidation" in str(warnings).lower()
                else "CAUTION"
                if status == "warning"
                else "CONTINUE"
            ),
        }

    def get_complexity_report(self) -> dict:
        return {
            "active_guard_count": self.active_guard_count,
            "maintainability_threshold": self.maintainability_threshold,
            "utilization_ratio": round(self.active_guard_count / self.maintainability_threshold, 2),
            "recent_marginal_values": [e.get("marginal_value", 0) for e in self.guard_complexity_history[-10:]],
            "total_historical_additions": len(self.guard_complexity_history),
        }
