# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.prompt_fingerprint
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
Prompt Fingerprint — v0.3.0 R14

Blindspot: LLM prompts drift silently over time without version tracking.
Risk: R14 — Prompt drift causes diagnostic inconsistency across sessions.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: prompt_fingerprint.py
# 层: 算法
# - id: A1
#   name_zh: ① PromptFingerprint
#   name_en: PromptFingerprint
#   intro: class PromptFingerprint 源码 L56-L62
#   desc: 公共方法（定义序）: from_content；源码 L56-L62
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: PromptFingerprint
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import hashlib
from dataclasses import dataclass


@dataclass
class PromptFingerprint:
    prompt_id: str
    content_hash: str = ""

    @classmethod
    def from_content(cls, prompt_id: str, content: str) -> "PromptFingerprint":
        return cls(prompt_id=prompt_id, content_hash=hashlib.sha256(content.encode()).hexdigest())
