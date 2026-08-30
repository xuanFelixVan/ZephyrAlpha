# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.debt_projector
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/budget/test_debt_projector.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
去重债务预测器 — weeks_to_payoff + intake_rate vs fix_rate 蒙特卡洛模拟.

职责：
  - 基于当前债务数 + 引入速率 + 修复速率 -> 预测清零日期
  - 蒙特卡洛模拟（1000次迭代）-> 置信区间
  - intake_rate > fix_rate -> 债务正向增长 -> ALERT

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: debt_projector.py
# 层: 算法
# - id: A1
#   name_zh: ① DebtProjector
#   name_en: DebtProjector
#   intro: 去重债务预测模型.
#   desc: 去重债务预测模型.；公共方法（定义序）: project；源码 L73-L129
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DebtProjector
#   downstream: tests/governance/budget/test_debt_projector.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
