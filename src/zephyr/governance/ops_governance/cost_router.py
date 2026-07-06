# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.cost_router
# [DOMAIN] D_GOVERNANCE
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
# [A_module] module_id=MOD-RES_cost_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
from enum import Enum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    DEEPSEEK = "deepseek"
    GLM4_7 = "glm-4.7"
    GLM4_6 = "glm-4.6"
    GLM4_5 = "glm-4.5"
    KIMI_K2 = "kimi-k2"
    CLAUDE_SONNET_4_5 = "claude-sonnet-4.5"
    O4_MINI = "o4-mini"
    GPT5_1_CODEX = "gpt-5.1-codex"
    GROK_4 = "grok-4"
    GPT5_2 = "gpt-5.2"
    QWEN3_CODER = "qwen3-coder"


class RoutingPolicy(str, Enum):
    COST_MIN = "COST_MIN"
    THROUGHPUT = "THROUGHPUT"


class ModelPricing(BaseModel):
    provider: LLMProvider
    cost_per_1k_input: float
    cost_per_1k_output: float
    throughput_rank: int
    context_window: int


PRICING_TABLE: Final[dict[LLMProvider, ModelPricing]] = {
    LLMProvider.DEEPSEEK: ModelPricing(
        provider=LLMProvider.DEEPSEEK,
        cost_per_1k_input=0.27,
        cost_per_1k_output=1.10,
        throughput_rank=4,
        context_window=65536,
    ),
    LLMProvider.GLM4_7: ModelPricing(
        provider=LLMProvider.GLM4_7,
        cost_per_1k_input=0.50,
        cost_per_1k_output=2.00,
        throughput_rank=5,
        context_window=32768,
    ),
    LLMProvider.GLM4_6: ModelPricing(
        provider=LLMProvider.GLM4_6,
        cost_per_1k_input=0.40,
        cost_per_1k_output=1.60,
        throughput_rank=6,
        context_window=32768,
    ),
    LLMProvider.GLM4_5: ModelPricing(
        provider=LLMProvider.GLM4_5,
        cost_per_1k_input=0.30,
        cost_per_1k_output=1.20,
        throughput_rank=7,
        context_window=32768,
    ),
    LLMProvider.KIMI_K2: ModelPricing(
        provider=LLMProvider.KIMI_K2,
        cost_per_1k_input=0.60,
        cost_per_1k_output=2.40,
        throughput_rank=3,
        context_window=131072,
    ),
    LLMProvider.CLAUDE_SONNET_4_5: ModelPricing(
        provider=LLMProvider.CLAUDE_SONNET_4_5,
        cost_per_1k_input=3.00,
        cost_per_1k_output=12.00,
        throughput_rank=6,
        context_window=200000,
    ),
    LLMProvider.O4_MINI: ModelPricing(
        provider=LLMProvider.O4_MINI,
        cost_per_1k_input=1.10,
        cost_per_1k_output=4.40,
        throughput_rank=1,
        context_window=200000,
    ),
    LLMProvider.GPT5_1_CODEX: ModelPricing(
        provider=LLMProvider.GPT5_1_CODEX,
        cost_per_1k_input=2.50,
        cost_per_1k_output=10.00,
        throughput_rank=3,
        context_window=128000,
    ),
    LLMProvider.GROK_4: ModelPricing(
        provider=LLMProvider.GROK_4,
        cost_per_1k_input=2.00,
        cost_per_1k_output=8.00,
        throughput_rank=4,
        context_window=131072,
    ),
    LLMProvider.GPT5_2: ModelPricing(
        provider=LLMProvider.GPT5_2,
        cost_per_1k_input=5.00,
        cost_per_1k_output=20.00,
        throughput_rank=5,
        context_window=256000,
    ),
    LLMProvider.QWEN3_CODER: ModelPricing(
        provider=LLMProvider.QWEN3_CODER,
        cost_per_1k_input=0.35,
        cost_per_1k_output=1.40,
        throughput_rank=2,
        context_window=131072,
    ),
}


def estimate_cost(
    provider: LLMProvider,
    estimated_tokens: int,
    input_output_ratio: float = 0.3,
) -> float:
    """根据预估token总量计算成本。"""
    p = PRICING_TABLE.get(provider)
    if p is None:
        return float("inf")
    input_tokens = estimated_tokens * input_output_ratio
    output_tokens = estimated_tokens * (1.0 - input_output_ratio)
    cost = p.cost_per_1k_input * (input_tokens / 1000) + p.cost_per_1k_output * (output_tokens / 1000)
    return round(cost, 4)


def route_min_cost(estimated_tokens: int) -> LLMProvider:
    """给定 token 预估量，返回成本最低模型。"""
    best_provider = LLMProvider.DEEPSEEK
    best_cost = float("inf")
    for provider in LLMProvider:
        cost = estimate_cost(provider, estimated_tokens)
        if cost < best_cost:
            best_cost = cost
            best_provider = provider
    return best_provider


def route(
    estimated_tokens: int,
    policy: RoutingPolicy = RoutingPolicy.COST_MIN,
) -> LLMProvider:
    """A/B 双路由策略。"""
    if policy is RoutingPolicy.COST_MIN:
        return route_min_cost(estimated_tokens)
    if policy is RoutingPolicy.THROUGHPUT:
        candidates = sorted(PRICING_TABLE.values(), key=lambda m: m.throughput_rank)
        return candidates[0].provider
    return LLMProvider.DEEPSEEK


def get_pricing(provider: LLMProvider) -> ModelPricing | None:
    return PRICING_TABLE.get(provider)


def list_models_sorted_by_cost() -> list[tuple[LLMProvider, float, float]]:
    pricing = [(p.provider, p.cost_per_1k_input, p.cost_per_1k_output) for p in PRICING_TABLE.values()]
    return sorted(pricing, key=lambda x: x[1] + x[2])
