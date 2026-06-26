---
module_id: KE-2920
status: active
title: src/zephyr/llm-security/layers/l5_resource_protection.py
category: module_blueprint
ttl: permanent
---

# src/zephyr/llm-security/layers/l5_resource_protection.py

src/zephyr/llm-security/layers/l5_resource_protection.py

@dataclass
class TokenBudget:
    request_limit: int = 16_000       # 单请求Token上限
    hourly_limit: int = 500_000       # 每小时Token上限
    daily_limit: int = 5_000_000      # 每天Token上限
    # 按模型分别配置可用模型专属预算表


@dataclass
class CostBudget:
    daily_limit_usd: float = 10.0     # 每日API费用上限
    monthly_limit_usd: float = 100.0  # 每月API费用上限
    warn_threshold_pct: float = 0.8   # 预警百分比（80%时告警）
    critical_threshold_pct: float = 0.95  # 严重预警（95%时熔断）


class ResourceProtectionLayer:
    """L5 资源保护层——Token预算+速率限制+成本熔断+执行保护。"""

    def __init__(
        self,
        token_budget: TokenBudget,
        cost_budget: CostBudget,
    ):
        ...

    def check_token_budget(
        self,
        request_tokens: int,
        session_id: str,
    ) -> BudgetResult:
        """检查请求是否在Token预算内。

        逐级检查：单请求 → 小时 → 天。
        任一超限 → 拒绝 + BUDGET_EXCEEDED事件。
        """

    def check_rate_limit(
        self,
        api_endpoint: str,
        caller_id: str,
    ) -> RateLimitResult:
        """速率限制检查——可选用 sliding window / token bucket 算法。"""

    def check_cost_budget(
        self,
        estimated_cost_usd: float,
    ) -> CostBudgetResult:
        """成本预算检查——当前累积费用是否接近/超过预算上限。"""

    def enforce_agent_limits(
        self,
        agent_id: str,
        elapsed_s: float,
        steps_taken: int,
    ) -> AgentLimitResult:
        """Agent执行保护——检查是否超过时长/步数上限。"""

    def record_usage(
        self,
        tokens: int,
        cost_usd: float,
        api_endpoint: str,
        session_id: str,
    ) -> None:
        """记录使用量到本地计数器（内存 + 定期持久化到日志）。"""
```
