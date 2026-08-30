# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.prompt_sanitizer
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
Prompt Sanitizer — v0.10.0 R133

Blindspot: External data injected into prompts can carry injection attacks.
Risk: R133 — Prompt injection through diagnosis evidence compromises LLM output.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: prompt_sanitizer.py
# 层: 算法
# - id: A1
#   name_zh: ① PromptSanitizer
#   name_en: PromptSanitizer
#   intro: class PromptSanitizer 源码 L55-L57
#   desc: 公共方法（定义序）: sanitize；源码 L55-L57
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: PromptSanitizer
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class PromptSanitizer:
    def sanitize(self, text: str) -> str:
        return text.replace("ignore previous", "[FILTERED]")
