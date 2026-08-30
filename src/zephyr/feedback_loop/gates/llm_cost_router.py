# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.llm_cost_router
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
LLM Cost Router — v0.3.0 R20

Blindspot: All LLM calls use costliest model regardless of task criticality.
Risk: R20 — FLE burns budget on low-value diagnostics.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: llm_cost_router.py
# 层: 算法
# - id: A1
#   name_zh: ① LLMCostRouter
#   name_en: LLMCostRouter
#   intro: class LLMCostRouter 源码 L55-L60
#   desc: 公共方法（定义序）: route；源码 L55-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: LLMCostRouter
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class LLMCostRouter:
    budget_monthly: float = 1000.0
    spent: float = 0.0

    def route(self, task_priority: int) -> str:
        return "cheap-model" if task_priority < 5 else "best-model"
