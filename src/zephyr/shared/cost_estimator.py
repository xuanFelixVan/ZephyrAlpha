"""
Cost Estimator — 执行前成本预估 (M-26)
Pre-flight Estimation：在执行 LLM 调用前预估 Token 消耗和成本。

与 Token Budget 四级体系的关系：
  - Level 1: MCP 工具级 → tool_contracts.yaml（已有）
  - Level 2: session 级 → context_budget_tracker.py（已有）
  - Level 3: org 级 → 本模块 + error_budget_tracker.py
  - Level 4: global 级 → 远期规划
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelPricing:
    model_name: str
    input_per_1k: float
    output_per_1k: float
    max_context_tokens: int


DEFAULT_PRICING = {
    "deepseek-chat": ModelPricing(
        model_name="deepseek-chat", input_per_1k=0.002, output_per_1k=0.008,
        max_context_tokens=128000
    ),
    "deepseek-reasoner": ModelPricing(
        model_name="deepseek-reasoner", input_per_1k=0.004, output_per_1k=0.016,
        max_context_tokens=128000
    ),
    "qwen2.5-3b-onnx": ModelPricing(
        model_name="qwen2.5-3b-onnx", input_per_1k=0.0, output_per_1k=0.0,
        max_context_tokens=32768
    ),
}


@dataclass
class CostEstimate:
    affordable: bool
    estimated_cost_usd: float = 0.0
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    model: str = ""
    suggestion: str = ""


class CostEstimator:
    """
    执行前成本预估器 (M-26)
    """

    DEFAULT_SESSION_BUDGET_USD = 5.0
    DEFAULT_DAILY_BUDGET_USD = 20.0

    def __init__(self, pricing: Optional[dict[str, ModelPricing]] = None):
        self.pricing = pricing or DEFAULT_PRICING
        self._daily_cost = 0.0

    def estimate(self, prompt_tokens: int, model: str,
                 expected_output_tokens: int = 500,
                 session_budget_remaining: Optional[float] = None) -> CostEstimate:
        pricing = self.pricing.get(model)
        if pricing is None:
            return CostEstimate(
                affordable=False,
                model=model,
                suggestion=f"Unknown model: {model}"
            )

        if prompt_tokens > pricing.max_context_tokens:
            return CostEstimate(
                affordable=False,
                estimated_input_tokens=prompt_tokens,
                model=model,
                suggestion=f"Prompt tokens ({prompt_tokens}) exceed model limit ({pricing.max_context_tokens})"
            )

        input_cost = prompt_tokens * pricing.input_per_1k / 1000
        output_cost = expected_output_tokens * pricing.output_per_1k / 1000
        total_cost = input_cost + output_cost

        budget = session_budget_remaining if session_budget_remaining is not None else self.DEFAULT_SESSION_BUDGET_USD

        if total_cost > budget:
            return CostEstimate(
                affordable=False,
                estimated_cost_usd=total_cost,
                estimated_input_tokens=prompt_tokens,
                estimated_output_tokens=expected_output_tokens,
                model=model,
                suggestion=f"Cost ${total_cost:.4f} exceeds budget ${budget:.2f}. Consider downgrading model."
            )

        self._daily_cost += total_cost

        return CostEstimate(
            affordable=True,
            estimated_cost_usd=total_cost,
            estimated_input_tokens=prompt_tokens,
            estimated_output_tokens=expected_output_tokens,
            model=model,
        )

    def estimate_input_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def estimate_output_tokens(self, prompt_complexity: str) -> int:
        complexity_map = {"simple": 100, "moderate": 500, "complex": 2000}
        return complexity_map.get(prompt_complexity.lower(), 500)

    def get_daily_cost(self) -> float:
        return self._daily_cost

    def reset_daily_cost(self):
        self._daily_cost = 0.0

    def suggest_alternative(self, model: str) -> Optional[str]:
        alternatives = {
            "deepseek-reasoner": "deepseek-chat",
            "deepseek-chat": "qwen2.5-3b-onnx",
        }
        return alternatives.get(model)


_estimator: Optional[CostEstimator] = None


def get_cost_estimator() -> CostEstimator:
    global _estimator
    if _estimator is None:
        _estimator = CostEstimator()
    return _estimator
