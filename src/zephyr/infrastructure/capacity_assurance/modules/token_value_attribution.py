# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.token_value_attribution
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] deprecated
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_token_value_attribution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Token Value Attribution — Token 成本 vs 产出价值 ROI (盲点 #24, M-30)

DEPRECATED: Use zephyr.infrastructure.budget_enforcement.ROICalculator.
SSoT: MOD-INF-024 budget-enforcer. This module is retained for backward compatibility only.
"""

import time


class TokenValueAttribution:
    """
    Token 价值归因 (M-30, 盲点 #24)
    """

    LOW_ROI_THRESHOLD = 0.1
    HIGH_ROI_THRESHOLD = 1.0

    def __init__(self):
        self._records: list[dict] = []

    def attribute(
        self,
        task_id: str,
        tokens_used: int,
        cost_usd: float,
        output_useful: bool = True,
        complexity_resolved: bool = True,
    ) -> dict:
        if cost_usd <= 0:
            roi = 1.0 if output_useful else 0.0
        else:
            value_score = 1.0 if (output_useful and complexity_resolved) else 0.5 if output_useful else 0.0
            roi = value_score / cost_usd

        tier = (
            "HIGH_VALUE"
            if roi >= self.HIGH_ROI_THRESHOLD
            else "LOW_VALUE"
            if roi < self.LOW_ROI_THRESHOLD
            else "ACCEPTABLE"
        )

        record = {
            "task_id": task_id,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "roi": round(roi, 4),
            "tier": tier,
            "suggestion": "Consider replacing" if tier == "LOW_VALUE" else "",
            "timestamp": time.time(),
        }
        self._records.append(record)
        return record

    def summary(self) -> dict:
        if not self._records:
            return {"total_records": 0}
        total_cost = sum(r["cost_usd"] for r in self._records)
        avg_roi = sum(r["roi"] for r in self._records) / len(self._records)
        return {
            "total_records": len(self._records),
            "total_cost_usd": round(total_cost, 4),
            "avg_roi": round(avg_roi, 4),
        }
