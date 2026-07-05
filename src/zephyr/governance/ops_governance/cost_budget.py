# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.cost_budget
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.shared.errors; zephyr.shared.metrics
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_cost_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
cost_budget.py —— AI 成本预算与强制熔断（Phase 11 | 盲点 B26）

痛点修复：LLM API 调用无硬性成本限制，Agent 异常循环可在 10 分钟内刷光配额。

设计对标：
  - AgentBudget / PydanticAI Logfire: 每 API 调用的成本追踪
  - OpenAI tiktoken: token 计价模型
  - AWS Budgets: 硬性熔断阈值 + 预警线

AI 施工约定：
  - 任何 LLM API 调用 MUST 通过 check_budget() 预检
  - 超出 hard_limit 时 MUST 抛 CostBudgetExceededError
  - 每次 API 调用 MUST 调用 record_usage() 更新累计消费

SSoT: MOD-INF-024 §12 盲点 B26
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.observability.metrics import COUNT_LLM_CALLS, get_registry

_logger = logging.getLogger(__name__)


class CostBudgetExceededError(ZephyrBaseError):
    """成本预算超出硬性熔断阈值时抛出。"""

    def __init__(self, current: float, limit: float, provider: str, model: str):
        self.current = current
        self.limit = limit
        self.provider = provider
        self.model = model
        super().__init__(f"Cost budget exceeded: ${current:.4f} / ${limit:.4f} (provider={provider}, model={model})")


@dataclass
class PricingTier:
    """单模型定价档位。所有价格以 USD 为单位，per 1K tokens。"""

    model: str
    input_price_per_1k: float
    output_price_per_1k: float
    cached_input_price_per_1k: float | None = None


@dataclass
class CostBudget:
    """AI 成本预算管理器——跟踪累计消费、强制熔断。

    Usage::

        budget = CostBudget(hard_limit=5.00)
        budget.set_pricing("openai", "gpt-4o", input_1k=0.0025, output_1k=0.0100)
        budget.check_budget("openai", "gpt-4o")
        budget.record_usage("openai", "gpt-4o", input_tokens=500, output_tokens=200)

    Attributes:
        hard_limit: 硬性熔断阈值（USD）。超出即抛 CostBudgetExceededError。
        warning_ratio: 预警比例（0.0-1.0）。超出 hard_limit * warning_ratio 时发 warning。
        cumulative_cost: 累计消费（USD）。
        call_count: API 调用次数。
    """

    hard_limit: float = 10.00
    warning_ratio: float = 0.80
    cumulative_cost: float = 0.0
    call_count: int = 0

    provider_pricing: dict[str, dict[str, PricingTier]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def set_pricing(
        self,
        provider: str,
        model: str,
        input_1k: float,
        output_1k: float,
        cached_input_1k: float | None = None,
    ) -> None:
        """注册 provider + model 的定价信息。"""
        tier = PricingTier(
            model=model,
            input_price_per_1k=input_1k,
            output_price_per_1k=output_1k,
            cached_input_price_per_1k=cached_input_1k,
        )
        self.provider_pricing.setdefault(provider, {})[model] = tier

    def get_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cached_input_tokens: int = 0,
    ) -> float:
        """计算单次 API 调用的预估成本（USD）。"""
        tier = self.provider_pricing.get(provider, {}).get(model)
        if tier is None:
            return 0.0
        cost = 0.0
        cost += (input_tokens / 1000.0) * tier.input_price_per_1k
        cost += (output_tokens / 1000.0) * tier.output_price_per_1k
        if cached_input_tokens and tier.cached_input_price_per_1k is not None:
            cost += (cached_input_tokens / 1000.0) * tier.cached_input_price_per_1k
        return cost

    def check_budget(self, provider: str = "", model: str = "") -> None:
        """预检：当前累计消费是否超出硬性熔断阈值。

        Raises:
            CostBudgetExceededError: 超出 hard_limit。
        """
        with self._lock:
            if self.cumulative_cost >= self.hard_limit:
                raise CostBudgetExceededError(
                    current=self.cumulative_cost,
                    limit=self.hard_limit,
                    provider=provider,
                    model=model,
                )

    def check_budget_or_warn(self, provider: str = "", model: str = "") -> str | None:
        """预检 + 预警。超出 warning_ratio 时返回预警消息，超出 hard_limit 抛异常。

        Returns:
            预警消息字符串或 None。
        """
        with self._lock:
            if self.cumulative_cost >= self.hard_limit:
                raise CostBudgetExceededError(
                    current=self.cumulative_cost,
                    limit=self.hard_limit,
                    provider=provider,
                    model=model,
                )
            if self.cumulative_cost >= self.hard_limit * self.warning_ratio:
                remaining = self.hard_limit - self.cumulative_cost
                return (
                    f"Cost budget warning: ${self.cumulative_cost:.4f} / ${self.hard_limit:.4f} "
                    f"({self.cumulative_cost / self.hard_limit * 100:.1f}%), "
                    f"${remaining:.4f} remaining"
                )
        return None

    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cached_input_tokens: int = 0,
    ) -> float:
        """记录一次 API 调用并更新累计消费。

        Returns:
            本次调用的成本（USD）。
        """
        cost = self.get_cost(provider, model, input_tokens, output_tokens, cached_input_tokens)
        with self._lock:
            self.cumulative_cost += cost
            self.call_count += 1
        self._emit_metrics(provider, model, cost)
        return cost

    def _emit_metrics(self, provider: str, model: str, cost: float) -> None:
        """向 metrics 注册表发送成本指标。"""
        try:
            registry = get_registry()
            registry.inc(COUNT_LLM_CALLS, labels={"provider": provider, "model": model})
            if cost > 0:
                registry.observe(
                    "zephyr_llm_cost_usd",
                    cost,
                    labels={"provider": provider, "model": model},
                )
        except Exception as e:
            _logger.warning("Failed to emit LLM cost metrics: %s", e)

    @property
    def remaining(self) -> float:
        """剩余预算（USD）。"""
        return max(0.0, self.hard_limit - self.cumulative_cost)

    @property
    def usage_ratio(self) -> float:
        """预算使用比例（0.0-1.0）。"""
        if self.hard_limit <= 0:
            return 1.0
        return min(1.0, self.cumulative_cost / self.hard_limit)

    def reset(self) -> None:
        """重置累计消费（如按日/按月重置预算窗口）。"""
        with self._lock:
            self.cumulative_cost = 0.0
            self.call_count = 0


__all__ = [
    "CostBudget",
    "CostBudgetExceededError",
    "PricingTier",
]
