# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive.tone_adapter_v2
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
Tone Adapter v2 — v0.10.0 R141

Enhanced tone adaptation with multi-channel context awareness.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: tone_adapter_v2.py
# 层: 算法
# - id: A1
#   name_zh: ① ToneAdapterV2
#   name_en: ToneAdapterV2
#   intro: class ToneAdapterV2 源码 L54-L60
#   desc: 公共方法（定义序）: route；源码 L54-L60
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ToneAdapterV2
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class ToneAdapterV2:
    channels: list[str] = field(default_factory=lambda: ["email", "sms", "push"])

    def route(self, severity: int) -> list[str]:
        if severity > 8:
            return self.channels
        return self.channels[:1]
