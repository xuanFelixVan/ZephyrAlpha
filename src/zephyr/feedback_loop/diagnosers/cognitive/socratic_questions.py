# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive.socratic_questions
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
Socratic Questions — v0.7.0 R81

Blindspot: FLE diagnosis lacks critical self-questioning.
Risk: R81 — Confirmation bias amplifies initial wrong diagnosis.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: socratic_questions.py
# 层: 算法
# - id: A1
#   name_zh: ① SocraticQuestions
#   name_en: SocraticQuestions
#   intro: class SocraticQuestions 源码 L55-L61
#   desc: 公共方法（定义序）: generate；源码 L55-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SocraticQuestions
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class SocraticQuestions:
    def generate(self, hypothesis: str) -> list[str]:
        return [
            f"Is {hypothesis} really the root cause?",
            f"What evidence contradicts {hypothesis}?",
            "If deep findings differ from initial diagnosis, why was the initial diagnosis wrong?",
        ]
