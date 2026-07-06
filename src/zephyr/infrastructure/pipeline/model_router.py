# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.model_router
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.models
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
# [A_module] module_id=MOD-INF_model_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ModelRouter — 模型路由与降级链管理
===================================

依据：GOV-AI-002 §二 决策树 + §三 补充（降级链）
从 PipelineOrchestrator 提取（SRC-0023），独立管理模型选择、版本映射、
上下文限制、成本估算和降级链。

三层模型策略（GOV-AI-002 §一）：
  DeepSeek V4 Pro → 主力生产（M1-M4 + M6/M8/M9/M10/M11）—— 1.74/3.48/M
  GLM-5.1        → 深度审查（M7 + M5）—— Trae CN免费
  Claude Opus 4.7 → 特种救援（DeepSeek失败3次 / GLM驳回2次 / Owner关键标记 / security标签 / experimental标签）

使用：
    from zephyr.infrastructure.pipeline.model_router import ModelRouter

    model = ModelRouter.resolve_model(task_card)
    chain = ModelRouter.fallback_chain_for("deepseek")
    cost = ModelRouter.estimate_cost("deepseek", 5000)  # -> float（总成本 USD）
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from zephyr.shared.foundation.models import TaskCard

__all__ = ["ModelRouter"]


class ModelRouter:
    """模型路由器 — 模型选择、降级链、成本估算。

    所有属性和方法均为类级别（静态），无需实例化。
    """

    # ------------------------------------------------------------------
    # 模型降级 Fallback 链 —— GOV-AI-002 §三 补充
    # ------------------------------------------------------------------

    FALLBACK_CHAIN: ClassVar[dict[str, list[str]]] = {
        "deepseek": ["glm", "claude"],
        "glm": ["deepseek", "claude"],
        "claude": [],
    }

    # ------------------------------------------------------------------
    # 模型版本映射 —— B150 模型版本锁定
    # 5.141.1 修复: 模型版本通过环境变量外部化, 避免硬编码 (与 deepseek_chat.py /
    # llm_gateway.py 的 os.getenv 模式统一)。使用 *_MODEL_VERSION 后缀以区别于
    # DEEPSEEK_MODEL(聊天默认模型) 等已有变量，版本映射是独立语义。
    # ------------------------------------------------------------------

    MODEL_VERSION_MAP: ClassVar[dict[str, str]] = {
        "deepseek": os.getenv("DEEPSEEK_MODEL_VERSION", "deepseek-v4-pro"),
        "glm": os.getenv("GLM_MODEL_VERSION", "glm-5.1"),
        "claude": os.getenv("ANTHROPIC_MODEL_VERSION", "claude-opus-4.7"),
    }

    # ------------------------------------------------------------------
    # 模型上下文限制
    # ------------------------------------------------------------------

    MODEL_CONTEXT_LIMITS: ClassVar[dict[str, int]] = {
        "deepseek": 128_000,
        "glm": 128_000,
        "claude": 200_000,
    }

    # ------------------------------------------------------------------
    # 模型成本（每 1K tokens，USD）—— B161 成本追踪
    # ------------------------------------------------------------------

    MODEL_COST_PER_1K_INPUT: ClassVar[dict[str, float]] = {
        "deepseek": 0.00174,
        "glm": 0.0,
        "claude": 0.005,
    }

    MODEL_COST_PER_1K_OUTPUT: ClassVar[dict[str, float]] = {
        "deepseek": 0.00348,
        "glm": 0.0,
        "claude": 0.025,
    }

    # ------------------------------------------------------------------
    # 模型路由 — GOV-AI-002 §二 决策树
    # ------------------------------------------------------------------

    @staticmethod
    def resolve_model(task_card: TaskCard) -> str:
        """根据 TaskCard 解析执行模型。

        GOV-AI-002 §二 决策树：
          - C管线 → "none"
          - 关键/rescue 关键词 → claude
          - security 标签 → claude
          - experimental 标签 → claude
          - ai_autonomy_level == "unsafe" → claude
          - 其他 → task_card.execution_model

        Args:
            task_card: 任务卡片

        Returns:
            模型名称字符串（"deepseek", "glm", "claude", "none" 或 task_card.execution_model）
        """
        model = task_card.execution_model

        if task_card.assigned_pipeline == "C":
            return "none"

        critical_keywords = ["关键", "critical", "rescue"]
        if any(kw in task_card.title.lower() for kw in critical_keywords):
            return "claude"

        if "security" in task_card.tags:
            return "claude"
        if "experimental" in task_card.tags:
            return "claude"

        if task_card.ai_autonomy_level == "unsafe":
            return "claude"

        return model

    # ------------------------------------------------------------------
    # 降级链查询
    # ------------------------------------------------------------------

    @staticmethod
    def fallback_chain_for(model: str) -> list[str]:
        """返回指定模型的降级链。

        Args:
            model: 模型名称（"deepseek", "glm", "claude"）

        Returns:
            降级链列表，若模型不在已知链中则返回空列表
        """
        return ModelRouter.FALLBACK_CHAIN.get(model, [])

    # ------------------------------------------------------------------
    # 成本估算 —— B161 成本追踪
    # ------------------------------------------------------------------

    @staticmethod
    def estimate_cost(model: str, tokens_used: int) -> float:
        """估算模型调用总成本（USD）。

        5.12.2#2 签名漂移治本（2026-07-02）：返回类型从 dict 收敛为 float（总成本），
        与 cost_tracker/cost_router/pricing_sync 的 estimate_cost 统一，满足 EstimateCostFn Protocol。
        分项明细请用 estimate_cost_detailed()。

        Args:
            model: 模型名称
            tokens_used: 使用的 token 数

        Returns:
            总成本（USD），保留 6 位小数
        """
        cost_input = (tokens_used / 1000.0) * ModelRouter.MODEL_COST_PER_1K_INPUT.get(model, 0.0)
        cost_output = (tokens_used / 1000.0) * ModelRouter.MODEL_COST_PER_1K_OUTPUT.get(model, 0.0)
        return round(cost_input + cost_output, 6)

    @staticmethod
    def estimate_cost_detailed(model: str, tokens_used: int) -> dict[str, float]:
        """估算模型调用成本（USD），返回分项明细。

        5.12.2#2 签名漂移治本（2026-07-02）：从 estimate_cost 拆出，保留分项能力。
        estimate_cost 改返回 float 总成本，分项需求用此方法。

        Args:
            model: 模型名称
            tokens_used: 使用的 token 数

        Returns:
            {"input_cost": float, "output_cost": float, "total_cost": float}
        """
        cost_input = (tokens_used / 1000.0) * ModelRouter.MODEL_COST_PER_1K_INPUT.get(model, 0.0)
        cost_output = (tokens_used / 1000.0) * ModelRouter.MODEL_COST_PER_1K_OUTPUT.get(model, 0.0)
        total_cost = round(cost_input + cost_output, 6)
        return {
            "input_cost": round(cost_input, 6),
            "output_cost": round(cost_output, 6),
            "total_cost": total_cost,
        }

    # ------------------------------------------------------------------
    # 模型版本查询
    # ------------------------------------------------------------------

    @staticmethod
    def model_version_for(model: str) -> str:
        """返回模型的版本字符串。

        Args:
            model: 模型名称

        Returns:
            版本字符串，若未找到则返回模型名称本身
        """
        return ModelRouter.MODEL_VERSION_MAP.get(model, model)

    @staticmethod
    def context_limit_for(model: str) -> int:
        """返回模型的上下文限制。

        Args:
            model: 模型名称

        Returns:
            上下文 token 限制，默认 128,000
        """
        return ModelRouter.MODEL_CONTEXT_LIMITS.get(model, 128_000)
