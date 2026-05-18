# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.context_model_strategy

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""context_model_strategy.py — 模型选择策略 (DD118, TASK-020)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ModelStrategy:
    task_type: str
    budget_level: str
    model: str
    fallback_model: str


class ContextModelStrategy:
    """task_type→model selection: simple task→small model, complex→large (DD118)."""
    _STRATEGIES: dict[str, ModelStrategy] = {
        "CODE_GEN": ModelStrategy("CODE_GEN", "L2", "Qwen2.5-3B-Instruct", "Qwen2.5-Coder-7B"),
        "CODE_REVIEW": ModelStrategy("CODE_REVIEW", "L2", "Qwen2.5-Coder-7B", "Claude-Sonnet-4"),
        "ANALYSIS": ModelStrategy("ANALYSIS", "L3", "Claude-Sonnet-4", "GPT-4o"),
    }

    def select(self, task_type: str) -> ModelStrategy:
        return self._STRATEGIES.get(task_type, ModelStrategy(task_type, "L2", "Qwen2.5-3B-Instruct", "Qwen2.5-Coder-7B"))
