# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.tco_model
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md;src/zephyr/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-RES_tco_model | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging

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
