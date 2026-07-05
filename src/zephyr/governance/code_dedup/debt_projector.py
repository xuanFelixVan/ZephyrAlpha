# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.debt_projector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/budget/test_debt_projector.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_debt_projector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""去重债务预测器 — weeks_to_payoff + intake_rate vs fix_rate 蒙特卡洛模拟.

职责：
  - 基于当前债务数 + 引入速率 + 修复速率 → 预测清零日期
  - 蒙特卡洛模拟（1000次迭代）→ 置信区间
  - intake_rate > fix_rate → 债务正向增长 → ALERT
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class DebtProjectionResult:
    weeks_to_payoff: float
    current_debt: int
    intake_rate: float
    fix_rate: float
    projected_zero_date: str
    confidence_interval_95: tuple[float, float]
    is_growing: bool
    recommendation: str


class DebtProjector:
    """去重债务预测模型."""

    _SIMULATION_ITERATIONS: int = 1000

    def project(
        self,
        current_debt_groups: int,
        intake_rate_groups_per_week: float,
        fix_rate_groups_per_week: float,
    ) -> DebtProjectionResult:
        """预测债务清零时间."""
        net_change = fix_rate_groups_per_week - intake_rate_groups_per_week
        is_growing = net_change <= 0

        if net_change <= 0:
            weeks = float("inf")
            zero_date = "NEVER（债务持续增长）"
            ci = (float("inf"), float("inf"))
            rec = "ALERT: fix_rate ≤ intake_rate——债务永远无法清零。建议提高修复速率或减少新引入。"
        else:
            weeks_base = current_debt_groups / net_change
            sim_results = self._monte_carlo_sim(
                current_debt_groups, intake_rate_groups_per_week, fix_rate_groups_per_week
            )
            sim_results.sort()
            n = len(sim_results)
            lower = sim_results[int(n * 0.025)]
            upper = sim_results[int(n * 0.975)]

            weeks = round(weeks_base, 1)
            ci = (round(lower, 1), round(upper, 1))
            zero_date = (datetime.now(UTC) + timedelta(weeks=weeks_base)).strftime("%Y-%m-%d")
            if weeks <= 4:
                rec = f"近在咫尺：{weeks}周(≈{int(weeks / 4.3 + 0.5)}月)——加大力度，一举清零"
            elif weeks <= 12:
                rec = f"可行路径：{weeks}周(≈{int(weeks / 4.3 + 0.5)}月)——保持修复节奏"
            else:
                rec = f"长期任务：{weeks}周——建议分阶段milestone推进"

        return DebtProjectionResult(
            weeks_to_payoff=weeks,
            current_debt=current_debt_groups,
            intake_rate=intake_rate_groups_per_week,
            fix_rate=fix_rate_groups_per_week,
            projected_zero_date=zero_date,
            confidence_interval_95=ci,
            is_growing=is_growing,
            recommendation=rec,
        )

    def _monte_carlo_sim(self, debt: int, intake: float, fix: float) -> list[float]:
        results: list[float] = []
        for _ in range(self._SIMULATION_ITERATIONS):
            net = max(0.01, fix * random.gauss(1.0, 0.15) - intake * random.gauss(1.0, 0.15))
            results.append(debt / net)
        return results
