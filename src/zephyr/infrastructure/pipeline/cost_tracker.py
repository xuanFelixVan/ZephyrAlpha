# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.cost_tracker
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_cost_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CostTracker —— LLM 调用成本追踪器（SRC-0025）
============================================

从 PipelineOrchestrator 提取成本追踪逻辑为独立组件。

职责：
  - 记录每次 LLM 调用的成本（模型、token 数、美元金额）
  - 基于 ModelRouter 定价常量估算调用成本
  - 提供成本汇总（按模型分组、总美元金额、记录数）
  - 状态持久化（save_state / load_state）

依据：重组蓝图 §3.3 + B161 成本追踪
"""

from __future__ import annotations

from typing import Any

from zephyr.infrastructure.pipeline.model_router import ModelRouter
from zephyr.infrastructure.pipeline.models import CostRecord

__all__ = ["CostTracker"]


# class-name-alias: Pipeline LLM 调用成本追踪器（SRC-0025），内存态，区别于 infrastructure/cost_tracker.py 的 SQLite 持久化成本追踪器
class CostTracker:
    """LLM 调用成本追踪器。

    记录每次模型调用的 token 使用量和美元成本，支持：
      - 实际 API 返回的成本记录
      - 基于定价常量的模拟成本估算
      - 按模型分组的成本汇总
      - 状态持久化与恢复

    使用：
        tracker = CostTracker()
        tracker.record_call("deepseek", 5000, 0.01305)
        tracker.estimate_cost("claude", 3000)  # -> 0.09
        tracker.total_cost()                   # -> 0.0131
        tracker.summary()                      # -> {"total_usd": ..., "by_model": {...}}
    """

    def __init__(self) -> None:
        self._total: float = 0.0
        self._records: list[CostRecord] = []

    @property
    def records(self) -> list[CostRecord]:
        """返回成本记录列表（只读视图）。"""
        return list(self._records)

    # ------------------------------------------------------------------
    # 核心 API
    # ------------------------------------------------------------------

    def record_call(self, model: str, tokens_input: int, cost_usd: float) -> None:
        """记录一次 LLM 调用的成本。

        Args:
            model: 模型名称（"deepseek", "glm", "claude"）
            tokens_input: 消耗的 token 数量
            cost_usd: 美元成本
        """
        self._total += cost_usd
        self._records.append(
            CostRecord(
                model=model,
                tokens_input=tokens_input,
                cost_usd=cost_usd,
            )
        )

    def estimate_cost(self, model: str, tokens: int) -> float:
        """估算指定模型处理给定 token 量的成本。

        基于 ModelRouter 的 MODEL_COST_PER_1K_INPUT / MODEL_COST_PER_1K_OUTPUT
        定价常量，使用相同的 token 量估算输入和输出成本。

        Args:
            model: 模型名称
            tokens: token 数量

        Returns:
            估算成本（USD），保留 6 位小数
        """
        cost_input = (tokens / 1000.0) * ModelRouter.MODEL_COST_PER_1K_INPUT.get(model, 0.0)
        cost_output = (tokens / 1000.0) * ModelRouter.MODEL_COST_PER_1K_OUTPUT.get(model, 0.0)
        return round(cost_input + cost_output, 6)

    def total_cost(self) -> float:
        """返回累计总成本（USD），保留 4 位小数。"""
        return round(self._total, 4)

    def summary(self) -> dict[str, Any]:
        """完整成本汇总。

        Returns:
            包含 total_usd、by_model（按模型拆分）、record_count 的字典
        """
        return {
            "total_usd": round(self._total, 4),
            "by_model": {
                m: round(sum(c.cost_usd for c in self._records if c.model == m), 4)
                for m in ("deepseek", "glm", "claude")
                if any(c.model == m for c in self._records)
            },
            "record_count": len(self._records),
        }

    # ------------------------------------------------------------------
    # 状态持久化
    # ------------------------------------------------------------------

    def save_state(self) -> dict:
        """导出状态（供 PipelineOrchestrator 持久化）。

        Returns:
            包含 total 和 records（最近 100 条）的状态字典
        """
        return {
            "total": self._total,
            "records": [c.model_dump() for c in self._records[-100:]],
        }

    def load_state(self, state: dict) -> None:
        """从持久化字典恢复状态。

        Args:
            state: save_state() 产出的状态字典
        """
        self._total = float(state.get("total", 0.0))
        self._records = [CostRecord(**c) for c in state.get("records", [])]
