# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.tco_model
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md;src/zephyr/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: name 参数
#   fields: 参数 name，类型注解 str
#   code: tco_model.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: total_tokens 参数
#   fields: 参数 total_tokens，类型注解 int
#   code: tco_model.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_column
#   name_en: get_column
#   intro: get_column(name) 源码 L169-L170
#   desc: 源码 L169-L170
#   inputs: name
#   outputs: BudgetColumn | None
# - id: A2
#   name_zh: ② total_annual
#   name_en: total_annual
#   intro: total_annual() 源码 L173-L174
#   desc: 源码 L173-L174
#   inputs: 无参数
#   outputs: float
# - id: A3
#   name_zh: ③ total_monthly
#   name_en: total_monthly
#   intro: total_monthly() 源码 L177-L178
#   desc: 源码 L177-L178
#   inputs: 无参数
#   outputs: float
# - id: A4
#   name_zh: ④ total_with_tolerance
#   name_en: total_with_tolerance
#   intro: total_with_tolerance() 源码 L181-L182
#   desc: 源码 L181-L182
#   inputs: 无参数
#   outputs: float
# - id: A5
#   name_zh: ⑤ token_budget_distribution
#   name_en: token_budget_distribution
#   intro: token_budget_distribution(total_tokens) 源码 L185-L189
#   desc: 源码 L185-L189
#   inputs: total_tokens
#   outputs: dict[str, int]
# - id: A6
#   name_zh: ⑥ column_summary
#   name_en: column_summary
#   intro: column_summary() 源码 L192-L202
#   desc: 源码 L192-L202
#   inputs: 无参数
#   outputs: dict[str, dict[str, float]]
#   （注：A6 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: BudgetColumn | None
#   name_en: BudgetColumn | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-020;MOD-INF-018;MOD-INF-027
# - id: O2
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-020;MOD-INF-018;MOD-INF-027
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import logging
from typing import Final

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BudgetColumn(BaseModel):
    name: str
    annual_cost: float
    precision_budget: float
    tolerance: float
    token_share: float
    description: str

    @property
    def monthly_cost(self) -> float:
        return round(self.annual_cost / 12, 2)

    def exceeds_budget(self, current_spend: float) -> bool:
        return current_spend > self.annual_cost + self.tolerance


TCO_MODEL: Final[dict[str, BudgetColumn]] = {
    "infra": BudgetColumn(
        name="infra",
        annual_cost=2400.00,
        precision_budget=100.00,
        tolerance=200.00,
        token_share=0.10,
        description="基础设施——云/本地/网络",
    ),
    "dev": BudgetColumn(
        name="dev",
        annual_cost=8000.00,
        precision_budget=500.00,
        tolerance=800.00,
        token_share=0.55,
        description="开发——LLM API调用/Session运行时",
    ),
    "ops": BudgetColumn(
        name="ops",
        annual_cost=3000.00,
        precision_budget=200.00,
        tolerance=300.00,
        token_share=0.20,
        description="运维——监控/日志/备份",
    ),
    "risk": BudgetColumn(
        name="risk",
        annual_cost=1200.00,
        precision_budget=100.00,
        tolerance=120.00,
        token_share=0.05,
        description="风险——合规审计/安全扫描/熔断",
    ),
    "metrics": BudgetColumn(
        name="metrics",
        annual_cost=1400.00,
        precision_budget=80.00,
        tolerance=150.00,
        token_share=0.10,
        description="指标——可观测性/Telemetry/TCA",
    ),
}


def get_column(name: str) -> BudgetColumn | None:
    return TCO_MODEL.get(name)


def total_annual() -> float:
    return round(sum(c.annual_cost for c in TCO_MODEL.values()), 2)


def total_monthly() -> float:
    return round(total_annual() / 12, 2)


def total_with_tolerance() -> float:
    return round(sum(c.annual_cost + c.tolerance for c in TCO_MODEL.values()), 2)


def token_budget_distribution(total_tokens: int) -> dict[str, int]:
    dist: dict[str, int] = {}
    for key, col in TCO_MODEL.items():
        dist[key] = int(total_tokens * col.token_share)
    return dist


def column_summary() -> dict[str, dict[str, float]]:
    return {
        key: {
            "annual_cost": col.annual_cost,
            "monthly_cost": col.monthly_cost,
            "precision_budget": col.precision_budget,
            "tolerance": col.tolerance,
            "token_share": col.token_share,
        }
        for key, col in TCO_MODEL.items()
    }
