# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_model_strategy
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
context_model_strategy.py — 模型选择策略 (DD118, TASK-020)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: context_model_strategy.py
# 层: 算法
# - id: A1
#   name_zh: ① ContextModelStrategy
#   name_en: ContextModelStrategy
#   intro: task_type->model selection: simple task->small model, compl…
#   desc: task_type->model selection: simple task->small model, complex->large (DD118).；公共方法（定义序）: select；源码 L60-L72
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ContextModelStrategy
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ModelStrategy:
    task_type: str
    budget_level: str
    model: str
    fallback_model: str


class ContextModelStrategy:
    """task_type->model selection: simple task->small model, complex->large (DD118)."""

    _STRATEGIES: dict[str, ModelStrategy] = {
        "CODE_GEN": ModelStrategy("CODE_GEN", "L2", "Qwen2.5-3B-Instruct", "Qwen2.5-Coder-7B"),
        "CODE_REVIEW": ModelStrategy("CODE_REVIEW", "L2", "Qwen2.5-Coder-7B", "Claude-Sonnet-4"),
        "ANALYSIS": ModelStrategy("ANALYSIS", "L3", "Claude-Sonnet-4", "GPT-4o"),
    }

    def select(self, task_type: str) -> ModelStrategy:
        return self._STRATEGIES.get(
            task_type, ModelStrategy(task_type, "L2", "Qwen2.5-3B-Instruct", "Qwen2.5-Coder-7B")
        )
