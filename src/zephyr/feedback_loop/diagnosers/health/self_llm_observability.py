# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.health.self_llm_observability
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
Self LLM Observability — v0.12.0 R160

Blindspot: FLE uses LLM but cannot observe LLM quality degradation.
Risk: R160 — Silent LLM quality drop corrupts all downstream diagnosis.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: self_llm_observability.py
# 层: 算法
# - id: A1
#   name_zh: ① SelfLLMObservability
#   name_en: SelfLLMObservability
#   intro: class SelfLLMObservability 源码 L55-L60
#   desc: 公共方法（定义序）: alert；源码 L55-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SelfLLMObservability
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class SelfLLMObservability:
    error_rate: float = 0.0
    latency_p95: float = 0.0

    def alert(self) -> bool:
        return self.error_rate > 0.05 or self.latency_p95 > 10000.0
