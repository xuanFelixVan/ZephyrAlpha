# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.llm_cost_accounting
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
LLM Cost Accounting — v0.4.0 R35

Blindspot: LLM API costs unaccounted; budget invisible.
Risk: R35 — Surprise bill from runaway LLM calls.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: llm_cost_accounting.py
# 层: 算法
# - id: A1
#   name_zh: ① LLMCostAccounting
#   name_en: LLMCostAccounting
#   intro: class LLMCostAccounting 源码 L55-L59
#   desc: 公共方法（定义序）: record；源码 L55-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: LLMCostAccounting
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class LLMCostAccounting:
    total_cost: float = 0.0

    def record(self, model: str, tokens: int) -> None:
        self.total_cost += tokens * 0.00001
