"""
Budget-Aware Prompt Merger — Prompt 与容量指令语义冲突 (盲点 #40)
三模式合并：
  - full_build: 完整上下文（高容量任务）
  - essential_only: 仅必要指令（常规任务）
  - minimal_viable: 最小可用（低容量预算）
"""
from enum import Enum
from typing import Any, Optional


class MergeMode(Enum):
    FULL_BUILD = "full_build"
    ESSENTIAL_ONLY = "essential_only"
    MINIMAL_VIABLE = "minimal_viable"


class BudgetAwarePromptMerger:
    """
    预算感知 Prompt 合并器 (盲点 #40)
    """

    def __init__(self, budget_remaining_pct: float = 1.0):
        self.budget_remaining_pct = budget_remaining_pct

    def select_mode(self) -> MergeMode:
        if self.budget_remaining_pct > 0.5:
            return MergeMode.FULL_BUILD
        if self.budget_remaining_pct > 0.1:
            return MergeMode.ESSENTIAL_ONLY
        return MergeMode.MINIMAL_VIABLE

    def merge(self, base_prompt: str, capacity_constraints: dict,
              extra_context: Optional[str] = None) -> str:
        mode = self.select_mode()
        parts = [base_prompt]

        if mode == MergeMode.FULL_BUILD:
            for key, val in capacity_constraints.items():
                parts.append(f"{key}: {val}")
            if extra_context:
                parts.append(extra_context)
        elif mode == MergeMode.ESSENTIAL_ONLY:
            essential = {k: v for k, v in capacity_constraints.items()
                         if k in ("budget_remaining", "model_tier")}
            for key, val in essential.items():
                parts.append(f"{key}: {val}")
        else:
            parts.append(f"budget_remaining: {self.budget_remaining_pct:.0%}")

        return "\n".join(parts)
